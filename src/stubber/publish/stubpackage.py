"""Create a stub-only package for a specific version of micropython"""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import tenacity

from mpflash.basicgit import get_git_describe
from stubber.publish.helpers import get_module_docstring

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore
else:
    import tomli as tomllib  # type: ignore

from typing import NewType

import tomli_w
from mpflash.logger import log
from packaging.version import Version, parse
from pysondb import PysonDB

from mpflash.versions import SET_PREVIEW, V_PREVIEW, clean_version
from stubber.publish.bump import bump_version
from stubber.publish.defaults import GENERIC_U, default_board
from stubber.publish.enums import StubSource
from stubber.publish.pypi import Version, get_pypi_versions
from stubber.utils.config import CONFIG

Status = NewType("Status", Dict[str, Union[str, None]])
StubSources = List[Tuple[StubSource, Path]]

# indicates which stubs will be skipped when copying for these stub sources
STUBS_COPY_FILTER = {
    StubSource.FROZEN: [
        "espnow",  # merged stubs + documentation of the espnow module is better than the info in the forzen stubs
    ],
    StubSource.FIRMWARE: [
        "builtins",
        "collections",  # collections must be in stdlib
    ],
    StubSource.MERGED: [
        "collections",  # collections must be in stdlib
    ],
}

# these modules will be replaced by a simple import statement to import from stdlib
STDLIB_UMODULES = ["ucollections"]


class VersionedPackage(object):
    """
    Represents a versioned package.

    Attributes:
        package_name (str): The name of the package.
        mpy_version (str): The MicroPython version.

    Methods:
        __init__(self, package_name: str, mpy_version: str): Initializes a new instance of the VersionedPackage class.
        is_preview(self): Checks if the package is a preview version.
        pkg_version(self) -> str: Returns the version of the package.
        pkg_version(self, version: str) -> None: Sets the version of the package.
        get_prerelease_package_version(self, production: bool = False) -> str: Gets the next prerelease version for the package.
        get_next_package_version(self, prod: bool = False, rc=False) -> str: Gets the next version for the package.
        next_pkg_version(self, production: bool) -> str: Gets the next version for the package.
        bump(self, *, rc: int = 0) -> str: Bumps the postrelease version of the package.
    """

    def __init__(self, package_name: str, *, mpy_version: str):
        super().__init__()
        self.package_name: str = package_name
        self.mpy_version: str = mpy_version
        self._pkg_version: str = mpy_version

    def __str__(self) -> str:
        return f"{self.package_name}=={self.mpy_version}"

    def __repr__(self) -> str:
        return f"{self.package_name}=={self.mpy_version}"

    def __eq__(self, o: object) -> bool:
        return str(self) == str(o)

    def __hash__(self) -> int:
        return hash(str(self))

    @property
    def pkg_version(self) -> str:
        "return the version of the package"
        return self._pkg_version

    @pkg_version.setter
    def pkg_version(self, version: str) -> None:
        "set the version of the package"
        self._pkg_version = version

    def next_package_version(self, production: bool) -> str:
        # sourcery skip: assign-if-exp
        """Get the next version for the package"""
        if self.is_preview():
            return self._get_next_preview_package_version(production)
        else:
            return self._get_next_package_version(production)

    def is_preview(self):
        return self.mpy_version in SET_PREVIEW or V_PREVIEW in self.mpy_version

    def _get_next_preview_package_version(self, production: bool = False) -> str:
        """
        Get the next prerelease version for the package.
        this is used for preview versions of micropython (-preview, formerly known as 'latest')
        """
        rc = 1
        if not (describe := get_git_describe(CONFIG.mpy_path.as_posix())):
            return "99.99.99post99"
        # use versiontag and the number of commits since the last tag
        # "v1.19.1-841-g3446"
        # 'v1.20.0-dirty'
        # 'v1.22.0-preview-19-g8eb7721b4'
        parts = describe.split("-", 3)
        ver = parts[0]
        if len(parts) > 1:
            rc = (
                parts[1]
                if parts[1].isdigit()
                else parts[2] if len(parts) > 2 and parts[2].isdigit() else 1
            )
        rc = int(rc)
        base = (
            bump_version(Version(ver), minor_bump=True) if parts[1] != V_PREVIEW else Version(ver)
        )
        return str(bump_version(base, rc=rc))
        # raise ValueError("cannot determine next version number micropython")

    def _get_next_package_version(self, prod: bool = False, rc=False) -> str:
        """Get the next version for the package."""
        base = Version(self.pkg_version)
        if pypi_versions := get_pypi_versions(self.package_name, production=prod, base=base):
            # get the latest version from pypi
            self.pkg_version = str(pypi_versions[-1])
        else:
            # no published package found , so we start at base version then bump 1 post release
            self.pkg_version = Version(self.pkg_version).base_version
        return self.bump()

    def bump(self, *, rc: int = 0) -> str:
        """
        bump the postrelease version of the package, and write the change to disk
        if rc >= 1, the version is bumped to the specified release candidate
        """
        try:
            current = Version(self.pkg_version)
            assert isinstance(current, Version)
            # bump the version
            self.pkg_version = str(bump_version(post_bump=True, current=current, rc=rc))
        except Exception as e:  # pragma: no cover
            log.error(f"Error: {e}")
        return self.pkg_version


