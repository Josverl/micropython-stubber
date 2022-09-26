import csv
import pkgutil
import tempfile
from collections import defaultdict
from pathlib import Path

import stubber.basicgit as git
from loguru import logger as log

# # log = logging.getLogger(__name__)


def switch(tag: str, *, mpy_path: Path, mpy_lib_path: Path):
    """
    Switch to a specific version of the micropython repos.

    Specify the version with --tag or --version to specify the version tag
    of the MicroPython repo.
    The Micropython-lib repo will be checked out to a commit that corresponds
    in time to that version tag, in order to allow non-current versions to be
    stubbed correctly.

    The repros must be cloned already
    """
    # fetch then switch
    git.fetch(mpy_path)
    git.fetch(mpy_lib_path)

    if not tag or tag in ["master", ""]:
        tag = "latest"
    if tag == "latest":
        git.switch_branch(repo=mpy_path, branch="master")
    else:
        git.checkout_tag(repo=mpy_path, tag=tag)
    match_lib_with_mpy(version_tag=tag, lib_path=mpy_lib_path)


def read_micropython_lib_commits(filename="data/micropython_tags.csv"):
    """
    Read a csv with the micropython version and matchin micropython-lib commit-hashes
    these can be used to make sure that the correct micropython-lib version is checked out.

    filename is relative to the 'stubber' package

    TODO: it would be nice if micropython-lib had matching commit-tags

        git for-each-ref --sort=creatordate --format '%(refname) %(creatordate)' refs/tags
    """
    data = pkgutil.get_data("stubber", filename)
    if not data:
        raise Exception(f"Resource {filename} not found")
    version_commit = defaultdict()  # lgtm [py/multiple-definition]
    with tempfile.NamedTemporaryFile(prefix="tags", suffix=".csv", mode="w+t") as ntf:
        ntf.file.write(data.decode(encoding="utf8"))
        ntf.file.seek(0)
        # read the csv file using DictReader
        reader = csv.DictReader(ntf.file, skipinitialspace=True)  # dialect="excel",
        rows = list(reader)
        # create a dict version --> commit_hash
        version_commit = {row["version"].split("/")[-1]: row["lib_commit_hash"] for row in rows if row["version"].startswith("refs/tags/")}
    # add default
    version_commit = defaultdict(lambda: "master", version_commit)
    return version_commit


def match_lib_with_mpy(version_tag: str, lib_path: Path):
    micropython_lib_commits = read_micropython_lib_commits()
    # Make sure that the correct micropython-lib release is checked out
    log.info(f"Matching repo's:  Micropython {version_tag} needs micropython-lib:{micropython_lib_commits[version_tag]}")
    return git.checkout_commit(micropython_lib_commits[version_tag], lib_path)
