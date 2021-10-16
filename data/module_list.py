"""
generate the list of modules that should be attempted to stub
for this : 
    - combine the modules from the different texts files
    - split the lines into individual module names
    - combine them in one set
    - remove the ones than cannot be stubbed
    - remove test modules, ending in `_test`
    - todo: remove the frozen modules from this list
"""

from pathlib import Path
from typing import Set


def read_modules(path: Path = None) -> Set:
    """
    read text files with modules per firmware.
    each contains the output of help("modules")
        lines starting with # are comments.
            split the other lines at whitespace seperator,
            and add each module to a set
    """
    path = Path(path or "./data")
    all_modules = set()
    for file in path.glob("*.txt"):
        print("processing:", file)
        with file.open("r") as f:
            line = f.readline()
            while line:
                if len(line) > 1 and line[0] != "#":

                    file_mods = line.split()
                    # print(line[0:-1])
                    # print( set(file_mods))
                    # remove modules ending in _test
                    file_mods = [m for m in file_mods if not m.endswith("_test")]
                    all_modules = set(all_modules | set(file_mods))
                # next
                line = f.readline()

    #     print("-" * 40)

    # print(">" * 40)

    return all_modules


def wrapped(modules: Set) -> str:
    "wrap code line at spaces"
    long_line = str(modules)
    _wrapped = "        self.modules = "
    IDENT = len(_wrapped)
    MAX_WIDTH = 135

    # find seperator
    while len(long_line) > MAX_WIDTH:
        p1 = long_line.find("', ", MAX_WIDTH)
        # drop space
        p1 += 3
        short = long_line[0 : p1 - 1]
        _wrapped += short + "\n" + " " * IDENT
        long_line = long_line[p1 - 1 :]
    _wrapped += long_line
    return _wrapped


def main():
    """
    helper script
    generate a few lines of code with all modules to be stubbed by createstubs
    """
    #######################################################################
    # the exceptions
    #######################################################################
    mods_problematic = set(
        [
            "upysh",
            "webrepl_setup",
            "http_client",
            "http_client_ssl",
            "http_server",
            "http_server_ssl",
        ]
    )
    mods_excluded = set(
        [
            "__main__",
            "_main",
            "_boot",
            "webrepl",
            "_webrepl",
            "port_diag",
            "example_sub_led",
            "example_pub_button",
        ]
    )

    all_modules = read_modules()
    modules_to_stub = sorted(all_modules - set(mods_excluded | mods_problematic))

    # remove pycom MQTT* from defaults
    modules_to_stub = sorted({m for m in modules_to_stub if not m.startswith("MQTT")})

    print("modules to stub :", len(modules_to_stub))
    print(wrapped(modules_to_stub))


if __name__ == "__main__":
    main()