class Builder(VersionedPackage):
    """
    Builder class for creating and updating MicroPython stub packages.

    Args:
        package_name (str): The name of the package.
        mpy_version (str, optional): The version of MicroPython. Defaults to "0.0.1".
        port (str): The port for the package.
        board (str, optional): The board for the package. Defaults to GENERIC_U.
        description (str, optional): The description of the package. Defaults to "MicroPython stubs".
        stubs (Optional[StubSources], optional): The stub sources for the package. Defaults to None.

    Attributes:
        package_name (str): The name of the package.
        mpy_version (str): The version of MicroPython.
        port (str): The port for the package.
        board (str): The board for the package.
        description (str): The description of the package.
        stub_sources (Optional[StubSources]): The stub sources for the package.
        hash (None): The hash of all the files in the package.
        stub_hash (None): The hash of the stub files.

    Properties:
        package_path (Path): The package path based on the package name and version, relative to the publish folder.
        toml_path (Path): The path to the `pyproject.toml` file.
        pyproject (Union[Dict[str, Any], None]): The parsed pyproject.toml or None.

    Methods:
        create_update_pyproject_toml(): Create or update/overwrite a `pyproject.toml` file.
        check(): Check if the package is valid.
        clean(): Remove the stub files from the package folder.
        copy_stubs(): Copy files from all listed stub folders to the package folder.
        update_package_files(): Update the stub-only package for a specific version of MicroPython.
        write_package_json(): Write the package.json file to disk.
        to_dict(): Return the package as a dict to store in the jsondb.
        from_dict(json_data: Dict): Load the package from a dict (from the jsondb).
        calculate_hash(include_md: bool = True): Create a SHA1 hash of all files in the package.
        update_hashes(): Update the package hashes.
        is_changed(include_md: bool = True): Check if the package has changed.
    """

    # BUF_SIZE is totally arbitrary,
    BUF_SIZE = 65536 * 16  # lets read stuff in 16 x 64kb chunks!

    def __init__(
        self,
        package_name: str,
        *,
        mpy_version: str = "0.0.1",
        port: str,
        board: str = GENERIC_U,
        description: str = "MicroPython stubs",
        stubs: Optional[StubSources] = None,
        # json_data: Optional[Dict[str, Any]] = None,
    ):  #  port: str, board: str
        super().__init__(package_name=package_name, mpy_version=mpy_version)
        self._publish = True  # intended for publishing
        self.package_name = package_name
        self.mpy_version = mpy_version
        self.port = port
        self.board = board
        self.description = description
        self.stub_sources = stubs or []
        self.hash = None  # intial hash
        """Hash of all the files in the package"""
        self.stub_hash = None  # intial hash
        """Hash of all .pyi files"""

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
    def pyproject(self) -> Union[Dict[str, Any], None]:
        "parsed pyproject.toml or None"
        pyproject = None
        _toml = self.toml_path
        if (_toml).exists():
            log.info(f"Load pyproject from {_toml}")
            try:
                with open(_toml, "rb") as f:
                    pyproject = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                log.error(f"Could not load pyproject.toml file {e}")
        return pyproject

    @pyproject.setter
    def pyproject(self, pyproject: Dict) -> None:
        # check if the result is a valid toml file
        try:
            tomllib.loads(tomli_w.dumps(pyproject))
        except tomllib.TOMLDecodeError as e:
            print("Could not create a valid TOML file")
            raise (e)
        # make sure parent folder exists
        _toml = self.toml_path
        (_toml).parent.mkdir(parents=True, exist_ok=True)
        with open(_toml, "wb") as output:
            tomli_w.dump(pyproject, output)

    # -----------------------------------------------
    def create_update_pyproject_toml(self) -> None:
        """
        create or update/overwrite a `pyproject.toml` file by combining a template file
        with the given parameters.
        """
        raise NotImplementedError("create_update_pyproject_toml not implemented")

    # -----------------------------------------------

    def check(self) -> bool:
        """Check if the package is valid, to be implemented by the subclass"""
        return True

    def clean(self) -> None:
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

    def copy_stubs(self) -> None:
        """
        Copy files from all listed stub folders to the package folder
        the order of the stub folders is relevant as "last copy wins"

         - 1 - Copy all MCU stubs/merged to the package folder
         - 2 - copy the remaining stubs to the package folder
         - 3 - remove *.py files from the package folder
        """
        try:
            # Check if all stub source folders exist
            for stub_type, src_path in self.stub_sources:
                if not (CONFIG.stub_path / src_path).exists():
                    raise FileNotFoundError(
                        f"Could not find stub source folder {CONFIG.stub_path / src_path}"
                    )

            # 1 - Copy  the stubs to the package, directly in the package folder (no folders)
            # for stub_type, fw_path in [s for s in self.stub_sources]:
            for n in range(len(self.stub_sources)):
                stub_type, src_path = self.stub_sources[n]
                try:
                    log.debug(f"Copying {stub_type} from {src_path}")
                    self.copy_folder(stub_type, src_path)
                except OSError as e:
                    if stub_type != StubSource.FROZEN:
                        raise FileNotFoundError(
                            f"Could not find stub source folder {src_path}"
                        ) from e
                    else:
                        log.debug(f"Error copying stubs from : {CONFIG.stub_path / src_path}, {e}")
        finally:
            # 3 - clean up a little bit
            # delete all the .py files in the package folder if there is a corresponding .pyi file
            for f in self.package_path.rglob("*.py"):
                if f.with_suffix(".pyi").exists():
                    f.unlink()
            self.update_umodules()

    def update_umodules(self):
        """
        Replace the STDLIB umodules with a simple import statement
        in order to allow the typecheckers to resove the stdlib modules in the usual stdlib location.
        """
        for f in self.package_path.rglob("*.pyi"):
            if f.stem in STDLIB_UMODULES:
                # read the docstring of the module
                docstring = get_module_docstring(f) or ""
                comment = "# import module from stdlib/module"
                # replace the file with a simple import statement
                f.write_text(f'"""\n{docstring}\n"""\n{comment}\nfrom {f.stem[1:]} import *')

    def copy_folder(self, stub_type: StubSource, src_path: Path):
        Path(self.package_path).mkdir(parents=True, exist_ok=True)
        for item in (CONFIG.stub_path / src_path).rglob("*"):
            if item.is_file():
                # filter the 'poorly' decorated files
                if stub_type in STUBS_COPY_FILTER and item.stem in STUBS_COPY_FILTER[stub_type]:
                    continue

                target = Path(self.package_path) / item.relative_to(CONFIG.stub_path / src_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(item.read_bytes())

    def update_package_files(self) -> None:
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

    def write_package_json(self) -> None:
        """write the package.json file to disk"""
        # make sure folder exists
        if not self.package_path.exists():
            self.package_path.mkdir(parents=True, exist_ok=True)
        # write the json to a file
        with open(self.package_path / "package.json", "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_dict(self) -> dict:
        """return the package as a dict to store in the jsondb

        need to simplify some of the Objects to allow serialization to json
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

    def from_dict(self, json_data: Dict) -> None:
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
        for name, path in json_data["stub_sources"]:
            if path.startswith("stubs/"):
                path = path.replace("stubs/", "")
            self.stub_sources.append((name, Path(path)))

    def calculate_hash(self, include_md: bool = True) -> str:
        # sourcery skip: reintroduce-else, swap-if-else-branches, use-named-expression
        """
        Create a SHA1 hash of all files in the package, excluding the pyproject.toml file itself.
        the hash is based on the content of the .py/.pyi and .md files in the package.
        if include_md is False , the .md files are not hased, allowing the files in the packeges to be compared simply
        As a single hash is created across all files, the files are sorted prior to hashing to ensure that the hash is stable.

        Note: A changed hash will not indicate which of the files in the package have been changed.
        """
        file_hash = hashlib.sha1()
        # Stubs Only
        files = list((self.package_path).rglob("**/*.pyi"))
        if include_md:
            files += (
                [self.package_path / "LICENSE.md"]
                + [self.package_path / "README.md"]
                # do not include [self.toml_file]
            )
        for file in sorted(files):
            try:
                # retry on file not found
                self.add_file_hash(file, file_hash)
            except FileNotFoundError:
                log.warning(f"File not found {file}")
                # ignore file not found errors to allow the hash to be created WHILE GIT / VIRUS SCANNERS HOLD LINGERING FILES
        return file_hash.hexdigest()

    @tenacity.retry(wait=tenacity.wait_fixed(0.2), stop=tenacity.stop_after_attempt(3))
    def add_file_hash(self, file, file_hash):
        """
        Adds the hash of a file to the given file hash object.
        If an error occurs, the file is retried up to 3 times with a 0.2 second delay

        Args:
            file (str): The path to the file.
            file_hash (hashlib._Hash): The file hash object to update.

        Returns:
            None
        """
        with open(file, "rb") as f:
            while True:
                if data := f.read(Builder.BUF_SIZE):
                    file_hash.update(data)
                else:
                    break

    def update_hashes(self, ret=False) -> None:
        """Update the package hashes. Resets is_changed() to False"""
        self.hash = self.calculate_hash()
        self.stub_hash = self.calculate_hash(include_md=False)

    def is_changed(self, include_md: bool = True) -> bool:
        """Check if the package has changed, based on the current and the stored hash.
        The default checks the hash of all files, including the .md files.
        """
        current = self.calculate_hash(include_md=include_md)
        stored = self.hash if include_md else self.stub_hash
        log.trace(f"changed = {self.hash != current} | Stored: {stored} | Current: {current}")
        return stored != current

    def create_license(self) -> None:
        """
        Create a license file for the package
         - copied from the template license file
        """
        # copy the license file from the template to the package folder
        # option : append other license files
        shutil.copy(CONFIG.template_path / "LICENSE.md", self.package_path)

    def create_readme(self) -> None:
        """
        Create a readme file for the package
         - based on the template readme file
         - with a list of all included stub folders added to it (not the individual stub-files)
        """
        # read the readme file and update the version and description
        with open(CONFIG.template_path / "README.md", "r") as f:
            TEMPLATE_README = f.read()

        # add a readme with the names of the stub-folders

        # read informations from firmware_stubs.json
        firmware_stubs = {}
        doc_stubs = {}
        core_stubs = {}
        try:
            with open(self.package_path / "firmware_stubs.json", "r") as f:
                firmware_stubs = json.load(f)
            with open(self.package_path / "doc_stubs.json", "r") as f:
                doc_stubs = json.load(f)
            with open(self.package_path / "modules.json", "r") as f:
                core_stubs = json.load(f)
        except FileNotFoundError:
            pass

        # Prettify this by merging with template text
        with open(self.package_path / "README.md", "w") as f:
            f.write(f"# {self.package_name}\n\n")
            f.write(TEMPLATE_README)
            f.write(f"Included stubs:\n")
            for name, folder in self.stub_sources:
                f.write(f"* {name} from `stubs/{Path(folder).as_posix()}`\n")

            f.write(f"\n\n")
            f.write(f"origin | Family | Port | Board | Version\n")
            f.write(f"-------|--------|------|-------|--------\n")
            try:
                f.write(
                    f"Firmware | {firmware_stubs['firmware']['family']} | {firmware_stubs['firmware']['port']} | {firmware_stubs['firmware']['machine']} | {clean_version(firmware_stubs['firmware']['version'])} \n"
                )
            except Exception:
                pass
            try:
                f.write(
                    f"Documentation | {doc_stubs['firmware']['family']} | {doc_stubs['firmware']['port']} | - | {clean_version(doc_stubs['firmware']['version'])} \n"
                )
            except Exception:
                pass
            try:
                f.write(
                    f"Core | {core_stubs['firmware']['family']} | {core_stubs['firmware']['port']} | - | {clean_version(core_stubs['firmware']['version'])} \n"
                )
            except Exception:
                pass


class PoetryBuilder(Builder):
    """
    Build a package using Poetry
    """

    def __init__(
        self,
        package_name: str,
        *,
        port: str,
        mpy_version: str = "0.0.1",
        board: str = GENERIC_U,
        description: str = "MicroPython stubs",
        stubs: Optional[StubSources] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            package_name=package_name,
            mpy_version=mpy_version,
            port=port,
            board=board,
            description=description,
            stubs=stubs,
        )

    # -----------------------------------------------
    # get and set the version of the package directly from the toml file
    @property
    def pkg_version(self) -> str:
        "return the version of the package"
        # read the version from the toml file
        _toml = self.toml_path
        if not _toml.exists():
            return self.mpy_version
        with open(_toml, "rb") as f:
            pyproject = tomllib.load(f)
        ver = pyproject["tool"]["poetry"]["version"]
        return str(parse(ver)) if ver not in SET_PREVIEW else ver

    @pkg_version.setter
    def pkg_version(self, version: str) -> None:
        # sourcery skip: remove-unnecessary-cast
        "set the version of the package"
        if not isinstance(version, str):  # type: ignore
            version = str(version)
        # read the current file
        _toml = self.toml_path
        try:
            with open(_toml, "rb") as f:
                pyproject = tomllib.load(f)
            pyproject["tool"]["poetry"]["version"] = version
            # update the version in the toml file
            with open(_toml, "wb") as output:
                tomli_w.dump(pyproject, output)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"pyproject.toml file not found at {_toml}") from e

    # -----------------------------------------------

    def poetry_build(self) -> bool:
        """build the package by running `poetry build`"""
        return self.run_poetry(["build", "-vvv"])

    def poetry_publish(self, production: bool = False) -> bool:
        if not self._publish:
            log.warning(f"Publishing is disabled for {self.package_name}")
            return False
        # update the package info
        self.write_package_json()
        if production:
            log.debug("Publishing to PRODUCTION https://pypy.org")
            params = ["publish"]
        else:
            log.debug("Publishing to TEST-PyPi https://test.pypy.org")
            params = ["publish", "-r", "test-pypi"]
        r = self.run_poetry(params)
        print("")  # add a newline after the output
        return r

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
            log.debug(f"poetry {parameters} starting")
            subprocess.run(
                ["poetry"] + parameters,
                cwd=self.package_path,
                check=True,
                # stdout=subprocess.PIPE,
                stdout=subprocess.PIPE,  # interestingly: errors on stdout , output on stderr .....
                universal_newlines=True,
                encoding="utf-8",
            )
            log.trace(f"poetry {parameters} completed")
        except (NotADirectoryError, FileNotFoundError) as e:  # pragma: no cover # InvalidVersion
            log.error("Exception on process, {}".format(e))
            return False
        except subprocess.CalledProcessError as e:  # pragma: no cover
            # Detect and log  error detection om upload
            #   UploadError
            #   HTTP Error 400: File already exists. See https://test.pypi.org/help/#file-name-reuse for more information.
            # TODO: how to return the state so it can be handled
            print()  # linefeed after output
            errors = [l for l in e.stdout.splitlines()[1:7] if "Error" in l]
            for e in errors:
                log.error(e)

            # log.error("Exception on process, {}".format(e))
            return False
        return True

    def check(self) -> bool:
        """check if the package is valid by running `poetry check`
        Note: this will write some output to the console ('All set!')
        """
        return self.run_poetry(["check", "-vvv"])

    def create_update_pyproject_toml(self) -> None:
        """
        create or update/overwrite a `pyproject.toml` file by combining a template file
        with the given parameters.
        and updating it with the pyi files included
        """
        if (self.toml_path).exists():
            # do not overwrite the version of a pre-existing file
            _pyproject = self.pyproject
            assert _pyproject is not None
            # clear out the packages section
            _pyproject["tool"]["poetry"]["packages"] = []
            # update the dependencies section by reading these from the template file
            with open(CONFIG.template_path / "pyproject.toml", "rb") as f:
                tpl = tomllib.load(f)
            _pyproject["tool"]["poetry"]["dependencies"] = tpl["tool"]["poetry"]["dependencies"]

        else:
            # read the template pyproject.toml file from the template folder
            try:
                with open(CONFIG.template_path / "pyproject.toml", "rb") as f:
                    _pyproject = tomllib.load(f)
                # note: can be 'latest' which is not semver
                _pyproject["tool"]["poetry"]["version"] = self.mpy_version
            except FileNotFoundError as e:
                log.error(f"Could not find template pyproject.toml file {e}")
                raise (e)

        # update the name , version and description of the package
        _pyproject["tool"]["poetry"]["name"] = self.package_name
        _pyproject["tool"]["poetry"]["description"] = self.description
        # write out the pyproject.toml file
        self.pyproject = _pyproject

    def update_pyproject_stubs(self) -> int:
        "Add the stub files to the pyproject.toml file"
        _pyproject = self.pyproject
        assert _pyproject is not None, "No pyproject.toml file found"
        _pyproject["tool"]["poetry"]["packages"] = [
            {"include": p.relative_to(self.package_path).as_posix()}
            for p in sorted((self.package_path).rglob("*.pyi"))
        ]
        # write out the pyproject.toml file
        self.pyproject = _pyproject
        return len(_pyproject["tool"]["poetry"]["packages"])


class StubPackage(PoetryBuilder):
    """
    Create a stub-only package for a specific version , port and board of micropython

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
        port: str,
        *,
        board: str = GENERIC_U,
        version: str = "0.0.1",
        description: str = "MicroPython stubs",
        stubs: Optional[StubSources] = None,
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
        self.port = port
        self.board = board
        if json_data is not None:
            self.from_dict(json_data)
        else:
            # store essentials
            self.package_name = package_name
            self.description = description
            self.mpy_version = clean_version(version, drop_v=True)  # Initial version

            self.create_update_pyproject_toml()

            self.stub_sources: StubSources = []
            # save the stub sources
            if stubs:
                self.stub_sources = stubs

        self.status: Status = Status(
            {
                "result": "-",
                "name": self.package_name,
                "version": self.pkg_version,
                "error": None,
                "path": self.package_path.as_posix(),
            }
        )
        super().__init__(
            package_name=package_name,
            mpy_version=self.mpy_version,
            port=port,
            board=board,
            description=description,
            stubs=self.stub_sources,
        )

    def update_sources(self) -> StubSources:
        """
        Update the stub sources to:
        - FIRMWARE: prefer -merged stubs over bare MCU stubs
        - FROZEN: fallback to use the GENERIC folder for the frozen sources if no board specific folder exists
        """
        updated_sources = []
        # TODO: find a way to simplify this code as this is a bit magic (and hard to understand)
        for stub_type, fw_path in self.stub_sources:
            # prefer -merged stubs over bare MCU stubs
            if stub_type == StubSource.FIRMWARE:
                # Check if -merged folder exists and use that instead
                if fw_path.name.endswith("-merged"):
                    merged_path = fw_path
                else:
                    merged_path = fw_path.with_name(f"{fw_path.name}-merged")
                if (CONFIG.stub_path / merged_path).exists():
                    updated_sources.append((stub_type, merged_path))
                else:
                    updated_sources.append((stub_type, fw_path))
            elif stub_type == StubSource.FROZEN:
                # use if folder exists , else use GENERIC folder
                if (CONFIG.stub_path / fw_path).exists():
                    updated_sources.append((stub_type, fw_path))
                elif fw_path.with_name("GENERIC").exists():
                    updated_sources.append((stub_type, fw_path.with_name("GENERIC")))
            elif stub_type == StubSource.MERGED:
                # Use the default board folder instead of the GENERIC board folder (if it exists)
                if self.board.upper() == GENERIC_U:
                    family = fw_path.name.split("-")[0]
                    default_path = Path(
                        f"{family}-{clean_version(self.mpy_version, flat=True)}-{self.port}-{default_board(self.port, self.mpy_version)}-merged"
                    )
                    if (CONFIG.stub_path / default_path).exists():
                        fw_path = default_path
                updated_sources.append((stub_type, fw_path))
                # ---------
            else:
                updated_sources.append((stub_type, fw_path))
        return updated_sources

    def update_distribution(self, production: bool) -> bool:
        """Update the package .pyi files, if all the sources are available"""
        log.info(f"- Update {self.package_path.name}")
        log.trace(f"{self.package_path.as_posix()}")

        # check if the sources exist
        ok = self.are_package_sources_available()
        if not ok:
            log.debug(
                f"{self.package_name}: skipping as one or more source stub folders are missing"
            )
            self.status["error"] = "Skipped, stub folder(s) missing"
            shutil.rmtree(self.package_path.as_posix())
            self._publish = False  # type: ignore
            return False
        try:
            # update to -merged and fallback to GENERIC
            self.stub_sources = self.update_sources()
            self.update_package_files()
            self.update_pyproject_stubs()
            # for a new package the version could be 'latest', which is not a valid semver, so update
            self.pkg_version = self.next_package_version(production)
            return self.check()
        except Exception as e:  # pragma: no cover
            log.error(f"{self.package_name}: {e}")
            self.status["error"] = str(e)
            return False

    def build_distribution(
        self,
        production: bool,  # PyPI or Test-PyPi - USED TO FIND THE NEXT VERSION NUMBER
        force=False,  # BUILD even if no changes
    ) -> (
        bool
    ):  # sourcery skip: default-mutable-arg, extract-duplicate-method, require-parameter-annotation
        """
        Build a package
        look up the previous package version in the dabase
            - update package files
            - build the wheels and sdist

        :param production: PyPI or Test-PyPi -
        :param force: BUILD even if no changes
        :return: True if the package was built
        """
        log.info(f"Build: {self.package_path.name}")

        ok = self.update_distribution(production)
        self.status["version"] = self.pkg_version
        if not ok:
            log.info(f"{self.package_name}: skip - Could not build/update package")
            if not self.status["error"]:
                self.status["error"] = "Could not build/update package"
            return False

        # If there are changes to the package, then publish it
        if self.is_changed() or force:
            if force:
                log.info(f"Force build: {self.package_name} {self.pkg_version} ")
            else:
                log.info(
                    f"Found changes to package sources: {self.package_name} {self.pkg_version} "
                )
                log.trace(f"Old hash {self.hash} != New hash {self.calculate_hash()}")
            #  Build the distribution files
            old_ver = self.pkg_version
            self.pkg_version = self.next_package_version(production)
            self.status["version"] = self.pkg_version
            # to get the next version
            log.debug(
                f"{self.package_name}: bump version for {old_ver} to {self.pkg_version } {'production' if production else 'test'}"
            )
            self.write_package_json()
            log.trace(f"New hash: {self.package_name} {self.pkg_version} {self.hash}")
            if self.poetry_build():
                self.status["result"] = "Build OK"
            else:
                log.warning(f"{self.package_name}: skipping as build failed")
                self.status["error"] = "Poetry build failed"
                return False
        return True

    def publish_distribution_ifchanged(
        self,
        db: PysonDB,
        *,
        production: bool,  # PyPI or Test-PyPi
        build=False,  #
        force=False,  # publish even if no changes
        dry_run=False,  # do not actually publish
        clean: bool = False,  # clean up afterwards
    ) -> (
        bool
    ):  # sourcery skip: assign-if-exp, default-mutable-arg, extract-method, remove-unnecessary-else, require-parameter-annotation, swap-if-else-branches, swap-if-expression
        """
        Publish a package to PyPi
        look up the previous package version in the dabase, and only publish if there are changes to the package
        - change determied by hash across all files

        Build
            - update package files
            - build the wheels and sdist
        Publish
            - publish to PyPi
            - update database with new hash
        """
        log.info(f"Publish: {self.package_path.name}")
        # count .pyi files in the package
        filecount = len(list(self.package_path.rglob("*.pyi")))
        if filecount == 0:
            log.debug(f"{self.package_name}: starting build as no .pyi files found")
            build = True

        if build or force or self.is_changed():
            self.build_distribution(production=production, force=force)

        if not self._publish:
            log.debug(f"{self.package_name}: skip publishing")
            return False

        self.next_package_version(production=production)
        # Publish the package to PyPi, Test-PyPi or Github
        if self.is_changed():
            if self.mpy_version in SET_PREVIEW and production and not force:
                log.warning(
                    "version: `latest` package will only be available on Github, and not published to PyPi."
                )
                self.status["result"] = "Published to GitHub"
            else:
                return self.publish_distribution(dry_run, production, db)
        elif force:
            return self.publish_distribution(dry_run, production, db)
        else:
            log.info(f"No changes to package : {self.package_name} {self.pkg_version}")

        if clean:
            self.clean()
        return True

    def publish_distribution(self, dry_run, production, db):
        """
        Publishes the package to PyPi or Test-PyPi.

        Args:
            dry_run (bool): If True, performs a dry run without actually publishing.
            production (bool): If True, publishes to PyPi. If False, publishes to Test-PyPi.
            db: The database object to save the package state.

        Returns:
            bool: True if the publish was successful, False otherwise.
        """
        self.update_hashes()  # resets is_changed to False
        if not dry_run:
            pub_ok = self.poetry_publish(production=production)
        else:
            log.warning(
                f"{self.package_name}: Dry run, not publishing to {'' if production else 'Test-'}PyPi"
            )
            pub_ok = True
        if not pub_ok:
            log.warning(f"{self.package_name}: Publish failed for {self.pkg_version}")
            self.status["error"] = "Publish failed"
            return False
        self.status["result"] = "Published to PyPi" if production else "Published to Test-PyPi"
        self.update_hashes()
        if dry_run:
            log.warning(f"{self.package_name}: Dry run, not saving to database")
        else:
            # get the package state and add it to the database
            db.add(self.to_dict())
            db.commit()
        return True

    def are_package_sources_available(self) -> bool:
        """
        Check if (all) the packages sources exist.
        """
        ok = True
        for stub_type, src_path in self.update_sources():
            if (CONFIG.stub_path / src_path).exists():
                continue
            if stub_type == StubSource.FROZEN:
                # not a blocking issue if there are no frozen stubs, perhaps this port/board does not have any
                continue
            # todo: below is a workaround for different types, but where is the source of this difference coming from?
            msg = (
                f"{self.package_name}: source '{stub_type.value}' not found: {CONFIG.stub_path / src_path}"
                if isinstance(stub_type, StubSource)  # type: ignore
                else f"{self.package_name}: source '{stub_type}' not found: {CONFIG.stub_path / src_path}"
            )
            self.status["error"] = msg
            log.debug(msg)
            ok = False
        return ok
