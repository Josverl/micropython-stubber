import pytest
from packaging.version import Version, parse
from stubber.publish.bump import bump_postrelease


@pytest.mark.parametrize(
    "before, after",
    [
        ("1.2.3", "1.2.3.post1"),
        ("1.0.0.post1", "1.0.0.post2"),
        ("1!2.0.0", "1!2.0.0.post1"),
        ("1.0.0.pre1", "1.0.0.pre1.post1"),
        ("1.2.3.a", "1.2.3.a0.post1"),  # a--> a0
        ("1.2.3.a4", "1.2.3.a4.post1"),
        ("1.2.3.b", "1.2.3.b0.post1"),
        ("1.2.3.b6", "1.2.3.b6.post1"),
        ("1.2.3.rc1", "1.2.3.rc1.post1"),
        ("1.2.3-dev4", "1.2.3.post1-dev4"),  # different order
        ("1.2.3+local.4", "1.2.3.post1+local.4"),  # different order
    ],
)
def test_bump(before, after):
    version = Version(before)
    result = bump_postrelease(version)
    assert result == Version(after)
