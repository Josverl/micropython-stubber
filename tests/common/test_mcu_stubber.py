from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import pytest
from mpflash.mpremoteboard import MPRemoteBoard

from stubber.bulk.mcu_stubber import ESPRESSIF_USB_SERIAL_JTAG, use_mount_vfs


@pytest.mark.parametrize(
    ("port", "cpu", "serialport", "usb_id", "mount_vfs", "safe_mount", "expected"),
    [
        ("esp32", "ESP32-C3", "COM7", ESPRESSIF_USB_SERIAL_JTAG, True, True, False),
        ("esp32", "ESP32-C3", "COM7", ESPRESSIF_USB_SERIAL_JTAG, True, False, True),
        ("esp32", "ESP32-C3", "COM7", ESPRESSIF_USB_SERIAL_JTAG, False, True, False),
        ("esp32", "ESP32-C6", "/dev/ttyACM0", (0, 0), True, True, False),
        ("esp32", "ESP32-C3", "/dev/ttyUSB0", (0, 0), True, True, True),
        ("esp32", "ESP32-S3", "/dev/ttyACM0", (0, 0), True, True, True),
        ("esp32", "ESP32-C3", "COM7", (0x10C4, 0xEA60), True, True, True),
        ("rp2", "RP2350", "COM7", ESPRESSIF_USB_SERIAL_JTAG, True, True, False),
    ],
)
def test_use_mount_vfs(
    monkeypatch: pytest.MonkeyPatch,
    port: str,
    cpu: str,
    serialport: str,
    usb_id: tuple[int, int],
    mount_vfs: bool,
    safe_mount: bool,
    expected: bool,
) -> None:
    monkeypatch.setattr("stubber.bulk.mcu_stubber.serial.tools.list_ports.comports", lambda: [])
    board = cast(
        MPRemoteBoard,
        SimpleNamespace(port=port, cpu=cpu, serialport=serialport, vid=usb_id[0], pid=usb_id[1]),
    )

    assert use_mount_vfs(board, mount_vfs, safe_mount) is expected


def test_use_mount_vfs_resolves_linux_usb_id(monkeypatch: pytest.MonkeyPatch) -> None:
    board = cast(
        MPRemoteBoard,
        SimpleNamespace(port="", cpu="", serialport="/dev/ttyACM0", vid=0, pid=0),
    )
    port_info = Mock(device="/dev/ttyACM0", vid=ESPRESSIF_USB_SERIAL_JTAG[0], pid=ESPRESSIF_USB_SERIAL_JTAG[1])
    monkeypatch.setattr("stubber.bulk.mcu_stubber.serial.tools.list_ports.comports", lambda: [port_info])

    assert use_mount_vfs(board, mount_vfs=True, safe_mount=True) is False
