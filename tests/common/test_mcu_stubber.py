import warnings
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock, call

import pytest
from mpflash.mpremoteboard import MPRemoteBoard

from stubber.bulk.mcu_stubber import ESPRESSIF_USB_SERIAL_JTAG, Variant, hard_reset, run_createstubs, use_mount_vfs


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


def test_hard_reset_uses_explicit_reset_command() -> None:
    board = Mock(spec=MPRemoteBoard)
    board.run_command.return_value = (0, [])
    board.connected = True

    assert hard_reset.retry_with(wait=lambda _: 0)(board) is True

    board.run_command.assert_called_once_with(["reset"], timeout=5)
    assert board.connected is False


def test_run_createstubs_resets_then_preserves_command_state(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("stubber.bulk.mcu_stubber.reset_before", True)
    board = Mock(spec=MPRemoteBoard)
    board.serialport = "COM7"
    board.description = "Test board"
    board.port = "rp2"
    board.run_command.side_effect = [(0, []), (0, ["done"])]

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = run_createstubs.retry_with(wait=lambda _: 0)(tmp_path, board, Variant.db)

    assert result == (0, ["done"])
    assert board.run_command.call_args_list == [
        call("reset", timeout=5),
        call(["mount", str(tmp_path), "exec", "import createstubs_db"], timeout=360),
    ]
    board.wait_for_restart.assert_called_once_with()
    assert not [warning for warning in caught if issubclass(warning.category, DeprecationWarning)]
