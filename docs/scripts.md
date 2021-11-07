# PowerShell Scripts 

A number of scripts have been written in PowerShell as that is one of my preferred scripting languages.
Possibly these scripts could be ported to python , at the cost of more complex handling of OS processes and paths and ports.

(a PR with a port to Python would be appreciated)

## remote_stubber.ps1

The goal of this script is to run create_stubs on a set of boards connected to my machine in order to generate new stubs for multiple micropython versions 

high level operation: 
- Scans the serial ports for connected esp32 and esp8266 devices 
  using `get-serialport.ps1 -chip`

- Uses a (hardcoded) list of firmwares including version + chip type 
- for each firmware in that list: 
  - Selects the corresponding device and serialport
  - Flashes the micropython version to the device 
    using `flash_MPY.ps1`
  - Resets the device
    ``` powershell
    rshell -p $serialport  --rts 1 repl "~ print('connected') ~" 
    rshell -p $serialport  --rts 1 repl "~ import machine ~ machine.reset() ~" 
    ```

    ```{note}
    This is quite sensitive to timing / and requires some delays to allow the device to restart 
    as well as for the the handling of the RTS and DTR signals
    ```
  - Starts the minified version of createstubs.py 
    ``` powershell 
    $createstubs_py = join-path $WSRoot "minified/createstubs.py" 
    pyboard --device $serialport $createstubs_py | write-host
    ```
  - Downloads the generated machine-stubs
    ``` powershell 
    # reverse sync 
    # $dest = path relative to current directory
    # $source = path on board ( all boards are called pyboard) 
    $source = "/pyboard/stubs"
    rshell -p $serialport --buffer-size 512 rsync $source $subfolder  | write-host
    ```

## Requirements & dependencies

**Python**
- esptool 
- pyboard 
- rshell


**PowerShell**
../../Firmware
 - get-serialport.ps1
 - flash_MPY.ps1

## Hardware 
- ESP32 board + SPIRAM on USB + Serial drivers 
- ESP8266 board on USB + Serial drivers 


```{Note}
Multiple  boards can be connected at the same time. 
The script will select the first board of the corresponding type.
If a board-type is not present, then no stubs for that device type will be generated.
```

