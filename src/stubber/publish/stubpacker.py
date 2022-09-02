import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import tomli
import tomli_w
from loguru import logger as log
from packaging.version import Version, parse
from stubber.codemod.enrich import enrich_folder
from stubber.publish.package import StubSource
from stubber.utils.config import CONFIG
from stubber.utils.versions import clean_version

from .bump import bump_postrelease
from .enums import StubSource
from .merge_docstubs import copy_merge_docstubs

# TODO: Get git tag and store in DB for reference
# import stubber.basicgit as git
# git log -n 1 --format="%H"
# git log -n 1 --format="https://github.com/josverl/micropython-stubs/tree/%H"
# https://github.com/Josverl/micropython-stubs/tree/d45c8fa3dbdc01978af58532ff4c5313090aabfb

#  git -C .\all-stubs\ log -n 1 --format="https://github.com/josverl/micropython-stubs/tree/%H"


class StubPackage:
    """
    Create a stub-only package for a specific version of micropython

    properties:
        - toml_path - the path to the `pyproject.toml` file
        - package_path - the path to the folder where the package info will be stored ('./publish').
        - pkg_version - the version of the package as used on PyPi (semver). Is stored directly in the `pyproject.toml` file
        - pyproject - the contents of the `pyproject.toml` file
    methods:
        - from_json - load the package from json
        - to_json - return the package as json

        - create_update_pyproject_toml - create or update the `pyproject.toml` file
        - create_readme - create the readme file
        - create_license - create the license file
        - copy_stubs - copy the stubs to the package folder
        - update_included_stubs - update the included stubs in the `pyproject.toml` file
        - create_hash - create a hash of the package files

        - update_package_files - combines clean, copy, and create reeadme & updates
    """

    def __init__(
        self,
        package_name: str,
        version: str = "0.0.1",
        description: str = "MicroPython stubs",
        stubs: Optional[List[Tuple[str, Path]]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a stub-only package for a specific version of micropython
        parameters:

            - package_name - the name of the package as used on PyPi
            - version - the version of the package as used on PyPi (semver)
            - description
            - stubs - a list of tuples (name, path) of the stubs to copy
            - json_data - Optional:  a json databse record that will be used to create the package from.
              When `json_data` is provided, the version, description and stubs parameters are ignored

        paths:
            ROOT_PATH - the root path of the project ('./')
            PUBLISH_PATH - root-relative path to the folder where the package info will be stored ('./publish').
            TEMPLATE_PATH - root-relative path to the folder where the template files are stored ('./publish/template').
            STUB_PATH - root-relative path to the folder where the stubs are stored ('./stubs').

        """
        # package must be stored in its own folder, add package name if needed
        # if not publish_path.name == package_name:
        #     package_path = publish_path / package_name
        # else:
        #     package_path = publish_path
        # # create the package folder
        # package_path.mkdir(parents=True, exist_ok=True)
        if json_data is not None:

            self.from_dict(json_data)

        else:
            # store essentials
            # self.package_path = package_path
            self.package_name = package_name
            self.description = description
            self.mpy_version = clean_version(version, drop_v=True)  # Initial version
            self.hash = None  # intial hash
            """Hash of all the files in the package"""
            self.stub_hash = None  # intial hash
            """hash of the the stub files"""
            self.create_update_pyproject_toml()

            # save the stub sources
            if stubs:
                self.stub_sources = stubs
            else:
                self.stub_sources: List[Tuple[str, Path]] = []
            self._publish = True

    @property
    def package_path(self) -> Path:
        "package path based on the package name and version and relative to the publish folder"
        parts = self.package_name.split("-")
        parts[1:1] = [clean_version(self.mpy_version, flat=True)]
        return CONFIG.publish_path / "-".join(parts)

    @property
    def toml_path(self) -> Path:
        "the path to the `pyproject.toml` file"
        # todo: make sure this is always relative to the root path
        return self.package_path / "pyproject.toml"

    # -----------------------------------------------
    @property
    def pkg_version(self) -> str:
        "return the version of the package"
        # read the version from the toml file
        _toml = self.toml_path
        if not _toml.exists():
            return self.mpy_version
        with open(_toml, "rb") as f:
            pyproject = tomli.load(f)
        return str(parse(pyproject["tool"]["poetry"]["version"]))

    @pkg_version.setter
    def pkg_version(self, version):
        "set the version of the package"
        # read the current file
        _toml = self.toml_path
        with open(_toml, "rb") as f:
            pyproject = tomli.load(f)
        pyproject["tool"]["poetry"]["version"] = version

        # update the version in the toml file
        with open(_toml, "wb") as output:
            tomli_w.dump(pyproject, output)

    # -----------------------------------------------
    @property
    def pyproject(self) -> Union[Dict[str, Any], None]:
        "parsed pyproject.toml or None"
        pyproject = None
        _toml = self.toml_path
        if (_toml).exists():
            with open(_toml, "rb") as f:
                pyproject = tomli.load(f)
        return pyproject

    @pyproject.setter
    def pyproject(self, pyproject):
        # check if the result is a valid toml file

        try:
            tomli.loads(tomli_w.dumps(pyproject))
        except tomli.TOMLDecodeError as e:
            print("Could not create a valid TOML file")
            raise (e)
        # make sure parent folder exists
        _toml = self.toml_path
        (_toml).parent.mkdir(parents=True, exist_ok=True)
        with open(_toml, "wb") as output:
            tomli_w.dump(pyproject, output)

    # -----------------------------------------------

    def to_dict(self):
        """return the package as a dict to store in the jsondb

        need to simplify some of the Objects to allow serialisation to json
        - the paths to posix paths
        - the version (semver) to a string
        - toml file to list of lines

        """
        return {
            "name": self.package_name,
            "mpy_version": self.mpy_version,
            "publish": self._publish,
            "pkg_version": str(self.pkg_version),
            "path": self.package_path.name,  # only store the folder name , as it is relative to the publish folder
            "stub_sources": [(name, Path(path).as_posix()) for (name, path) in self.stub_sources],
            "description": self.description,
            "hash": self.hash,
            "stub_hash": self.stub_hash,
        }

    def from_dict(self, json_data):
        """load the package from a dict (from the jsondb)"""
        self.package_name = json_data["name"]
        # self.package_path = Path(json_data["path"])
        self.description = json_data["description"]
        self.mpy_version = json_data["mpy_version"]
        self._publish = json_data["publish"]
        self.hash = json_data["hash"]
        self.stub_hash = json_data["stub_hash"]
        # create folder
        if not self.package_path.exists():
            self.package_path.mkdir(parents=True, exist_ok=True)
        #  create the pyproject.toml file
        self.create_update_pyproject_toml()
        # set pkg version after creating the toml file
        self.pkg_version = json_data["pkg_version"]
        self.stub_sources = []
        for (name, path) in json_data["stub_sources"]:
            if path.startswith("stubs/"):
                path = path.replace("stubs/", "")
            self.stub_sources.append((name, Path(path)))

    def update_package_files(
        self,
    ):
        """
        Update the stub-only package for a specific version of micropython
         - cleans the package folder
         - copies the stubs from the list of stubs.
         - creates/updates the readme and the license file


        """
        # create the package folder
        self.package_path.mkdir(parents=True, exist_ok=True)

        self.clean()  # Delete any previous *.py? files
        self.copy_stubs()
        self.create_readme()
        self.create_license()

    def copy_stubs(self):
        """
        Copy files from all listed stub folders to the package folder
        the order of the stub folders is relevant as "last copy wins"

         - 1 - Copy all firmware stubs/merged to the package folder
         - 2 - copy the remaining stubs to the package folder

        """

        # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
        for stub_type, fw_path in [s for s in self.stub_sources]:
            if stub_type == StubSource.FIRMWARE:
                # Check if -merged folder exists and copy that instead
                merged_path = fw_path.with_name(f"{fw_path.name}-merged")
                source = fw_path
                if merged_path.exists():
                    source = merged_path
                try:
                    log.debug(f"Copying {stub_type} from {source}")
                    shutil.copytree(CONFIG.stub_path / source, self.package_path, symlinks=True, dirs_exist_ok=True)
                except OSError as e:
                    log.error(f"Error copying stubs from : {CONFIG.stub_path / source}, {e}")
                    raise (e)
            else:
                try:
                    log.debug(f"Copying {stub_type} from {fw_path}")
                    shutil.copytree(CONFIG.stub_path / fw_path, self.package_path, symlinks=True, dirs_exist_ok=True)
                except OSError as e:
                    log.error(f"Error copying stubs from : {CONFIG.stub_path / fw_path}, {e}")
                    raise (e)

    def create_readme(self):
        """
        Create a readme file for the package
         - based on the template readme file
         - with a list of all included stub folders added to it (not the individual stub-files)
        """
        # read the readme file and update the version and description
        with open(CONFIG.template_path / "README.md", "r") as f:
            TEMPLATE_README = f.read()

        # add a readme with the names of the stub-folders

        # Prettify this by merging with template text
        with open(self.package_path / "README.md", "w") as f:
            f.write(f"# {self.package_name}\n\n")
            f.write(TEMPLATE_README)
            f.write(f"Included stubs:\n")
            for name, folder in self.stub_sources:
                f.write(f"* {name} from {Path(folder).as_posix()}\n")

    def create_license(self):
        """
        Create a license file for the package
         - copied from the template license file
        """
        # copy the license file from the template to the package folder
        # option : append other license files
        shutil.copy(CONFIG.template_path / "LICENSE.md", self.package_path)

    def create_update_pyproject_toml(
        self,
    ):
        """
        create or update/overwrite a `pyproject.toml` file by combining a template file
        with the given parameters.
        and updating it with the pyi files included
        """
        # Do not overwrite existing pyproject.toml but read and apply changes to it
        # 1) read from disk , if exists
        # 2) create from template, in all other cases
        on_disk = (self.toml_path).exists()
        if on_disk:
            # do not overwrite the version of a pre-existing file
            _pyproject = self.pyproject
            assert _pyproject is not None
            # clear out the packages section
            _pyproject["tool"]["poetry"]["packages"] = []

        else:
            # read the template pyproject.toml file from the template folder
            try:
                with open(CONFIG.template_path / "pyproject.toml", "rb") as f:
                    _pyproject = tomli.load(f)
                _pyproject["tool"]["poetry"]["version"] = self.mpy_version
            except FileNotFoundError as e:
                log.error(f"Could not find template pyproject.toml file {e}")
                raise (e)
        # # check if version number of the package matches the version number of the stubs
        # ver_pkg = parse(_pyproject["tool"]["poetry"]["version"])
        # ver_stubs = parse(self.mpy_version)
        # if isinstance(ver_stubs, LegacyVersion) or isinstance(ver_pkg, LegacyVersion):
        #     raise ValueError(f"Legacy version not supported: {ver_pkg} || {ver_stubs}")

        # if not (ver_pkg.major == ver_stubs.major and ver_pkg.minor == ver_stubs.minor):

        #     log.warning(f"Package version:{ver_pkg.public} does not match the version of the stubs: {ver_stubs.public}")
        #     _pyproject["tool"]["poetry"]["version"] = self.mpy_version

        # update the name , version and description of the package
        _pyproject["tool"]["poetry"]["name"] = self.package_name
        _pyproject["tool"]["poetry"]["description"] = self.description
        # write out the pyproject.toml file
        self.pyproject = _pyproject

    def update_included_stubs(self):
        "Add the stub files to the pyproject.toml file"
        _pyproject = self.pyproject
        assert _pyproject is not None, "No pyproject.toml file found"
        _pyproject["tool"]["poetry"]["packages"] = []
        # find packages using __init__ files
        # take care no to include a module twice
        modules = set({})
        for p in (self.package_path).rglob("**/__init__.py*"):
            # add the module to the package
            # fixme : only accounts for one level of packages
            modules.add(p.parent.name)
        for module in sorted(modules):
            _pyproject["tool"]["poetry"]["packages"] += [{"include": module}]
        # now find other stub files directly in the folder
        for p in sorted((self.package_path).glob("*.py*")):
            if p.suffix in (".py", ".pyi"):
                _pyproject["tool"]["poetry"]["packages"] += [{"include": p.name}]

        # write out the pyproject.toml file
        self.pyproject = _pyproject

        # OK

    def clean(self):
        """
        Remove the stub files from the package folder

        This is used before update the stub package, to avoid lingering stub files,
        and after the package has been built, to avoid needing to store files multiple times.

        `.gitignore` cannot be used as this will prevent poetry from processing the files.

        """
        # remove all *.py and *.pyi files in the folder
        for wc in ["*.py", "*.pyi", "modules.json"]:
            for f in (self.package_path).rglob(wc):
                f.unlink()

    def create_hash(self, include_md=True) -> str:
        """
        Create a SHA1 hash of all files in the package, excluding the pyproject.toml file itself.
        the hash is based on the content of the .py/.pyi and .md files in the package.
        if include_md is False , the .md files are not hased, allowing the files in the packeges to be compared simply
        As a single has is created across all files, the files are sorted prior to hashing to ensure that the hash is stable.

        A changed hash will not indicate which of the files in the package have been changed.
        """
        # BUF_SIZE is totally arbitrary,
        BUF_SIZE = 65536 * 16  # lets read stuff in 16 x 64kb chunks!

        hash = hashlib.sha1()
        files = list((self.package_path).rglob("**/*.py")) + list((self.package_path).rglob("**/*.pyi"))
        if include_md:
            files += (
                [self.package_path / "LICENSE.md"]
                + [self.package_path / "README.md"]
                # do not include [self.toml_file]
            )

        for file in sorted(files):
            with open(file, "rb") as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    hash.update(data)

        return hash.hexdigest()

    def update_hashes(self):
        "Update the pachage hashes"
        self.hash = self.create_hash()
        self.stub_hash = self.create_hash(include_md=False)

    def is_changed(self) -> bool:
        "Check if the package has changed, based on the current and the stored hash"
        current = self.create_hash()
        log.debug(f"changed: {self.hash != current} : Stored {self.hash} Current: {current}")
        return self.hash != current

    def bump(self):
        """
        bump the postrelease version of the package, and write the change to disk
        """
        try:
            pyproject = self.pyproject
            assert pyproject is not None, "No pyproject.toml file found"
            current = parse(pyproject["tool"]["poetry"]["version"])
            assert isinstance(current, Version)
            # bump the version
            new_version = bump_postrelease(current)
            pyproject["tool"]["poetry"]["version"] = str(new_version)
            self.pyproject = pyproject
        except Exception as e:  # pragma: no cover
            log.error(f"Error: {e}")
            return None
        return new_version

    def run_poetry(self, parameters: List[str]) -> bool:
        """Run a poetry commandline in the package folder.
        Note: this may write some output to the console ('All set!')
        """
        # check for pyproject.toml in folder
        if not (self.package_path / "pyproject.toml").exists():  # pragma: no cover
            log.error(f"No pyproject.toml file found in {self.package_path}")
            return False
        # todo: call poetry directly to improve error handling
        try:
            subprocess.run(
                ["poetry"] + parameters,
                cwd=self.package_path,
                check=True,
                # stdout=subprocess.PIPE,
                stdout=subprocess.PIPE,  # interestingly: errors on stdout , output on stderr .....
                universal_newlines=True,
            )
        except (NotADirectoryError, FileNotFoundError) as e:  # pragma: no cover
            log.error("Exception on process, {}".format(e))
            return False
        except subprocess.CalledProcessError as e:  # pragma: no cover
            # Detect and log  error detection om upload
            #   UploadError
            #   HTTP Error 400: File already exists. See https://test.pypi.org/help/#file-name-reuse for more information.
            # TODO: how to return the state so it can be handled
            errors = [l for l in e.stdout.splitlines()[1:7] if "Error" in l]
            for e in errors:
                log.error(e)

            # log.error("Exception on process, {}".format(e))
            return False
        return True

    def write_package_json(self):
        # write the json to a file
        with open(self.package_path / "package.json", "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def check(self) -> bool:
        """check if the package is valid by running `poetry check`
        Note: this will write some output to the console ('All set!')
        """
        return self.run_poetry(["check", "-vvv"])

    def build(self) -> bool:
        """build the package by running `poetry build`"""
        return self.run_poetry(["build"])  # ,"-vvv"

    def publish(self, production=False) -> bool:
        if not self._publish:
            log.warning(f"Publishing is disabled for {self.package_name}")
            return False
        # update the package info
        self.write_package_json()
        if production:
            log.info(f"Publishing to PRODUCTION  https://pypy.org")
            params = ["publish"]
        else:
            log.info(f"Publishing to TEST-PyPi https://test.pypy.org")
            params = ["publish", "-r", "test-pypi"]
        return self.run_poetry(params)
