from packaging.version import Version, parse


# def bump_postrelease(
#     current: Version,
#     rc: int = 0,  # o, to bump post release, or release candidate number
# ) -> Version:
#     return bump_version( current, rc=rc , post_bump=True  )


def bump_version(
    current: Version,
    *,
    major_bump: bool = False,
    minor_bump: bool = False,
    micro_bump: bool = False,
    version_bump: bool = False,  # Increase the first non-zero of micro , minor , major
    post_bump: bool = False,
    rc: int = 0,  # to bump post release, or release candidate number
) -> Version:
    """
    Increases the post release version number

    This allows for a new stub-release to be published while still using the Major.Minor.Patch version numbers of Micropython
    if rc = 0(default) : bump post release
        format: x.y.z.post1, x.y.z.post2 ...
    if rec specified:
        drop the post release and set the release candidate number

    ref: https://peps.python.org/pep-0440/
    """
    release_bump = major_bump or minor_bump or micro_bump or version_bump
    other_bump = post_bump or rc != 0

    if release_bump and other_bump:
        raise ValueError("Cannot bump both release and other fragments")

    parts = []

    # ----------------------------------------------------------------------
    # Epoch
    if current.epoch != 0:
        parts.append(f"{current.epoch}!")
    # ----------------------------------------------------------------------
    # Release segment: major.minor.micro x.y.z
    major = current.major
    minor = current.minor
    micro = current.micro
    if version_bump:  # Increase the first non-zero of micro , minor , major
        if micro != 0:
            micro_bump = True
        elif minor != 0:
            minor_bump = True
        elif major != 0:
            major_bump = True
        else:
            raise ValueError("Cannot bump version, all version numbers are zero")

    # higher level bump clears lowers
    major = major + 1 if major_bump else major
    minor = 0 if major_bump else minor + 1 if minor_bump else minor
    micro = 0 if minor_bump or major_bump else micro + 1 if micro_bump else micro

    release = f"{major}.{minor}.{micro}"
    parts.append(release)
    if not release_bump:
        # ----------------------------------------------------------------------
        # pre
        if rc != 0:
            # Pre-release / alpha / beta / rc segment
            parts.append(f".a{rc}")
        # ----------------------------------------------------------------------
        # post
        if post_bump and rc == 0:
            parts.append(".post1" if current.post is None else f".post{current.post + 1}")
        # ----------------------------------------------------------------------
        # Development release
        if current.dev is not None:
            parts.append(f".dev{current.dev}")

        # ----------------------------------------------------------------------
        # Local version segment
        if current.local is not None:
            parts.append(f"+{current.local}")

    new = parse("".join(parts))
    # Sanity check that the new version is valid
    if not isinstance(new, Version):
        raise ValueError(f"{new} is not a valid version")

    return new
