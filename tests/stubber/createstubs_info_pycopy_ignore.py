import sys
from collections import namedtuple
import pytest

# pylint: disable=import-error,wrong-import-position
# pyright: reportMissingImports=false

UName = namedtuple('UName', ['sysname', 'nodename', 'release', 'version', 'machine'])

if sys.path[0] != './board':
    sys.path[0:0] = ['./board']

# allow loading of the cpython mock-alikes
core_mocks = './tests/mocks/pycopy-cpython_core'
if sys.path[1] != core_mocks:
    sys.path[1:1] = [core_mocks]

from createstubs import Stubber # type: ignore

def test_stubber_info():
    stubber = Stubber() # type: ignore
    assert stubber is not None, "Can't create Stubber instance"

    info = stubber._info()
    print(info)
    assert info["family"] != '', "stubber.info() - No Family detected"
    assert info["port"] != '', "stubber.info() - No port detected"
    assert info["platform"] != '', "stubber.info() - No platform detected"
    assert info["ver"] != '', "stubber.info() - No clean version detected"

    assert stubber._fwid != 'none'

    assert ' ' not in stubber.flat_fwid , "flat_fwid must not contain any spaces"
    assert '.' not in stubber.flat_fwid , "flat_fwid must not contain any dots"

#################################################
# test the fwid naming on the different platforms
#################################################

from collections import namedtuple
UName = namedtuple('uname', 'sysname nodename release version machine')

#Lobo 
lobo            = UName(sysname='esp32_LoBo', nodename='esp32_LoBo', release='3.2.24', version='ESP32_LoBo_v3.2.24 on 2018-09-06', machine='ESP32 board with ESP32')
lobo_bt_ram     = UName(sysname='esp32_LoBo', nodename='esp32_LoBo', release='3.2.24', version='ESP32_LoBo_v3.2.24 on 2018-09-06', machine='ESP32&psRAM board with ESP32')

#mpy 113
mpy_113         = UName(sysname='esp32', nodename='esp32', release='1.13.0', version='v1.13 on 2020-09-02', machine='ESP32 module (spiram) with ESP32')
mpy_113_build   = UName(sysname='esp32', nodename='esp32', release='1.13.0', version='v1.13-103-gb137d064e on 2020-10-09', machine='ESP32 module (spiram) with ESP32')
mpy_110         = UName(sysname='esp32', nodename='esp32', release='1.10.0', version='v1.10 on 2019-01-25', machine='ESP32 module with ESP32')

mpy_194         = UName(sysname='esp32', nodename='esp32', release='1.9.4', version='v1.9.4 on 2018-05-11', machine='ESP32 module with ESP32')

mpy_esp8622     = UName(sysname='esp8266', nodename='esp8266', release='2.2.0-dev(9422289)', version='v1.11-8-g48dcbbe60 on 2019-05-29', machine='ESP module with ESP8266')

pyb1_113        = UName(sysname='pyboard', nodename='pyboard', release='1.13.0', version='v1.13-95-g0fff2e03f on 2020-10-03', machine='PYBv1.1 with STM32F405RG')


@pytest.mark.parametrize(
    "fwid,  sys_imp_name, sys_platform, os_uname",
    [   
        # mpy esp32 
        ('pycopy-esp32-1.9.4', 'micropython', 'esp32', mpy_194),
        ('pycopy-esp32-1.10', 'micropython', 'esp32', mpy_110),

        ('pycopy-esp32-1.13-103', 'micropython', 'esp32', mpy_113_build),
        # mpy esp8622
        # FIXME: Use version over release
        ('pycopy-esp8622-2.2.0-dev(9422289)-8', 'micropython', 'esp8622', mpy_esp8622),
        # mpy pyb1
        ('pycopy-pyb1-1.13-95', 'micropython', 'pyb1', pyb1_113),
    ]
)

def test_stubber_fwid(mocker, fwid,  sys_imp_name, sys_platform, os_uname):
    # class.property : just pass a value
    mocker.patch(
        'createstubs.sys.platform',
        sys_platform
    )
    mocker.patch(
        'createstubs.sys.implementation.name',
        sys_imp_name
    )
    # class.method--> mock using function
    fake_uname = os_uname
    def mock_uname():
        return fake_uname
    mocker.patch(
        'createstubs.os.uname',
        mock_uname, create=True
    )
    # now run the tests
    stubber = Stubber()  
    assert stubber is not None, "Can't create Stubber instance"

    info = stubber._info()
    print('\nvalidating: '+fwid)
    print(info)
    

    assert info["family"] != '', "stubber.info() - No Family detected"
    assert info["family"] == 'pycopy', "stubber.info() - family pycopy expected"
    assert info["port"] != '', "stubber.info() - No port detected"
    assert info["platform"] != '', "stubber.info() - No platform detected"
    assert info["ver"] != '', "stubber.info() - No clean version detected"

    assert stubber._fwid != 'none'

    # Does the firmware id match
    assert stubber._fwid == fwid

    chars = " .()/\\:$"
    for c in chars:
        assert c not in stubber.flat_fwid, "flat_fwid must not contain '{}'".format(c)
