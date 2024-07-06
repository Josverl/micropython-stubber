from typing import List

import jsons
import pytest
from serial.tools.list_ports_common import ListPortInfo

from mpflash.common import filtered_comports

pytestmark = [pytest.mark.mpflash]


# output of txt = jsons.dumps(list_ports.comports())
windows_ports_json = """
[{"description": "USB Serial Device (COM8)", "device": "COM8", "hwid": "USB VID:PID=F055:9802 SER=7A674ABB5336464E4E202020FF130722 LOCATION=1-5:x.0", "interface": null, "location": "1-5:x.0", "manufacturer": "Microsoft", "name": "COM8", "pid": 38914, "product": null, "serial_number": "7A674ABB5336464E4E202020FF130722", "vid": 61525}, {"description": "Standard Serial over Bluetooth link (COM15)", "device": "COM15", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_VID&00010067_PID&094E\\\\7&4CE5CE3&0&745C4B893934_C00000000", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM15", "pid": null, "product": null, "serial_number": null, "vid": null}, {"description": "Standard Serial over Bluetooth link (COM13)", "device": "COM13", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_VID&00010067_PID&094E\\\\7&4CE5CE3&0&50C275017686_C00000000", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM13", "pid": null, "product": null, "serial_number": null, "vid": null}, {"description": "Standard Serial over Bluetooth link (COM17)", "device": "COM17", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0000\\\\7&4CE5CE3&0&000000000000_00000000", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM17", "pid": null, "product": null, "serial_number": null, "vid": null}, {"description": "Standard Serial over Bluetooth link (COM5)", "device": "COM5", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0000\\\\7&4CE5CE3&0&000000000000_00000001", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM5", "pid": null, "product": null, "serial_number": null, "vid": null}, {"description": "USB Serial Device (COM9)", "device": "COM9", "hwid": "USB VID:PID=2341:025E SER=50159300709F8C1C LOCATION=1-6.2:x.0", "interface": null, "location": "1-6.2:x.0", "manufacturer": "Microsoft", "name": "COM9", "pid": 606, "product": null, "serial_number": "50159300709F8C1C", "vid": 9025}]
"""


@pytest.mark.parametrize(
    "id, include, ignore, bluetooth, expected",
    [
        ("00-default", ["*"], [], False, ["COM8", "COM9"]),
        ("10-ignore", ["*"], ["COM8"], False, ["COM9"]),
        ("11-ignore", ["*"], ["COM9"], False, ["COM8"]),
        #
        ("20-include", ["COM8"], [], False, ["COM8"]),
        ("21-include", ["COM9"], [], False, ["COM9"]),
        ("25-include", ["COM?"], [], False, ["COM8", "COM9"]),
        #
        ("30-include-over", ["COM8"], ["COM*"], False, ["COM8"]),
        ("31-include-over", ["COM8"], ["*"], False, ["COM8"]),
        ("32-include-over", ["COM9"], ["COM*"], False, ["COM9"]),
        ("33-include-over", ["COM9"], ["*"], False, ["COM9"]),
        ("35-include-over", ["COM?"], ["COM*"], False, ["COM8", "COM9"]),
        ("36-include-over", ["COM8", "COM9"], ["COM*"], False, ["COM8", "COM9"]),
    ],
)
def test_filtered_comports_windows(id, include, ignore, bluetooth, expected, mocker):
    windows_ports = jsons.loads(windows_ports_json, List[ListPortInfo])
    mocker.patch("mpflash.common.list_ports.comports", return_value=windows_ports)
    result = filtered_comports(include=include, ignore=ignore, bluetooth=bluetooth)
    devices = [port.device for port in result]
    assert all([(e in devices) for e in expected]), f"{expected} not in {devices}"
    assert all([(d in expected) for d in devices]), f"{devices} not in {expected}"


@pytest.mark.parametrize(
    "id, include, ignore, bluetooth, expected",
    [
        ("00-default", ["*"], [], False, ["/dev/tty001", "/dev/tty002"]),
        ("10-ignore", ["*"], ["/dev/tty001"], False, ["/dev/tty002"]),
    ],
)
def test_filtered_comports_linux(id, include, ignore, bluetooth, expected, mocker):
    linux_ports = [
        ListPortInfo(device="/dev/tty001", skip_link_detection=True),
        ListPortInfo(device="/dev/tty002", skip_link_detection=True),
    ]
    n = 0
    for port in linux_ports:
        port.location = f"1-1.{n}:x.0"
        n += 1
    mocker.patch("mpflash.common.list_ports.comports", return_value=linux_ports)
    result = filtered_comports(include=include, ignore=ignore, bluetooth=bluetooth)
    devices = [port.device for port in result]
    assert all([(e in devices) for e in expected])
    assert all([(d in expected) for d in devices])


def test_skip_bogus_comports_linux(mocker):
    linux_ports = [
        ListPortInfo(device="/dev/tty001", skip_link_detection=True),
        ListPortInfo(device="/dev/tty002", skip_link_detection=True),
    ]
    linux_ports[0].location = f"1-1.1:x.0"
    mocker.patch("mpflash.common.list_ports.comports", return_value=linux_ports)
    result = filtered_comports(include=["*"], ignore=[], bluetooth=False)
    devices = [port.device for port in result]
    assert len(devices) == 1
