# others
import pytest
from pathlib import Path
import shutil

# SOT
import utils

do_profiling = False
if do_profiling:
    import cProfile
    from pstats import Stats, SortKey


@pytest.mark.parametrize(
    "commit, build, clean",
    [
        ("v1.13-103-gb137d064e", True, "v1.13-103"),
        ("v1.13", True, "v1.13"),
        ("v1.13-dirty", True, "v1.13"),
        ("v1.13-103-gb137d064e", False, "v1.13-Latest"),
        ("v1.13", False, "v1.13"),
        ("v1.13-dirty", False, "v1.13-Latest"),
    ],
)
def test_clean_version_build(commit, build, clean):
    assert utils.clean_version(commit, build=build) == clean


def test_clean_version():
    assert utils.clean_version("-") == "-"
    assert utils.clean_version("0.0") == "v0.0"
    assert utils.clean_version("1.9.3") == "v1.9.3"
    assert utils.clean_version("v1.9.3") == "v1.9.3"
    assert utils.clean_version("v1.10.0") == "v1.10"
    assert utils.clean_version("v1.13.0") == "v1.13"
    assert utils.clean_version("v1.13.0-103-gb137d064e") == "v1.13-Latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", build=True) == "v1.13-103"
    assert utils.clean_version("v1.13.0-103-gb137d064e", build=True, commit=True) == "v1.13-103-gb137d064e"
    # with path
    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True) == "v1.13.0-Latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True, build=True) == "v1.13.0-103"
    # with commit
    assert utils.clean_version("v1.13.0-103-gb137d064e", patch=True, build=True, commit=True) == "v1.13.0-103-gb137d064e"
    # FLats
    assert utils.clean_version("v1.13.0-103-gb137d064e", flat=True) == "v1_13-Latest"
    assert utils.clean_version("v1.13.0-103-gb137d064e", build=True, commit=True, flat=True) == "v1_13-103-gb137d064e"

    # all options , no V for version
    assert (
        utils.clean_version("v1.13.0-103-gb137d064e", patch=True, build=True, commit=True, flat=True, drop_v=True)
        == "1_13_0-103-gb137d064e"
    )


# make stub file
def test_make_stub_files_OK(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-ok"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    result = utils.generate_pyi_files(dest)
    py_count = len(list(Path(dest).glob("**/*.py")))
    pyi_count = len(list(Path(dest).glob("**/*.pyi")))
    assert py_count == pyi_count, "1:1 py:pyi"
    # for py missing pyi:
    py_files = list(dest.rglob("*.py"))
    pyi_files = list(dest.rglob("*.pyi"))
    for pyi in pyi_files:
        # remove all py files  from list that have been stubbed successfully
        try:
            py_files.remove(pyi.with_suffix(".py"))
        except ValueError:
            pass
    assert len(py_files) == 0, "py and pyi files should match 1:1 and stored in the same folder"


def test_stub_one_file(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-issues"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    file = list(dest.rglob("micropython.py"))[0]
    result = utils.generate_pyi_from_file(file=file)
    print(f"result : {result}")
    assert result != False


def test_stub_one_bad_file(tmp_path, pytestconfig):
    source = pytestconfig.rootpath / "tests/data/stubs-issues"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    file = list(dest.rglob("machine.py"))[0]
    r = utils.generate_pyi_from_file(file=file)
    # Should not have been processed
    assert r == False


# make stub file
def test_make_stub_files_issues(tmp_path, pytestconfig):
    # Deal with some files having issues
    source = pytestconfig.rootpath / "tests/data/stubs-issues"
    dest = tmp_path / "stubs"
    shutil.copytree(source, dest)
    PROBLEMATIC = 1  # number of files with issues

    if do_profiling:
        with cProfile.Profile() as pr:
            result = utils.generate_pyi_files(dest)

        with open("profiling_stats.txt", "w") as stream:
            stats = Stats(pr, stream=stream)
            stats.strip_dirs()
            stats.sort_stats("time")
            stats.dump_stats(".prof_stats")
            stats.print_stats()

    else:
        result = utils.generate_pyi_files(dest)

    py_count = len(list(Path(dest).glob("**/*.py")))
    pyi_count = len(list(Path(dest).glob("**/*.pyi")))

    assert py_count == pyi_count + PROBLEMATIC, "1:1 py:pyi"
    # for py missing pyi:
    py_files = list(dest.rglob("*.py"))
    pyi_files = list(dest.rglob("*.pyi"))
    for pyi in pyi_files:
        # remove all py files that have been stubbed successfully
        try:
            py_files.remove(pyi.with_suffix(".py"))
        except ValueError:
            pass

    assert len(py_files) == PROBLEMATIC, "py and pyi files should match 1:1 and stored in the same folder"


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
