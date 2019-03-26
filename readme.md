# simplify and improve the writing of micropython code in Visual Studio code and other modern editors

# Configuring Visual Studio Code 

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

# Downloading the Stubs from GIThub 


# Generating Stubs for a specific Firmware 

The stub files are generated on a micropython board by running the script `createstybs.py`
this will generate the stubs on the board, either on flash or on the SD card.
The generation will take a few minutes ( 2-5 minutes) depending on the speed of the board and the number of included modules.

todo: add board specific modules 

After this is completed, you will need to download the generated stubs from the micropython board, and save them on a folder on your computer. 
if you work with multiple firmwares or versions it is recomended to use a folder name combining the firmware name and version
- \stubs
    - \ESP32_LoBo_v3.1.20\
    - \ESP32_LoBo_v3.2.24\
    
## module Duplication 
Due to the naming convention in micropython some modules will be duplicated , ie `uos` and `os` will both be included 


## Stub format and limitations 




