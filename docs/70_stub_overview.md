
# Overview of Stubs

Initially I also stored all the generated subs in the same repo. That turned out to be a bit of a hassle and since then I have moved [all the stubs][all-stubs] to the [micropython-stubs][] repo

Below are the most relevant stub sources referenced in this project.

## Firmware and libraries 

### MicroPython firmware and frozen modules _[MIT]_

https://github.com/micropython/micropython

https://github.com/micropython/micropython-lib

### Pycopy firmware and frozen modules _[MIT]_

https://github.com/pfalcon/pycopy

https://github.com/pfalcon/pycopy-lib

### LoBoris ESP32 firmware and frozen modules _[MIT, Apache 2]_

https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo


## Included custom stubs 

| Github repo                | Contributions                                                           | License |
|----------------------------|-------------------------------------------------------------------------|---------|
| pfalcon/micropython-lib    | CPython backports                                            | MIT |
| dastultz/micropython-pyb   | a pyb.py file for use with IDEs in developing a project for the Pyboard | Apache 2|

### Stub source: MicroPython-lib > CPython backports _[MIT, Python]_

While micropython-lib focuses on MicroPython, sometimes it may be beneficial to run MicroPython code using CPython, e.g. to use code coverage, debugging, etc. tools available for it. To facilitate such usage, micropython-lib also provides re-implementations ("backports") of MicroPython modules which run on CPython. 
https://github.com/pfalcon/micropython-lib#cpython-backports

### micropython_pyb _[Apache 2]_

This project provides a pyb.py file for use with IDEs in developing a project for the Pyboard.
https://github.com/dastultz/micropython-pyb


[stubs-repo]:   https://github.com/Josverl/micropython-stubs
[stubs-repo2]:  https://github.com/BradenM/micropy-stubs
[micropython-stubber]: https://github.com/Josverl/micropython-stubber
[micropython-stubs]: https://github.com/Josverl/micropython-stubs#micropython-stubs
[micropy-cli]: https://github.com/BradenM/micropy-cli
[using-the-stubs]: https://github.com/Josverl/micropython-stubs#using-the-stubs
[demo]:         docs/img/demo.gif	"demo of writing code using the stubs"
[stub processing order]: docs/img/stuborder_pylance.png	"recommended stub processing order"
[naming-convention]: #naming-convention-and-stub-folder-structure
[all-stubs]: https://github.com/Josverl/micropython-stubs/blob/master/firmwares.md
[micropython]: https://github.com/micropython/micropython
[micropython-lib]:  https://github.com/micropython/micropython-lib
[pycopy]: https://github.com/pfalcon/pycopy
[pycopy-lib]: https://github.com/pfalcon/pycopy-lib
[createstubs-flow]: docs/img/createstubs-flow.png
[symlink]: #create-a-symbolic-link

