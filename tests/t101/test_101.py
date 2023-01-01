##########################
import pytest
import stubber

##########################

pytest.skip("---===*** DEBUGGING ***===---", allow_module_level=True)


def test_minified(mock_micropython_path, fx_add_minified_path):
    from createstubs import __version__ as version  # type: ignore

    assert version


def test_version():
    assert stubber.__version__


def test_dummy():
    pass


def test_foo(pytestconfig, testrepo_micropython):
    if pytestconfig.getoption("verbose") > 0:
        assert 1
