import os
import glob
import pytest

#SOT
import basicgit as git
import freezer_mpy

# No Mocks, does actual extraction from repro
# todo: get seperate test instaNCE OF THE REPO



@pytest.mark.parametrize(
    "path, port, board",
    [   ('C:\\develop\\MyPython\\micropython\\ports\\esp32\\modules\\_boot.py', 
         'esp32', None),
        ('/develop/micropython/ports/esp32/modules/_boot.py',
         'esp32', None),
        ('../micropython/ports/esp32/modules/_boot.py',
         'esp32', None),
        ('C:\\develop\\MyPython\\micropython\\ports\\stm32\\boards\\PYBV11\\modules\\_boot.py',
         'stm32', 'PYBV11'),
        ('/develop/micropython/ports/stm32/boards/PYBV11/modules/_boot.py',
         'stm32', 'PYBV11'),
        ('../micropython/ports/stm32/boards/PYBV11/modules/_boot.py',
         'stm32', 'PYBV11'),
    ]
)

def test_extract_target_names(path, port, board):
    _port, _board = freezer_mpy.get_target_names(path)
    assert _board == board
    assert _port == port


def test_freezer_mpy_manifest(tmp_path, gitrepo_micropython):
    "test if we can freeze source using manifest.py files"
    mpy_path = gitrepo_micropython
    # mpy version must be at 1.12 or newer
    mpy_version = 'v1.12'

    version = git.get_tag(mpy_path)
    if version < mpy_version:
        git.checkout_tag(mpy_version, mpy_path)
        version = git.get_tag(mpy_path)
        assert version == mpy_version, "prep: could not checkout version {} of ../micropython".format(mpy_version)

    stub_path = tmp_path
    freezer_mpy.get_frozen(stub_path, mpy_path, lib_path='../micropython-lib')
    scripts = glob.glob(str(stub_path)  + '/**/*.py', recursive=True)

    assert scripts is not None, "can freeze scripts from manifest"
    assert len(scripts) > 50, "expect at least 50 files, only found {}".format(len(scripts))


    #assert len(list(tmp_path.iterdir())) == 18, "there should be 18 files"


def test_freezer_mpy_folders(tmp_path, gitrepo_micropython):
    "test if we can freeze source using modules folders"
    mpy_path = gitrepo_micropython

    # mpy version must be older than 1.12 ( so use 1.10)
    mpy_version = 'v1.10'
    version = git.get_tag(mpy_path)
    if version != mpy_version:
        git.checkout_tag(mpy_version, mpy_path)
        version = git.get_tag(mpy_path)
        assert version == mpy_version, "prep: could not checkout version {} of ../micropython".format(mpy_version)

    stub_path = tmp_path
    # freezer_mpy.get_frozen(stub_path, mpy_path, lib_path='../micropython-lib')
    freezer_mpy.get_frozen_folders(stub_path, mpy_path, lib_path='../micropython-lib')
    assert True


