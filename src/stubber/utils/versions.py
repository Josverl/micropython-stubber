"""Handle versions of micropython based on the git tags in the repo """

from functools import lru_cache
from pathlib import Path

from github import Github
from loguru import logger as log
from packaging.version import parse

import stubber.basicgit as git
import stubber.utils as utils

OLDEST_VERSION = "1.16"
"This is the oldest MicroPython version to build the stubs on"

V_PREVIEW = "preview"
"Latest preview version"

SET_PREVIEW = {"preview", "latest", "master"}


def clean_version(
    version: str,
    *,
    build: bool = False,
    patch: bool = False,
    commit: bool = False,
    drop_v: bool = False,
    flat: bool = False,
):
    "Clean up and transform the many flavours of versions"
    # 'v1.13.0-103-gb137d064e' --> 'v1.13-103'
    if version in {"", "-"}:
        return version
    if version.lower() == "stable":
        _v = get_stable_mp_version()
        if not _v:
            log.warning("Could not determine the latest stable version")
            return "stable"
        version = _v
        log.trace(f"Using latest stable version: {version}")
    is_preview = "-preview" in version
    nibbles = version.split("-")
    ver_ = nibbles[0].lower().lstrip("v")
    if not patch and ver_ >= "1.10.0" and ver_ < "1.20.0" and ver_.endswith(".0"):
        # remove the last ".0" - but only for versions between 1.10 and 1.20 (because)
        nibbles[0] = nibbles[0][:-2]
    if len(nibbles) == 1:
        version = nibbles[0]
    elif build and not is_preview:
        version = "-".join(nibbles) if commit else "-".join(nibbles[:-1])
    else:
        # version = "-".join((nibbles[0], LATEST))
        # HACK: this is not always right, but good enough most of the time
        if is_preview:
            version = "-".join((nibbles[0], V_PREVIEW))
        else:
            version = V_PREVIEW
    if flat:
        version = version.strip().replace(".", "_").replace("-", "_")
    else:
        version = version.strip().replace("_preview", "-preview").replace("_", ".")

    if drop_v:
        version = version.lstrip("v")
    elif not version.startswith("v") and version.lower() not in SET_PREVIEW:
        version = "v" + version
    if version in SET_PREVIEW:
        version = V_PREVIEW
    return version


@lru_cache(maxsize=10)
def checkedout_version(path: Path, flat: bool = False) -> str:
    """Get the checked-out version of the repo"""
    version = git.get_local_tag(path.as_posix())
    if not version:
        raise ValueError("No valid Tag found")
    version = utils.clean_version(version, flat=flat, drop_v=False)
    return version


def micropython_versions(minver: str = "v1.20", reverse: bool = False):
    """Get the list of micropython versions from github tags"""
    try:
        gh_client = Github()
        repo = gh_client.get_repo("micropython/micropython")
        versions = [tag.name for tag in repo.get_tags() if parse(tag.name) >= parse(minver)]
        # Only keep the last preview
        versions = [v for v in versions if not v.endswith(V_PREVIEW) or v == versions[-1]]
    except Exception:
        versions = [
            "v9.99.9-preview",
            "v1.22.2",
            "v1.22.1",
            "v1.22.0",
            "v1.21.1",
            "v1.21.0",
            "v1.20.0",
            "v1.19.1",
            "v1.19",
            "v1.18",
            "v1.17",
            "v1.16",
            "v1.15",
            "v1.14",
            "v1.13",
            "v1.12",
            "v1.11",
            "v1.10",
        ]
    versions = [v for v in versions if parse(v) >= parse(minver)]
    # remove all but the most recent (preview) version
    versions = versions[:1] + [v for v in versions if "preview" not in v]
    return sorted(versions, reverse=reverse)


def get_stable_mp_version() -> str:
    # read the versions from the git tags
    all_versions = micropython_versions(minver=OLDEST_VERSION)
    return [v for v in all_versions if not v.endswith(V_PREVIEW)][-1]


def get_preview_mp_version() -> str:
    # read the versions from the git tags
    all_versions = micropython_versions(minver=OLDEST_VERSION)
    return [v for v in all_versions if v.endswith(V_PREVIEW)][-1]

