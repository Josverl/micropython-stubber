# Create MCU Stubs

It is possible to create MicroPython stubs using the `stubber get-mcu-stubs`command.  

This command will do the following

1. It determines the serialports that are available on your system.
2. It runs a small script to determine the firmware family, the version and the port of the device, and looks up the boards description in a list of known boards.
3. it uses `mpremote mip` to install the files needed to generate the stubs on the device
4. it runs the selected variant of  `createstubs.py` script on the device to generate the stubs


2. it cleans the stub folder 
3. it generates stubs, using a predetermined list of module names.
   for each found module or submodule a stub file is written to the device and progress is output to the console/repl.
4. a module manifest (`modules.json`) is created that contains the pertinent information determined from the board, the version of createstubs.py and a list of the successful generated stubs 

**Module duplication** 

Due to the module naming convention in micropython some modules will be duplicated , ie `uos` and `os` will both be included 

## Running the script

The `createstubs.py` script can either be run as a script or imported as a module depending on your preferences.

Running as a script is used on the linux or win32 platforms in order to pass a --path parameter to the script.

The steps are : 

1. Connect to your board 
2. Upload the script(s) to your board. All variants of the script are located in the [`/board`](https://github.com/Josverl/micropython-stubber/tree/main/board) folder of this repo   
3. Run/import the `createstubs.py` script 
4. Download the generated stubs to a folder on your PC
5. run the post-processor [optional, but recommended]

![createstubs-flow][]



***Note:***  There is a memory allocation bug in MicroPython 1.30 that prevents createstubs.py to work.  this was fixed in nightly build v1.13-103 and newer.

If you try to create stubs on this defective version, the stubber will raise *NotImplementedError*("MicroPython 1.13.0 cannot be stubbed")

## Generating Stubs for a specific Firmware 

The stub files are generated on a MicroPython board by running the script `createstubs.py`, this will generate the stubs on the board and store them, either on flash or on the SD card.
If your firmware does not include the `logging` module, you will need to upload this to your board, or use the minified version.

``` python
import createstubs
```
The generation will take a few minutes ( 2-5 minutes) depending on the speed of the board and the number of included modules.

As the stubs are generated on the board, and as MicroPython is highly optimized to deal with the scarce resources, this unfortunately does mean that the stubs lacks parameters details. So for these you must still use the documentation provided for that firmware.

## Downloading the files

After the sub files have been generated , you will need to download the generated stubs from the micropython board and most likely you will want to copy and  save them on a folder on your computer. 
if you work with multiple firmwares, ports or version it is simple to keep the stub files in a common folder as the firmware id is used to generate unique names

- ./stubs
  - /micropython-v1_10-stm32
  - /micropython-v1_12-esp32
  - /micropython-v1_11-linux
  - /loboris-v3_1_20-esp32
  - /loboris-v3_2_24-esp32

## Custom firmware 

The script tries to determine a firmware ID and version from the information provided in `sys.implementation `,  `  sys.uname()` and the existence of specific modules..

This firmware ID is used in the stubs , and in the folder name to store the subs.

If you need, or prefer, to specify a firmware ID you can do so by setting the firmware_id variable before importing createstubs
For this you will need to edit the createstubs.py file.  

The recommendation is to keep the firmware id short, and add a version as in the below example.

``` python
# almost at the end of the file
def main():
    stubber = Stubber(firmware_id='HoverBot v1.2.1')
    # Add specific additional modules to be stubbed
    stubber.add_modules(['hover','rudder'])

```

after this , upload the file and import it to generate the stubs using your custom firmware id.

## The Unstubbables 

There are a limited number of modules that cannot be stubbed by createstubs.py for a number of different reasons. Some simply raise errors , others my reboot the MCU, or require a specific configuration or state before they are loaded.

a few of the frozen modules are just included as a sample rather \t would not be very useful to generate stubs for these

the problematic category throw errors or lock up the stubbing process altogether: 

```python 
 self.problematic=["upysh","webrepl_setup","http_client","http_client_ssl","http_server","http_server_ssl"]
```

The excluded category provides no relevant stub information 

``` python 
 self.excluded=["webrepl","_webrepl","port_diag","example_sub_led.py","example_pub_button.py"]
```

`createstubs.py` will not process a module in either category.

Note: that some of these modules are also included in the frozen modules that are gathered for those ports or boards. 
For those modules it makes sense to use/prioritize the .pyi stubs for the frozen modules over the MCU stubs.
