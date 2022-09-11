import pytest

# Module Under Test
import stubber.get_cpython as get_cpython


# No Mocks, does actual extraction using pip-install
@pytest.mark.skip(reason="Does actual extraction using pip-install")
@pytest.mark.parametrize(
    "requirements",
    [
        "requirements-core-micropython.txt",
        "requirements-core-pycopy.txt",
    ],
)
@pytest.mark.slow
def test_get_cpython(requirements, tmp_path):
    get_cpython.get_core(requirements=requirements, stub_path=tmp_path)
    stubfiles = list(tmp_path.rglob("*.py"))
    assert len(stubfiles) > 1
