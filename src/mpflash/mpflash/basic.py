from .vendored import pydfu as pydfu
from argparse import Namespace
from pathlib import Path


def main():
    print("Hello, DFU!")
    dfu_file = Path("/home/jos/projects/micropython/ports/stm32/build-PYBV11/firmware.dfu")

    print("List ANY DFU devices...")
    try:
        pydfu.list_dfu_devices()
    except ValueError as e:
        print(f"Insuffient permissions to access usb DFU devices: {e}")
        exit(1)

    kwargs = {"idVendor": 0x0483, "idProduct": 0xDF11}
    print("List SPECIFIED DFU devices...")
    pydfu.list_dfu_devices(**kwargs)

    # Needs to be a list of serial ports
    print("Inititialize pydfu...")
    pydfu.init(**kwargs)

    # print("Mass erase...")
    # pydfu.mass_erase()

    print("Read DFU file...")
    elements = pydfu.read_dfu_file(dfu_file)
    if not elements:
        print("No data in dfu file")
        return
    print("Writing memory...")
    pydfu.write_elements(elements, False, progress=pydfu.cli_progress)

    print("Exiting DFU...")
    pydfu.exit_dfu()


if __name__ == "__main__":
    main()
