"""Handle versions of micropython based on the git tags in the repo """

from github import Github
from packaging.version import parse


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
    nibbles = version.split("-")
    if not patch and nibbles[0] >= "1.10.0" and nibbles[0].endswith(".0"):
        # remove the last ".0"
        nibbles[0] = nibbles[0][:-2]
    if len(nibbles) == 1:
        version = nibbles[0]
    elif build:
        version = "-".join(nibbles) if commit else "-".join(nibbles[:-1])
    else:
        # version = "-".join((nibbles[0], LATEST))
        # HACK: this is not always right, but good enough most of the time
        version = "latest"
    if flat:
        version = version.strip().replace(".", "_")
    else:
        version = version.strip().replace("_", ".")

    if drop_v:
        version = version.lstrip("v")
    elif not version.startswith("v") and version.lower() != "latest":
        version = "v" + version
    return version


def micropython_versions(start="v1.9.2"):
    """Get the list of micropython versions from github tags"""
    try:
        g = Github()
        repo = g.get_repo("micropython/micropython")
        return [tag.name for tag in repo.get_tags() if parse(tag.name) >= parse(start)]
    except Exception:
        return ["v1.19.1", "v1.19", "v1.18", "v1.17", "v1.16", "v1.15", "v1.14", "v1.13", "v1.12", "v1.11", "v1.10", "v1.9.4", "v1.9.3"]
