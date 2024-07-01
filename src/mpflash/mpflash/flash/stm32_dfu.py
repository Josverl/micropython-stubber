import platform
from pathlib import Path
from typing import Optional

from loguru import logger as log

from mpflash.mpremoteboard import MPRemoteBoard


def init_libusb_windows() -> bool:
    """
    Initializes the libusb backend on Windows.

    Returns:
        bool: True if the initialization is successful, False otherwise.
    """
    import libusb  # type: ignore
    import usb.backend.libusb1 as libusb1

    arch = "x64" if platform.architecture()[0] == "64bit" else "x86"
    libusb1_dll = Path(libusb.__file__).parent / f"_platform\\_windows\\{arch}\\libusb-1.0.dll"
    if not libusb1_dll.exists():
        raise FileNotFoundError(f"libusb1.dll not found at {libusb1_dll}")
    backend = libusb1.get_backend(find_library=lambda x: libusb1_dll.as_posix())
    return backend is not None


try:
    from ..vendor import pydfu as pydfu
except ImportError:
    pydfu = None


def dfu_init():
    """
    Initializes the DFU (Device Firmware Upgrade) process.
    """
    if not pydfu:
        log.error("pydfu not found")
        return None
    if platform.system() == "Windows":
        log.debug("Initializing libusb backend on Windows...")
        init_libusb_windows()


def flash_stm32_dfu(
    mcu: MPRemoteBoard,
    fw_file: Path,
    *,
    erase: bool = True,
) -> Optional[MPRemoteBoard]:
    """
    Flashes the STM32 microcontroller using DFU (Device Firmware Upgrade).

    Args:
        mcu (MPRemoteBoard): The remote board to flash.
        fw_file (Path): The path to the firmware file (.dfu).
        erase (bool, optional): Whether to erase the memory before flashing. Defaults to True.

    Returns:
        Optional[MPRemoteBoard]: The flashed remote board if successful, None otherwise.
    """
    log.info("Using pydfu to flash STM32 boards")

    if not pydfu:
        log.error("pydfu not found, please install it with 'pip install pydfu' if supported")
        return None

    if not fw_file.exists():
        log.error(f"File {fw_file} not found")
        return None

    if fw_file.suffix != ".dfu":
        log.error(f"File {fw_file} is not a .dfu file")
        return None

    kwargs = {"idVendor": 0x0483, "idProduct": 0xDF11}
    log.debug("List SPECIFIED DFU devices...")
    try:
        pydfu.list_dfu_devices(**kwargs)
    except ValueError as e:
        log.error(f"Insuffient permissions to access usb DFU devices: {e}")
        return None

    # Needs to be a list of serial ports
    log.debug("Inititialize pydfu...")
    pydfu.init(**kwargs)

    if erase:
        log.info("Mass erase...")
        pydfu.mass_erase()

    log.debug("Read DFU file...")
    elements = pydfu.read_dfu_file(fw_file)
    if not elements:
        print("No data in dfu file")
        return
    log.info("Writing memory...")
    pydfu.write_elements(elements, False, progress=pydfu.cli_progress)

    log.debug("Exiting DFU...")
    pydfu.exit_dfu()
    log.success("Done flashing, resetting the board and wait for it to restart")
    return mcu
