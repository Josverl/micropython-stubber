# CPython and Frozen modules 

## Frozen Modules 

It is common for Firmwares to include a few (or many) python modules as 'frozen' modules. 
'Freezing' modules is a way to pre-process .py modules so they're 'baked-in' to MicroPython' s firmware and use less memory. Once the code is frozen it can be quickly loaded and interpreted by MicroPython without as much memory and processing time.

Most OSS firmwares store these frozen modules as part of their repository, which allows us to: 

1. Download the *.py from the (github) repo using `git clone` or a direct download 

2. Extract and store the 'unfrozen' modules (ie the *.py files) in a <Firmware>_Frozen folder.
   if there are different port / boards or releases defined , there may be multiple folders such as: 

   * stubs/micropython_1_12_frozen

     * /esp32

       * /GENERIC
       * /RELEASE
       * /TINYPICO

     * /stm32

       * /GENERIC
       * /PYBD_SF2

       

3. generate typeshed stubs of these files. (the .pyi files will be stored alongside the .py files)

4. Include/use them in the configuration 

ref: https://learn.adafruit.com/micropython-basics-loading-modules/frozen-modules

## Collect Frozen Stubs (micropython) 

This is run daily though the github action workflow : get-all-frozen in the micropython-stubs repo.

If you want to run this manually 
- Check out repos side-by-side:
    - micropython-stubs
    - micropython-stubber
    - micropython
    - micropython-lib

- link repos using all_stubs symlink
- checkout tag / version in the micropython folder  
  (for most accurate results should checkout micropython-lib for the same date)
- run `src/get-frozen.py`
- run `src/update-stubs.py`

- create a PR for changes to the stubs repo 

## Postprocessing 

You can run postprocessing for all stubs by running either of the two scripts.
There is an optional parameter to specify the location of the stub folder. The default path is `./all_stubs`

Powershell:  
``` powershell
./scripts/updates_stubs.ps1 [-path ./mystubs]

```
or python  
``` bash
python ./src/update_stubs.py [./mystubs]
```

This will generate or update the `.pyi` stubs for all new (and existing) stubs in the `./all_stubs` or specified folder.

From version '1.3.8' the  `.pyi` stubs are generated using `stubgen`, before that the `make_stub_files.py` script was used.

Stubgen is run on each 'collected stub folder' (that contains a `modules.json` manifest) using the options : `--ignore-errors --include-private` and the resulting `.pyi` files are stored in the same folder (`foo.py` and `foo.pyi` are stored next to each other).

In some cases `stubgen` detects duplicate modules in a 'collected stub folder', and subsequently does not generate any stubs for any `.py` module or script.
then __Plan B__ is to run stubgen for each separate `*.py` file in that folder. THis is significantly slower and according to the stubgen documentation the resulting stubs may of lesser quality, but that is better than no stubs at all.

**Note**: In several cases `stubgen` creates folders in inappropriate locations (reason undetermined), which would cause issues when re-running `stubgen` at a later time.
to compensate for this behaviour the known-incorrect .pyi files are removed before and after stubgen is run [see: `cleanup(modules_folder)` in `utils.py`](https://github.com/Josverl/micropython-stubber/blob/main/src/utils.py#L40-L66)


[stubs-repo]:   https://github.com/Josverl/micropython-stubs
[stubs-repo2]:  https://github.com/BradenM/micropy-stubs
[micropython-stubber]: https://github.com/Josverl/micropython-stubber
[micropython-stubs]: https://github.com/Josverl/micropython-stubs#micropython-stubs
[micropy-cli]: https://github.com/BradenM/micropy-cli
[using-the-stubs]: https://github.com/Josverl/micropython-stubs#using-the-stubs
[demo]:         docs/img/demo.gif	"demo of writing code using the stubs"
[stub processing order]: docs/img/stuborder_pylance.png	"recommended stub processing order"
[naming-convention]: #naming-convention-and-stub-folder-structure
[all-stubs]: https://github.com/Josverl/micropython-stubs/blob/main/firmwares.md
[micropython]: https://github.com/micropython/micropython
[micropython-lib]:  https://github.com/micropython/micropython-lib
[pycopy]: https://github.com/pfalcon/pycopy
[pycopy-lib]: https://github.com/pfalcon/pycopy-lib
[createstubs-flow]: docs/img/createstubs-flow.png
[symlink]: #create-a-symbolic-link

