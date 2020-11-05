# run createsubs in the unix version of micropython
import os
import sys
import subprocess
from pathlib import Path
import pytest

#  ROOT = Path(__file__).parent

@pytest.mark.parametrize(
    "script_folder", [ ('./board') , ('./minified') ]
)

def test_createstubs(tmp_path, script_folder):
    # run createsubs in the unix version of micropython
    # Use temp_path to generate stubs 
    scriptfolder = os.path.abspath(script_folder)
    cmd = [os.path.abspath('tools/micropython'), 'createstubs.py', '--path', tmp_path]
    try:
        subproc = subprocess.run(cmd,cwd=scriptfolder, timeout=100000)
        assert (subproc.returncode == 0 ), "createstubs ran with an error"
    except ImportError:
        pass
    # did it run without error ?
    
    stubfolder = Path(tmp_path)  / 'stubs'
    stubfiles = list(stubfolder.rglob('*.py'))
    # filecount 
    assert (len(stubfiles) >= 45 ), "there should be 45 stubs or more"

    # manifest exists
    jsons = list(stubfolder.rglob('*.json'))
    assert (len(jsons) == 1 ), "there should be 1 manifest"

    # manifest is valid json 
    pass


