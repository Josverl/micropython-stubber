"""Info to support mounting and unmounting of UF2 drives on linux and macos"""


class UF2Disk:
    """Info to support mounting and unmounting of UF2 drives on linux"""

    device_path: str
    label: str
    mountpoint: str

    def __repr__(self):
        return repr(self.__dict__)
