from typing import List

import jsons
import pytest
from mpflash.common import filtered_comports
from serial.tools.list_ports_common import ListPortInfo

pytestmark = [pytest.mark.mpflash]


# output of:
# import jsons
# import serial.tools.list_ports as list_ports
# comports = jsons.dumps(list_ports.comports()).replace('{"description":','\n{"description":')
# print(comports)

windows_ports_json = """
[
{"description": "USB Serial Device (COM8)", "device": "COM8", "hwid": "USB VID:PID=F055:9802 SER=7A674ABB5336464E4E202020FF130722 LOCATION=1-5:x.0", "interface": null, "location": "1-5:x.0", "manufacturer": "Microsoft", "name": "COM8", "pid": 38914, "product": null, "serial_number": "7A674ABB5336464E4E202020FF130722", "vid": 61525}, 
{"description": "Standard Serial over Bluetooth link (COM15)", "device": "COM15", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_VID&00010067_PID&094E\\\\7&4CE5CE3&0&745C4B893934_C00000000", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM15", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description": "Standard Serial over Bluetooth link (COM13)", "device": "COM13", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_VID&00010067_PID&094E\\\\7&4CE5CE3&0&50C275017686_C00000000", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM13", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description": "Standard Serial over Bluetooth link (COM17)", "device": "COM17", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0000\\\\7&4CE5CE3&0&000000000000_00000000", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM17", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description": "Standard Serial over Bluetooth link (COM5)", "device": "COM5", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0000\\\\7&4CE5CE3&0&000000000000_00000001", "interface": null, "location": null, "manufacturer": "Microsoft", "name": "COM5", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description": "USB Serial Device (COM9)", "device": "COM9", "hwid": "USB VID:PID=2341:025E SER=50159300709F8C1C LOCATION=1-6.2:x.0", "interface": null, "location": "1-6.2:x.0", "manufacturer": "Microsoft", "name": "COM9", "pid": 606, "product": null, "serial_number": "50159300709F8C1C", "vid": 9025}]
"""

# below is genereated by AI
# TODO : replace by a real data to test realisticly
macos_ports_json = """
[
{"description" : "n/a", "device": "/dev/cu.debug-console", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "cu.debug-console", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description" : "n/a", "device": "/dev/tty.debug-console", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "cu.debug-console", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description" : "n/a", "device": "/dev/cu.Bluetooth-Incoming-Port", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "cu.Bluetooth-Incoming-Port", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description" : "n/a", "device": "/dev/cu.Hermes", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "cu.Hermes", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description" : "n/a", "device": "/dev/tty.Hermes", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "cu.Hermes", "pid": null, "product": null, "serial_number": null, "vid": null}, 
{"description" : "Espressif Device", "device": "/dev/cu.usbmodem2101", "hwid": "USB VID:PID=303A:4001 SER=983daee912f0cb3f LOCATION=2-1", "interface": null, "location": "2-1", "manufacturer": "Espressif Systems", "name": "cu.usbmodem2101", "pid": 16385, "product": "Espressif Device", "serial_number": "983daee912f0cb3f", "vid": 12346}, 
{"description" : "Espressif Device", "device": "/dev/cu.usbmodem1101", "hwid": "USB VID:PID=303A:4001 SER=68b6b3210350cb3f LOCATION=1-1", "interface": null, "location": "1-1", "manufacturer": "Espressif Systems", "name": "cu.usbmodem1101", "pid": 16385, "product": "Espressif Device", "serial_number": "68b6b3210350cb3f", "vid": 12346}, 
{"description" : "CP2102N USB to UART Bridge Controller", "device": "/dev/cu.usbserial-10", "hwid": "USB VID:PID=10C4:EA60 SER=c267ea1cda23ed118f088ae8f9a97352 LOCATION=0-1", "interface": null, "location": "0-1", "manufacturer": "Silicon Labs", "name": "cu.usbserial-10", "pid": 60000, "product": "CP2102N USB to UART Bridge Controller", "serial_number": "c267ea1cda23ed118f088ae8f9a97352", "vid": 4292}]
"""
# {"description": "Hermes", "device": "/dev/cu.Hermes", "hwid": "BTHENUM\\\\{00001101-0000-1000-8000-00805F9B34FB}_VID&00010067_PID&094E\\\\7&4CE5CE3&0&50C275017686_C00000000", "interface": null, "location": null, "manufacturer": "Apple", "name": "Hermes", "pid": null, "product": null, "serial_number": null, "vid": null},
# {"description": "debug-console", "device": "/dev/cu.debug-console", "hwid": "USB VID:PID=F055:9802 SER=7A674ABB5336464E4E202020FF130722 LOCATION=1-5:x.0", "interface": null, "location": "1-5:x.0", "manufacturer": "Apple", "name": "debug-console", "pid": 38914, "product": null, "serial_number": "7A674ABB5336464E4E202020FF130722", "vid": 61525}


