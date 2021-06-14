import sys
from collections import namedtuple
import pytest

from pathlib import Path
# pyright: reportMissingImports=false

UName = namedtuple("UName", ["sysname", "nodename", "release", "version", "machine"])


# allow loading of the cpython mock-a-likes
core_mocks = "./tests/mocks/micropython-cpython_core"
if sys.path[1] != core_mocks:
    sys.path[1:1] = [core_mocks]

# ----------------------------------------------------------------------------------------
# Specify wether to load the normal or minified version of the test 
# ----------------------------------------------------------------------------------------
prefix = "minified."
from minified.createstubs import Stubber, read_path

# ----------------------------------------------------------------------------------------
# Below this the tests are identical between :
# - createstubs_board.test.py
# - createstubs_minified.test.py
# ----------------------------------------------------------------------------------------


def test_stubber_info_basic():
    stubber = Stubber() # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    info = stubber._info()
    print(info)
    assert info["family"] != "", "stubber.info() - No Family detected"
    assert info["port"] != "", "stubber.info() - No port detected"
    assert info["platform"] != "", "stubber.info() - No platform detected"
    assert info["ver"] != "", "stubber.info() - No clean version detected"

    assert stubber._fwid != "none"

    assert " " not in stubber.flat_fwid, "flat_fwid must not contain any spaces"
    assert "." not in stubber.flat_fwid, "flat_fwid must not contain any dots"

def test_stubber_info_custom():
    myid = "MyCustomID"
    stubber = Stubber(firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    assert stubber._fwid != "none"
    assert stubber._fwid == myid.lower()


#################################################
# test the fwid naming on the different platforms
#################################################

from collections import namedtuple

UName = namedtuple("uname", "sysname nodename release version machine")

# Lobo
lobo = UName(
    sysname="esp32_LoBo",
    nodename="esp32_LoBo",
    release="3.2.24",
    version="ESP32_LoBo_v3.2.24 on 2018-09-06",
    machine="ESP32 board with ESP32",
)
lobo_bt_ram = UName(
    sysname="esp32_LoBo",
    nodename="esp32_LoBo",
    release="3.2.24",
    version="ESP32_LoBo_v3.2.24 on 2018-09-06",
    machine="ESP32&psRAM board with ESP32",
)

# mpy 113
mpy_113 = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.13.0",
    version="v1.13 on 2020-09-02",
    machine="ESP32 module (spiram) with ESP32",
)
mpy_113_build = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.13.0",
    version="v1.13-103-gb137d064e on 2020-10-09",
    machine="ESP32 module (spiram) with ESP32",
)
mpy_110 = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.10.0",
    version="v1.10 on 2019-01-25",
    machine="ESP32 module with ESP32",
)

mpy_194 = UName(
    sysname="esp32",
    nodename="esp32",
    release="1.9.4",
    version="v1.9.4 on 2018-05-11",
    machine="ESP32 module with ESP32",
)

mpy_esp8622 = UName(
    sysname="esp8266",
    nodename="esp8266",
    release="2.2.0-dev(9422289)",
    version="v1.11-8-g48dcbbe60 on 2019-05-29",
    machine="ESP module with ESP8266",
)

pyb1_113 = UName(
    sysname="pyboard",
    nodename="pyboard",
    release="1.13.0",
    version="v1.13-95-g0fff2e03f on 2020-10-03",
    machine="PYBv1.1 with STM32F405RG",
)


@pytest.mark.parametrize(
    "fwid,  sys_imp_name, sys_platform, os_uname",
    [
        # mpy esp32
        ("micropython-esp32-1.9.4", "micropython", "esp32", mpy_194),
        ("micropython-esp32-1.10", "micropython", "esp32", mpy_110),
        ("micropython-esp32-1.13-103", "micropython", "esp32", mpy_113_build),
        # mpy esp8622
        # FIXME: Use version over release
        (
            "micropython-esp8622-2.2.0-dev(9422289)-8",
            "micropython",
            "esp8622",
            mpy_esp8622,
        ),
        # mpy pyb1
        ("micropython-pyb1-1.13-95", "micropython", "pyb1", pyb1_113),
        # lobo
        ("loboris-esp32-v3.2.24", "micropython", "esp32_LoBo", lobo),
        ("loboris-esp32-v3.2.24", "micropython", "esp32_LoBo", lobo_bt_ram),
        # ev3_pybricks_1_0_0
        (
            "ev3-pybricks-linux-1.0.0",
            "",
            "linux",
            UName(
                machine="ev3", nodename="ev3", release=None, sysname="ev3", version=None
            ),
        ),
    ],
)

#        # TODO: add support for -Latest
#        #('micropython-esp32-1.13-latest', 'micropython', 'esp32', mpy_113_build),


