# others
import pytest
from pathlib import Path
import shutil

# SOT
import utils


@pytest.mark.parametrize(
    "commit, build, clean",
    [
        ("v1.13-103-gb137d064e", True, "v1.13-103"),
        ("v1.13-103-gb137d064e", False, "v1.13-N"),
        ("v1.13", True, "v1.13"),
        ("v1.13", False, "v1.13"),
        # #BUG:?
        ("v1.13-dirty", True, "v1.13"),
        ("v1.13-dirty", False, "v1.13-N"),
    ],
)
def test_clean_version(commit, build, clean):
    assert utils.clean_version(commit, build) == clean


# test manifest()


# make manifest


# make stub file
def test_make_stub_files(tmp_path):
    dest = tmp_path / "stubs"
    shutil.copytree("./tests/data/stubs", dest)
    result = utils.generate_pyi_files(dest)
    py_count = len(list(Path(dest).glob("**/*.py")))
    pyi_count = len(list(Path(dest).glob("**/*.pyi")))
    assert py_count == pyi_count, "1:1 py:pyi"
    # for py missing pyi:
    py_files = list(dest.rglob("*.py"))
    pyi_files = list(dest.rglob("*.pyi"))
    for pyi in pyi_files:
        # remove all py files that have been stubbed successfully
        try:
            py_files.remove(pyi.with_suffix(".py"))
        except ValueError:
            pass
    assert len(py_files) == 0 , "py and pyi files should match 1:1 and stored in the same folder"

def test_read_exclusion():
    exclusions = utils.read_exclusion_file()
    assert type(exclusions) == list, "should be a list"
    assert len(exclusions) > 0, "should contain some values"
    for l in exclusions:
        assert l.strip() == l, "Lines should be trimmed"
        assert len(l) > 0, "empty lines should be removed"
        assert l[0] != "#", "comment lines should be removed"


def test_read_exclusion_nonexistent_folder():
    exclusions = utils.read_exclusion_file(Path("./ThisFolderDoesNotExists"))
    assert type(exclusions) == list, "should be a list"
    assert len(exclusions) == 0, "Should conain no values"


def test_read_exclusion_nonexistent_drive():
    exclusions = utils.read_exclusion_file(Path("!:\\"))
    assert type(exclusions) == list, "should be a list"
    assert len(exclusions) == 0, "Should conain no values"


def test_should_ignore():
    exclusions = []
    assert not utils.should_ignore("somefile.abc", exclusions), "No match"
    assert utils.should_ignore("somefile.abc", ["*.abc"]), "Match simple"
    assert not utils.should_ignore("somefile.abc", exclusions)
    assert utils.should_ignore("somefile.abc", ["**/*.py", "*.abc"]), "Match second"
