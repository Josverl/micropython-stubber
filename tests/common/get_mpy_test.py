# Module Under Test
import get_mpy
from utils import clean_version, flat_version

# No Mocks, does actual download from github
import basicgit as git


def test_get_mpy(tmp_path):

    # Use Submodules 
    mpy_path = "./micropython"
    lib_path = "./micropython-lib"
    try: 
        version = clean_version(git.get_tag(mpy_path))
    except:
        version = "v1.15"

    assert version, "could not find micropython version"
    print("found micropython version : {}".format(version))
    # folder/{family}-{version}-frozen
    family = "micropython"
    stub_path = "{}-{}-frozen".format(family, flat_version(version))
    get_mpy.get_frozen(
        str(tmp_path / stub_path), version=version, mpy_path=mpy_path, lib_path=lib_path
    )

    if version >= "v1.15":
        modules_count = len(list((tmp_path / stub_path).glob("**/modules.json")))
        assert modules_count >= 7, "there should at least 7 module manifests"

        stub_count = len(list((tmp_path / stub_path).glob("**/*.py")))
        assert stub_count >= 100, "there should > 100 frozen modules"
