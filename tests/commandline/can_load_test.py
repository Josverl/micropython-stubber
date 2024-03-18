import pytest

pytestmark = [pytest.mark.stubber]


def test_can_load():
    # can we import the base module?
    import stubber  # type: ignore
