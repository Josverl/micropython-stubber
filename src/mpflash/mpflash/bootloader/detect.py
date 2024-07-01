""" Detect if a board is in bootloader mode 
"""

import os

from mpflash.common import PORT_FWTYPES
from mpflash.flash.uf2 import waitfor_uf2
from mpflash.logger import log
from mpflash.mpremoteboard import MPRemoteBoard


def in_bootloader(mcu: MPRemoteBoard) -> bool:
    """Check if the board is in bootloader mode"""
    if ".uf2" in PORT_FWTYPES[mcu.port]:
        return in_uf2_bootloader(mcu.port.upper())
    elif mcu.port in ["stm32"]:
        return in_stm32_bootloader()
    elif mcu.port in ["esp32", "esp8266"]:
        log.debug("esp32/esp8266 does not have a bootloader mode, Assume OK to flash")
        return True

    log.error(f"Bootloader mode not supported on {mcu.board} on {mcu.serialport}")
    return False


def in_uf2_bootloader(board_id: str) -> bool:
    """
    Check if the board is in UF2 bootloader mode.

    :param board_id: The board ID to check for (SAMD or RP2)
    """
    return bool(waitfor_uf2(board_id=board_id))


def in_stm32_bootloader() -> bool:
    """Check if the board is in STM32 bootloader mode"""
    if os.name == "nt":
        driver_installed, status = check_for_stm32_bootloader_device()
        if not driver_installed:
            log.warning("STM32  BOOTLOADER device not found.")
            return False
        print()
        if status != "OK":
            log.warning(f"STM32 BOOTLOADER device found, Device status: {status}")
            log.error("Please use Zadig to install a WinUSB (libusb)  driver.\nhttps://github.com/pbatard/libwdi/wiki/Zadig")
            return False
    return check_dfu_devices()


def check_dfu_devices():
    """Check if there are any DFU devices connected"""
    # JIT import
    from mpflash.flash.stm32_dfu import dfu_init
    from mpflash.vendor.pydfu import get_dfu_devices

    # need to init on windows to get the right usb backend
    dfu_init()
    devices = get_dfu_devices()
    return len(devices) > 0


def check_for_stm32_bootloader_device():
    import win32com.client

    # Windows only
    # Create a WMI interface object
    wmi = win32com.client.GetObject("winmgmts:")

    # Query for USB devices
    for usb_device in wmi.InstancesOf("Win32_PnPEntity"):
        try:
            # Check if device name or description contains "STM32 BOOTLOADER"
            if str(usb_device.Name).strip() in {
                "STM32  BOOTLOADER",
                "STM BOOTLOADER",
            }:
                # Just the first match is enough
                return True, usb_device.Status
        except Exception:
            pass
    # If no matching device was found
    return False, "Not found."
