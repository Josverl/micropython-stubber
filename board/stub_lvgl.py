import sys
from createstubs import *
import lvgl


def main():
    print("stubber version :", stubber_version)
    try:
        logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.DEBUG)
    except NameError:
        pass
    # stubber = Stubber(path=read_path())
    # Specify a firmware name & version
    fw_id = "lvgl-{0}_{1}_{2}-{3}-{4}".format(
        lvgl.version_major(),
        lvgl.version_minor(),
        lvgl.version_patch(),
        lvgl.version_info(),
        sys.platform,
    )
    stubber = Stubber(firmware_id=fw_id)
    stubber = Stubber(path="/sd")
    stubber.clean()
    # # Option: Add your own modules
    # # stubber.add_modules(['bluetooth','GPS'])

    stubber.modules = ["lvgl", "lodepng", "rtch"]
    stubber.create_all_stubs()
    stubber.report()


if __name__ == "__main__" or isMicroPython():
    main()
