# run createsubs in the unix version of micropython
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent

def test_createstubs():
    # run createsubs in the unix versionof micropython
    Path('./')

    #why is this different on linux python 3.6.9 ? no option to capture the output ?
    # capture_output is supported only with Python 3.7,
        # By default, stdout and stderr are not captured, and those attributes
        #     will be None. Pass stdout=PIPE and/or stderr=PIPE in order to capture them.
    os.getcwd()
    scriptfolder = os.path.abspath('./board')
    scriptfolder = os.path.abspath('./minified')
    cmd = [os.path.abspath('tools/micropython'), 'createstubs.py']
#    cmd = [os.path.abspath('tools/micropython')]
    #todo: delete stubs folder beforehand
    here = os.getcwd()
    print('current directory', here)

    # subproc = subprocess.run(cmd,cwd=scriptfolder, timeout=100000)
    # assert (subproc.returncode == 0 ), "createstubs ran with an error"

    here = os.getcwd()
    print('current directory', here)

    # did it run withouth error ?
    
    stubfolder = Path(scriptfolder)  / 'stubs'
    stubfiles = list(stubfolder.rglob('*.py'))
    # filecount 
    assert (len(stubfiles) >= 40 ), "there should be 50 stubs or more"

    # manifest exists
    jsons = list(stubfolder.rglob('*.json'))
    assert (len(jsons) == 1 ), "there should be 1 manifest"

    # manifest is valid json 
    pass


test_createstubs()

