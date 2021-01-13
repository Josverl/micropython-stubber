import sys
if sys.path[0] != 'c:\\develop\\MyPython\\micropython-stubber\\board':
 sys.path[0:0] = ['c:\\develop\\MyPython\\micropython-stubber\\board']

# allow loading of the cpython mockalikes 
if sys.path[1] != 'c:\\develop\\MyPython\\micropython-stubber\\all-stubs\\cpython_core':
 sys.path[1:1] = ['c:\\develop\\MyPython\\micropython-stubber\\all-stubs\\cpython_core']

from createstubs import Stubber

def test_stubber_info():
    stubber = Stubber()
    assert stubber != None, "Can't create Stubber instance"

    info = stubber._info()
    print(info)
    assert info["family"] != '', "stubber.info() - No Family detected"
    assert info["port"] != '', "stubber.info() - No port detected"
    assert info["platform"] != '', "stubber.info() - No platform detected"
    assert info["ver"] != '', "stubber.info() - No clean version detected"

    assert stubber._fwid != 'none'

    assert ' ' not in stubber.flat_fwid , "flat_fwid must not contain any spaces"
    assert '.' not in stubber.flat_fwid , "flat_fwid must not contain any dots"


if __name__ == "__main__":
    test_stubber_info()
