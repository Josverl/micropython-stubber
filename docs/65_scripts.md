# PowerShell Scripts 

A number of scripts have been written in PowerShell as that is one of my preferred scripting languages.
Possibly these scripts could be ported to python , at the cost of more complex handling of OS processes and paths and ports.

(a PR with a port to Python would be appreciated)


(remote_stubber)=
## bulk_stubber.ps1

The goal of this script is to run create_stubs on a set of boards connected to my machine in order to generate new stubs for multiple micropython versions 

high level operation: 
- Scans the serial ports for connected esp32 and esp8266 devices 
  using `get-serialport.ps1 -chip`

- Uses a (hardcoded) list of firmwares including version + chip type 
- for each firmware in that list: 
  - Selects the corresponding device and serialport
  - Flashes the micropython version to the device 
    using `flash_MPY.ps1`
  - waits for the device to finish processing any initial tasks ( file system creation etc) 
    ``` powershell
    rshell -p $serialport  --rts 1 repl "~ print('connected') ~" 
    ```

    ```{note}
    This is quite sensitive to timing and requires some delays to allow the device to restart before the script continues.
    
    Also a bit of automated manipulation of the RTS (and DTR) signals is needed to avoid needing to press a device's reset button.
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

### Minificantion and compilation 

in order to allow createstubs to be run on low-memory devices there are a few steps needed to allow for sufficient memory 

```{mermaid}
graph TD
    M[board\modulelist.txt]
    A[board\createstubs.py] -->|process.py minify| B(minified\createstubs.py)
    
    B --> |mpy-cross -O3|C[[minified\createstubs.mpy]]

    C -->|remote_stubber.ps1| D[esp32]
    C -->|remote_stubber.ps1| E[esp8622]
    M --> D[esp32]
    M --> E[esp8622]
```


### Requirements & dependencies

**Python**
- esptool  - to flash new firmware to the esp32 and esp8266
- pyboard.py - to upload files and run commands (not the old version on PyPi) 
- rshell - to download the folder with stubs 


**PowerShell**
../../Firmware
 - get-serialport.ps1
 - flash_MPY.ps1

### Hardware 
- ESP32 board + SPIRAM on USB + Serial drivers 
- ESP8266 board on USB + Serial drivers 

```{Note}
Multiple  boards can be connected at the same time. 
The script will select the first board of the corresponding type.
If a board-type is not present, then no stubs for that device type will be generated.
```

