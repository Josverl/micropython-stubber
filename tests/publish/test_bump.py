import pytest
from packaging.version import Version
from stubber.publish.bump import bump_version


@pytest.mark.parametrize(
    "before, after",
    [
        ("1.2.3", "1.2.3.post1"),
        ("1.0.0.post1", "1.0.0.post2"),
        ("1!2.0.0", "1!2.0.0.post1"),
        ("1.0.0.pre1", "1.0.0.post1"),  # drop prerelease and set postrelease
        ("1.2.3.a", "1.2.3.post1"),  # drop prerelease and set postrelease
        ("1.2.3.a4", "1.2.3.post1"),
        ("1.2.3.b", "1.2.3.post1"),  # drop prerelease and set postrelease
        ("1.2.3.b6", "1.2.3.post1"),  # drop prerelease and set postrelease
        ("1.2.3.rc1", "1.2.3.post1"),  # drop prerelease and set postrelease
        ("1.2.3-dev4", "1.2.3.post1-dev4"),  # different order
        ("1.2.3+local.4", "1.2.3.post1+local.4"),  # different order
    ],
)
def test_bump_post(before, after):
    version = Version(before)

    result = bump_version(version, post_bump=True)
    assert result == Version(after)


@pytest.mark.parametrize(
    "before, after",
    [
        ("1.2.3", "1.2.3.a456"),
        ("1.0.0.post1", "1.0.0.a456"),
        ("1!2.0.0", "1!2.0.0.a456"),
        ("1.0.0.pre1", "1.0.0.a456"),  # drop prerelease and set postrelease
        ("1.2.3.a", "1.2.3.a456"),  # drop prerelease and set postrelease
        ("1.2.3.a4", "1.2.3.a456"),
        ("1.2.3.b", "1.2.3.a456"),  # drop prerelease and set postrelease
        ("1.2.3.b6", "1.2.3.a456"),  # drop prerelease and set postrelease
        ("1.2.3.rc1", "1.2.3.a456"),  # drop prerelease and set postrelease
        ("1.2.3-dev4", "1.2.3.a456-dev4"),  # different order
        ("1.2.3+local.4", "1.2.3.a456+local.4"),  # different order
    ],
)
def test_bump_pre(before, after):
    version = Version(before)

    result = bump_version(version, rc=456)
    assert result == Version(after)


@pytest.mark.parametrize(
    "before, after",
    [
        ("1.2.3", "2.0.0"),
        ("1.2.3.post1", "2.0.0"),
        ("5!1.2.3.post1", "5!2.0.0"),
        ("1.2.3.a456", "2.0.0"),
        ("1.2.3.rc1", "2.0.0"),
        ("1.2.3-dev4", "2.0.0"),
        ("1.2.3+local.4", "2.0.0"),
    ],
)
def test_bump_major(before, after):
    version = Version(before)
    result = bump_version(version, major_bump=True)
    assert result == Version(after)


@pytest.mark.parametrize(
    "before, after",
    [
        ("1.2", "1.3"),
        ("1.2.3", "1.3.0"),
        ("1.2.3.post1", "1.3.0"),
        ("5!1.2.3.post1", "5!1.3.0"),
        ("1.2.3.a456", "1.3.0"),
        ("1.2.3.rc1", "1.3.0"),
        ("1.2.3-dev4", "1.3.0"),
        ("1.2.3+local.4", "1.3.0"),
    ],
)
def test_bump_minor(before, after):
    version = Version(before)
    result = bump_version(version, minor_bump=True)
    assert result == Version(after)


@pytest.mark.parametrize(
    "before, after",
    [
        ("1.2", "1.2.1"),
        ("1.2.3", "1.2.4"),
        ("1.2.3.post1", "1.2.4"),
        ("5!1.2.3.post1", "5!1.2.4"),
        ("1.2.3.a456", "1.2.4"),
        ("1.2.3.rc1", "1.2.4"),
        ("1.2.3-dev4", "1.2.4"),
        ("1.2.3+local.4", "1.2.4"),
    ],
)
def test_bump_micro(before, after):
    version = Version(before)
    result = bump_version(version, micro_bump=True)
    assert result == Version(after)

@pytest.mark.parametrize(
    "before, after",
    [
        ("1", "2"),
        ("1.2", "1.3"),
        ("1.2.3", "1.2.4"),
        ("1.2.3.post1", "1.2.4"),
        ("5!1.2.3.post1", "5!1.2.4"),
        ("1.2.3.a456", "1.2.4"),
        ("1.2.3.rc1", "1.2.4"),
        ("1.2.3-dev4", "1.2.4"),
        ("1.2.3+local.4", "1.2.4"),
    ],
)
def test_bump_version(before, after):
    version = Version(before)
    result = bump_version(version, version_bump=True)
    assert result == Version(after)
