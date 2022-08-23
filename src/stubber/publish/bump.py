from packaging.version import Version, parse


def bump_postrelease(
    current: Version,
) -> Version:
    """
    Increases the post release version number

    This allows for a new stub-release to be published while still using the Major.Minor.Patch version numbers of Micropython
    format: x.y.z.post1, x.y.z.post2 ...

    ref: https://peps.python.org/pep-0440/
    """
    parts = []
    # Epoch
    if current.epoch != 0:
        parts.append(f"{current.epoch}!")
    # Release segment
    parts.append(".".join(str(x) for x in current.release))
    # Pre-release
    if current.pre is not None:
        parts.append("".join(str(x) for x in current.pre))
    # BUMP Post-release
    if current.post is not None:
        parts.append(f".post{current.post + 1}")
    else:
        parts.append(f".post{1}")
    # Development release
    if current.dev is not None:
        parts.append(f".dev{current.dev}")

    # Local version segment
    if current.local is not None:
        parts.append(f"+{current.local}")

    new = parse("".join(parts))
    if not isinstance(new, Version):
        raise ValueError(f"{new} is not a valid version")

    return new
