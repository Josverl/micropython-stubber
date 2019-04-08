# simplify and improve the writing of micropython code in Visual Studio code and other modern editors

In order to do this (I suggest) a few things are needed:
- Stub files for the native / enabled modules in the firmware using PEP 484 Type Hints
- Autocompletion / intellisense capabilities for python source files, using VScode and the Python extention 
- Statical syntax checks, or linting, using pylint.
- Suppression of warnings that collide with the micropython principals or code optimization.

Not that the above is not limited to VSCode and Pylint, but it happens to be the combination that I use.
Please feel free to suggest and add other combinations and the relevant steps to configure these. 


## Configuring Visual Studio Code 

### vscode User Settings
file: ~\.vscode\settings.json
``` json
{
    // ...
    "python.autoComplete.extraPaths": ["C:\\develop\\MyPython\\Stubber\\stubs"],
    "python.analysis.typeshedPaths": ["C:\\develop\\MyPython\\Stubber\\stubs"],
    "python.autoComplete.typeshedPaths": ["C:\\develop\\MyPython\\Stubber\\stubs"]
}
```

### vscode workspace settings 
- Enalble linting
- using pylint 
file: .\.vscode\settings.json

```  json
{
    // ...
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}

```
### pylint

Pylint needs 2 settings :
1. init-hook to inform it where the stubs are stored
2. disable some pesty warnings that make no sense for micropython, and thatare caused by the stubs that have only limited information

file: .pylintrc
``` ini
[MASTER]
init-hook='import sys; sys.path.insert(1,"C:\\Develop\\mypython\\Stubber\\stubs")'

disable = missing-docstring, line-too-long, trailing-newlines, broad-except, logging-format-interpolation, invalid-name, 
        no-method-argument, assignment-from-no-return, too-many-function-args, unexpected-keyword-arg
        # the 2nd  line deals with the limited information in the generated stubs.

```

## Downloading the Stubs from GIThub 

This is not complete at this point.
You may find stubs as part of this project, but I have not settled on a d=way to distribute them yet.
If you have suggestions, then please contact me.

## Generating Stubs for a specific Firmware 

The stub files are generated on a micropython board by running the script `createstybs.py`, 
this will generate the stubs on the board, either on flash or on the SD card.
The generation will take a few minutes ( 2-5 minutes) depending on the speed of the board and the number of included modules.

<todo: add board specific modules>  

After this is completed, you will need to download the generated stubs from the micropython board, and save them on a folder on your computer. 
if you work with multiple firmwares or versions it is recomended to use a folder name combining the firmware name and version
- \stubs
    - \ESP32_LoBo_v3.1.20\
    - \ESP32_LoBo_v3.2.24\

Note: I found out that you need to be mindfull of the path and filename limitations on the filesystem if you use IFSS. 

### Tested firmwares :

| Firmware         | Version                          | Comments        |
|------------------|----------------------------------|-----------------|
| Loboris ESP32    | ESP32_LoBo_v3.2.24 on 2018-09-06 | includes _threads module 
| Micropython ESP32| v1.10-247-g0fb15fc3f             | logging modules required 

Note: the logging module currently does not log .... but at least it runs.

## Stub format and limitations 

1. No function parameters are generated 
2. No return types are generated 
3. Instances of imported classess have no type (due to 2)
4. Standard micropython functions [unknown if these work]
5. The stubs use the .py extention rather than .pyi (for autocomplete to work) 
6. Due to the method of generation nested modules are included, rather than referenced. While this leads to somwhat larger stubs, this should not be limiting for using the stubs on a PC.  

### Module Duplication 
Due to the naming convention in micropython some modules will be duplicated , ie `uos` and `os` will both be included 

### References
PEP 3107 -- Function Annotations
https://www.python.org/dev/peps/pep-3107/

PEP 484 -- Type Hints
https://www.python.org/dev/peps/pep-0484/

## Kudos 
The script to create the stubs is based on the work of Aivar Annamaa and the Thonny crew, however the code has been rewritten to run on the micropython board, rather than on a connected PC running python.  

Please refer to : 
https://github.com/thonny/thonny/blob/786f63ff4460abe84f28c14dad2f9e78fe42cc49/thonny/plugins/micropython/__init__.py#L608

## Related 

Possible stub source: Micropython-lib > Cpython backports
https://github.com/pfalcon/micropython-lib#cpython-backports

https://github.com/python/typeshed/

stubgen , runs on host and extracts information from the source 
https://github.com/python/mypy/blob/master/mypy/stubgen.py

