# run createsubs in the unix version of micropython
import os
import subprocess
from pathlib import Path
import pytest

#  ROOT = Path(__file__).parent

@pytest.mark.parametrize(
    "script_folder", [ ('./board') , ('./minified') ]
)

def test_createstubs(script_folder):
    # run createsubs in the unix versionof micropython
    Path('./')

    #why is this different on linux python 3.6.9 ? no option to capture the output ?
    # capture_output is supported only with Python 3.7,
        # By default, stdout and stderr are not captured, and those attributes
        #     will be None. Pass stdout=PIPE and/or stderr=PIPE in order to capture them.
    os.getcwd()
    scriptfolder = os.path.abspath(script_folder)

    cmd = [os.path.abspath('tools/micropython'), 'createstubs.py']
#    cmd = [os.path.abspath('tools/micropython')]
    #todo: delete stubs folder beforehand
    # import shutil
    # shutil.rmtree('remDemo/')
    try:
        subproc = subprocess.run(cmd,cwd=scriptfolder, timeout=100000)
        # assert (subproc.returncode == 0 ), "createstubs ran with an error"
    except ImportError:
        pass
    # did it run without error ?
    
    stubfolder = Path(scriptfolder)  / 'stubs'
    stubfiles = list(stubfolder.rglob('*.py'))
    # filecount 
    assert (len(stubfiles) >= 45 ), "there should be 45 stubs or more"

    # manifest exists
    jsons = list(stubfolder.rglob('*.json'))
    assert (len(jsons) == 1 ), "there should be 1 manifest"

    # manifest is valid json 
    pass


