# Createstub Variants

There are multiple variants of the script available, in 3 levels of optimisation:

| variant           | full documented script | minified script (no logging)  | cross-compiled script 
|-------------------|------------------------|-------------------------------|----------------------
| full version      | createstubs.py         | createstubs_min.py            | createstubs_mpy.mpy
| memory optimized  | createstubs_mem.py     | createstubs_mem_min.py        | createstubs_mem_mpy.mpy
| restartable       | createstubs_db.py      | createstubs_db_min.py         | createstubs_db_mpy.mpy
| lvgl only         | createstubs_lvgl.py    | createstubs_lvgl_min.py       | createstubs_lvgl_mpy.mpy

all file are located in the repo in 'src/stubber/board' and included in the stubber package as stubber.board.*

In all cases the generation will take a few minutes ( 2-5 minutes) depending on the speed of the board and the number of included modules.
As the stubs are generated on the board, and as MicroPython is highly optimized to deal with the scarce resources, this unfortunately does mean that the stubs lacks parameters details. So for these you must still use the documentation provided for that firmware.

The variants can be updated / regenerated using the `stubber make-variants` command

``` bash
stubber make-variants

Usage: stubber make-variants [OPTIONS]

  Update all variants of createstubs*.py.

Options:
  -V, --version, --Version TEXT  The version of mpy-cross to use  [default: v1.19.1]
```


## board/createstubs.py

This is the core version of the script, and is fully self contained, but includes logging with requires the logging module to be avaialble on your device 
If your firmware does not include the `logging` module, you will need to upload this to your board, or use the minified version.

``` python
import createstubs
```

## createstubs_mem.py
This variant of the createstubs.py script is optimised for use on low-memory devices, and reads the list of modules from a text file, rather than including it in the source file.
as a result this requires an additional file `./modulelist.txt`,  that should be uploaded to the device.
If that cannot be found then only a single module (micropython) is stubbed.

``` python
import createstubs_mem
```

## Optimisations 
In order to run  this on low-memory devices two additional steps are recommended: 
- Minifification, using python-minifier
  to reduce overall size, and remove logging overhead.
  can be used on all devices

- Cross compilation, using mpy-cross, 
  to avoid the compilation step on the micropython device.
  The cross-compiled version can only run on specific Micropython 1.12 or newer.

### Minification

Minified versions, which requires less memory and only very basic logging. 
this removes the requirement for the logging module on the MCU.

Minifiacation helps reduce the seize of the script, and therefore of the memory usage. As a result the script becomes almost unreadable.

### Cross compilation 
This is specially suited for low memory devices such as the esp8622 

