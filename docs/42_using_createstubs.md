# Using Createstub

## Use MIP to install createstubs on a MCU board

It is possible to install the firmware stubber ( createsubs.py or one of its variants) on a MicroPython board. 
This allows you to create the firmware stubs on the board itself, and then copy them to your PC.

mip is a package manager for MicroPython. It is a command line tool that allows you to install packages on a MicroPython board.
In this case it is best to use `mpremote` that has a built-in `mip` command.

Make sure you have the latest version of `mpremote` installed.
```bash
pip install mpremote
```

## Install createstubs

Connect your board to your PC and run the following command:

`mpremote mip install github:josverl/micropython-stubber`
```log
Install github:josverl/micropython-stubber
Installing github:josverl/micropython-stubber/package.json to /lib
Installing: /lib/createstubs.py
Installing: /lib/createstubs_db.py
Installing: /lib/createstubs_mem.py
Installing: /lib/modules.txt
Done
```

## run createstubs
A simple way to run createstubs is to use the `mpremote mount` command to allow the MCU board to directly access the PC's file system.
Then you can run the createstubs.py script directly from the MCU board with outh the need to copy the created files back to the PC.

Navigate to the folder where you want to create the stubs and run the following command:
`mpremote mount . exec "import createstubs"` or 
`mpremote mount . exec "import createstubs_mem"` or 


## low memory devices 

If you have a low memory board, then you can install the cross-compiled variants to reduce the memory footprint durign compilation on the board:

| MicroPython release | .mpy version | command |
|---------------------|--------------|---------|
| v1.19 and up        | 6            | `mpremote mip install github:josverl/micropython-stubber/mpy_v6.json` |
| v1.12 - v1.18       | 5            | `mpremote mip install github:josverl/micropython-stubber/mpy_v5.json` |

```log	
Install github:josverl/micropython-stubber/mpy_v6.json
Installing github:josverl/micropython-stubber/mpy_v6.json to /lib
Installing: /lib/createstubs_mpy.mpy
Installing: /lib/createstubs_db_mpy.mpy
Installing: /lib/createstubs_mem_mpy.mpy
Installing: /lib/modulelist.txt
```
**Note:** The names of the scripts have changed to createstubs_mpy.py, createstubs_db_mpy.py and createstubs_mem_mpy.py

Navigate to the folder where you want to create the stubs and run the following command:
`mpremote mount . exec "import createstubs_db_mpy"` or 
`mpremote mount . exec "import createstubs_mem_mpy"` 

## format the stubs and generate the .pyi files

The stubs are generated in a folder called `stubs` in the current folder.
You can use stubber to run the  `stubgen` tool to format the stubs and generate the .pyi files.

For example:
```bash
stubber stub -s ./stubs/micropython-v1_19_1-rp2
```

see [MicroPython Package management](https://docs.micropython.org/en/latest/reference/packages.html?highlight=mip#package-management)