def test_stubber_fwid(mocker, fwid, sys_imp_name, sys_platform, os_uname):
    # class.property : just pass a value
    mocker.patch(prefix + "createstubs.sys.platform", sys_platform)
    mocker.patch(prefix + "createstubs.sys.implementation.name", sys_imp_name)
    # class.method--> mock using function
    fake_uname = os_uname

    def mock_uname():
        return fake_uname

    mocker.patch(prefix + "createstubs.os.uname", mock_uname, create=True)
    # now run the tests
    stubber = Stubber()
    assert stubber is not None, "Can't create Stubber instance"

    info = stubber._info()
    print("\nvalidating: " + fwid)
    print(info)

    assert info["family"] != "", "stubber.info() - No Family detected"
    assert info["port"] != "", "stubber.info() - No port detected"
    assert info["platform"] != "", "stubber.info() - No platform detected"
    assert info["ver"] != "", "stubber.info() - No clean version detected"

    assert stubber._fwid != "none"

    # Does the firmware id match
    assert stubber._fwid == fwid

    chars = " .()/\\:$"
    for c in chars:
        assert c not in stubber.flat_fwid, "flat_fwid must not contain '{}'".format(c)


def test_read_path():
    assert read_path() == ''


def test_get_obj_attributes():
    stubber = Stubber() # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    items, errors = stubber.get_obj_attributes(sys)
    assert items != []
    assert errors == []
    assert len(items) > 50
    for attr in items:
        assert type(attr) == tuple 


def test_create_all_stubs(tmp_path:Path):
    myid = "MyCustomID"

    stubber = Stubber(path = str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    stubber.modules = ["json","_thread","array"]
    stubber.add_modules(["http_client","webrepl","_internal"])
    stubber.create_all_stubs()
    
    stublist = list(tmp_path.glob('**/*.py'))
    assert len(stublist) == 3
    stubber.report() 
    stublist = list(tmp_path.glob('**/modules.json'))
    assert len(stublist) == 1

    stubber.clean()
    stublist = list(tmp_path.glob('**/*.*'))
    assert len(stublist) == 0

def test_get_root():
    stubber = Stubber()
    assert stubber is not None, "Can't create Stubber instance"
    x = stubber.get_root()
    assert type(x) == str
    assert len(x) > 0

    
def test_create_module_stub(tmp_path:Path):
    myid = "MyCustomID"
    stubber = Stubber(path = str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # just in the test folder , no structure
    stubber.create_module_stub("json", str( tmp_path / "json.py" ))
    stubber.create_module_stub("_thread", str(tmp_path / "_thread.py" ))
   
    stublist = list(tmp_path.glob('**/*.py'))
    assert len(stublist) == 2


def test_create_module_stub_folder(tmp_path:Path):
    myid = "MyCustomID"
    stubber = Stubber(path = str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    
    stubber.create_module_stub("json" )
    stublist = list((tmp_path / "stubs" / myid.lower()).glob('**/*.py'))
    assert len(stublist) == 1 , "should create stub in stub folder if no folder specified"    


def test_create_module_stub_ignored(tmp_path:Path):
    myid = "MyCustomID"
    stubber = Stubber(path = str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    #should not generate
    stubber.create_module_stub("_internal", str(tmp_path / "_internal.py" ))
    stubber.create_module_stub("http_client", str(tmp_path / "http_client.py" ))
    stubber.create_module_stub("webrepl", str(tmp_path / "webrepl.py" ))
    
    stublist = list(tmp_path.glob('**/*.py'))
    assert len(stublist) == 0




def test_nested_modules(tmp_path:Path):
    myid = "MyCustomID"
    stubber = Stubber(path = str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # just in the test folder , no structure
    stubber.create_module_stub("urllib/request", str( tmp_path / "request.py" ))
    stublist = list(tmp_path.glob('**/*.py'))
    assert len(stublist) == 1

def test_unavailable_modules(tmp_path:Path):
    myid = "MyCustomID"
    stubber = Stubber(path = str(tmp_path), firmware_id=myid)  # type: ignore
    assert stubber is not None, "Can't create Stubber instance"
    # this should not generate a module , but also should not th
    stubber.create_module_stub("notamodule1", str( tmp_path / "notamodule1.py" ))
    stubber.create_module_stub("not/amodule2", str( tmp_path / "notamodule2.py" ))
    stublist = list(tmp_path.glob('**/*.py'))
    assert len(stublist) == 0

# def test_clean(tmp_path):

#     myid = "MyCustomID"
#     test_path = str(tmp_path)
#     stub_path =  Path(test_path) /"stubs"/ myid.lower() 
#     stubber = Stubber(path = test_path, firmware_id=myid)  
#     stubber.clean()

#     #Create a file
#     stubber.create_module_stub("json", PurePosixPath( stub_path / "json.py") )
#     stublist = list(Path(test_path).glob('**/*.py'))
#     assert len(stublist) == 1
#     stubber.clean()
# Error 
# # tests\stubber\createstubs_info_mpy_test.py:244:
# # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
# # board\createstubs.py:435: in create_module_stub
# #     with open(file_name, "w") as fp:
# # _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

# # name = PurePosixPath('C:\\/Users/josverl/AppData/Local/Temp/pytest-of-josverl/pytest-39/test_clean0/stubs/mycustomid/json.py')
# # mode = 'w', args = (), kw = {}

# #     def open(name, mode="r", *args, **kw):
# # >       f = io.open(name, mode, *args, **kw)
# # E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\/Users/josverl/AppData/Local/Temp/pytest-of-josverl/pytest-39/test_clean0/stubs/mycustomid/json.py'

# # tests\mocks\micropython-cpython_core\uio.py:44: FileNotFoundError

