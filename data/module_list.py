"""
generate the list of modules that should be attempted to stub
for this : 
    - combine the modules from the different texts files
    - split the lines into individual module names
    - combine them in one set
    - remove the ones than cannot be stubbed
    - todo: remove the frozen modules from this list
"""

from pathlib import Path
from typing import Set


def read_modules(path:Path = None)->Set:
    """
    docstring
    """
    # 
    path = Path(path or "./data")
    all_modules = set()
    for file in path.glob("*.txt"):
        print("processing:", file)
        with  file.open("r") as f:
            line = f.readline()
            while line:
                if len(line) > 1 and line[0] != "#":

                    file_mods = line.split()
                    # print(line[0:-1])
                    # print( set(file_mods))
                    all_modules = set( all_modules |  set(file_mods))
                # next
                line = f.readline()

    #     print("-" * 40)
    
    # print(">" * 40)

    return all_modules


def main():
    """
    docstring
    """

    #######################################################################
    # the exceptions
    #######################################################################
    mods_problematic = set(["upysh", "webrepl_setup", "http_client", "http_client_ssl", "http_server", "http_server_ssl"])
    mods_excluded = set(["__main__", "_boot", "webrepl", "_webrepl", "port_diag", "example_sub_led", "example_pub_button"])

    all_modules = read_modules()

    modules_to_stub = sorted(all_modules - set(mods_excluded | mods_problematic))

    print("modules to stub :", len(modules_to_stub))
    print("\nself.modules =", modules_to_stub)


if __name__ == "__main__":
    main()