ci_linux_ports_json = """
 [
{"description": "n/a", "device": "/dev/ttyS0", "device_path": "/sys/devices/pnp0/00:03/00:03:0/00:03:0.0", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS0", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS1", "device_path": "/sys/devices/pnp0/00:04/00:04:0/00:04:0.0", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS1", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS2", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.2", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS2", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS3", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.3", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS3", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS4", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.4", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS4", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS5", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.5", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS5", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS6", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.6", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS6", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS7", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.7", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS7", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS8", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.8", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS8", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS9", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.9", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS9", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS10", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.10", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS10", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS11", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.11", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS11", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS12", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.12", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS12", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS13", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.13", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS13", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS14", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.14", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS14", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS15", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.15", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS15", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS16", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.16", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS16", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS17", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.17", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS17", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS18", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.18", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS18", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS19", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.19", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS19", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS20", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.20", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS20", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS21", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.21", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS21", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS22", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.22", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS22", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS23", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.23", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS23", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS24", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.24", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS24", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS25", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.25", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS25", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS26", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.26", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS26", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS27", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.27", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS27", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS28", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.28", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS28", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS29", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.29", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS29", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS30", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.30", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS30", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}, 
{"description": "n/a", "device": "/dev/ttyS31", "device_path": "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.31", "hwid": "n/a", "interface": null, "location": null, "manufacturer": null, "name": "ttyS31", "pid": null, "product": null, "serial_number": null, "subsystem": "serial-base", "usb_device_path": null, "usb_interface_path": null, "vid": null}
]
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
@pytest.mark.win32
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
@pytest.mark.linux
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


@pytest.mark.linux
def test_skip_bogus_comports_linux(mocker):
    linux_ports = [
        ListPortInfo(device="/dev/tty001", skip_link_detection=True),
        ListPortInfo(device="/dev/tty002", skip_link_detection=True),
    ]

    def platform_system():
        return "Linux"

    mocker.patch("mpflash.common.platform.system", platform_system)

    linux_ports[0].location = f"1-1.1:x.0"
    mocker.patch("mpflash.common.list_ports.comports", return_value=linux_ports)
    result = filtered_comports(include=["*"], ignore=[], bluetooth=False)
    devices = [port.device for port in result]
    assert len(devices) == 1


@pytest.mark.parametrize(
    "mock_os,exp, ser_port, mock_ports",
    [
        ("Darwin", 0, "/dev/tty.debug-console", macos_ports_json),
        ("Darwin", 0, "/dev/cu.debug-console", macos_ports_json),
        ("Darwin", 0, "/dev/cu.Hermes", macos_ports_json),
        ("Darwin", 0, "/dev/tty.Hermes", macos_ports_json),
        ("Darwin", 0, "/dev/cu.Bluetooth-Incoming-Port", macos_ports_json),
        ("Darwin", 1, "/dev/cu.usbmodem2101", macos_ports_json),
        ("Darwin", 1, "/dev/cu.usbmodem1101", macos_ports_json),
        ("Darwin", 1, "/dev/cu.usbserial-10", macos_ports_json),
        # BT ports are ignored on Windows
        ("Windows", 0, "COM15", windows_ports_json),
        ("Windows", 0, "COM13", windows_ports_json),
        ("Windows", 0, "COM17", windows_ports_json),
        ("Windows", 0, "COM5", windows_ports_json),
        ("Windows", 1, "COM8", windows_ports_json),
        ("Windows", 1, "COM9", windows_ports_json),
    ],
)
def test_default_ignore_comports(mock_os: str, exp: int, ser_port: str, mocker, mock_ports: str):
    """Test that the default ignore list is used
    all of the devices on the list should be ignored by default
    """
    platform_ports = jsons.loads(mock_ports, List[ListPortInfo])
    devices = [port.device for port in platform_ports]
    if ser_port not in devices:
        pytest.skip(f"{ser_port} not in {devices}")
    mocker.patch("mpflash.common.list_ports.comports", return_value=platform_ports)
    mocker.patch("mpflash.common.platform.system", return_value=mock_os)
    result = filtered_comports()  # include=include, ignore=ignore, bluetooth=bluetooth)
    devices = [port.device for port in result]
    if exp:
        assert ser_port in devices, f"{ser_port} not in {devices}"
    else:
        assert ser_port not in devices, f"{ser_port} in {devices}"
