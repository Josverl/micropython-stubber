# CPython and Frozen Modules 

## Frozen Modules 

It is common for {ref}`firmwares <firmware>` to include a few (or many) Python modules as '{ref}`frozen modules <frozen-modules>`'. 
'Freezing' modules is a way to pre-process .py modules so they're 'baked-in' to MicroPython's {ref}`firmware <firmware>` and use less memory. Once the code is frozen it can be quickly loaded and interpreted by MicroPython without as much memory and processing time.

Most OSS firmwares store these frozen modules as part of their repository, which allows us to: 

1. Download the *.py from the (GitHub) repo using `git clone` or a direct download.

2. Extract and store the 'unfrozen' modules (i.e. the *.py files) in a <Firmware>_Frozen folder.
   If there are different port / boards or releases defined, there may be multiple folders such as: 

   * stubs/micropython_1_12_frozen

     * /esp32

       * /GENERIC
       * /RELEASE
       * /TINYPICO

     * /stm32

       * /GENERIC
       * /PYBD_SF2


3. Generate typeshed stubs of these files.
   _const pre-processing:_
   As the mypy.stubgen tool is not able to incur the correct types from the MicroPython `foo = const(1)` syntax, 
   the 'to be frozen' modules are pre-processed usig a regular expression to replace the `foo = const(1)` with `foo = 1`.
   If the `.py` files contain any docstrings, they are preserved. Howecer this is uncommon as most micropython-lib modules have not docstrings to save space.

    _Addition of docstrings:_
    Then the docstring to modules, classes and methods are added by merging the docstrings based on the docstubs generated from the MicroPython documentation.
   
   Finally  the stubs are generated using the `stubgen` tool. 
   The resulting .pyi files are stored alongside the .py files


4. Include/use them in the configuration 

ref: https://learn.adafruit.com/micropython-basics-loading-modules/frozen-modules

## Collect Frozen Stubs (micropython) 

`stubber frozen` (alias: `frozen-stubs`) pulls frozen modules from the selected MicroPython version and turns them into stubs. This is the same path used in the manual build notebook.

Typical local workflow:

1. Ensure the repos folder exists (use `stubber clone --add-stubs` if you need fresh checkouts).
2. Select the firmware version/tag to work against: `stubber switch stable` (or `v1.22.2`, `preview`, custom tag).
3. Generate frozen stubs: `stubber frozen --version stable --enrich`.
4. Combine with doc-based stubs and build wheels as needed:
   - `stubber merge --port esp32 --board ESP32_GENERIC --version stable`
   - `stubber build --port esp32 --board ESP32_GENERIC --version stable`

CI in micropython-stubs automates a similar flow via the `get-all-frozen` workflow.

## Postprocessing 

You can run postprocessing for all stubs by running either of the two scripts.
There is an optional parameter to specify the location of the stub folder. The default path is `./all_stubs`


``` bash
update_stubs [./mystubs]
```

This will generate or update the `.pyi` stubs for all new (and existing) stubs in the `./all_stubs` or specified folder.

From version '1.3.8' the  `.pyi` stubs are generated using `stubgen`, before that the `make_stub_files.py` script was used.

Stubgen is run on each 'collected stub folder' (that contains a `modules.json` manifest) using the options : `--ignore-errors --include-private` and the resulting `.pyi` files are stored in the same folder (`foo.py` and `foo.pyi` are stored next to each other).

In some cases `stubgen` detects duplicate modules in a 'collected stub folder', and subsequently does not generate any stubs for any `.py` module or script.
then __Plan B__ is to run stubgen for each separate `*.py` file in that folder. While this is significantly slower and according to the stubgen documentation the resulting stubs may of lesser quality, but that is better than no stubs at all.

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

