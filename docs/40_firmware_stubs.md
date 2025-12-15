# Create Firmware Stubs (formerly MCU stubs)

It is possible to create MicroPython firmware stubs using the `stubber firmware-stubs` command (the `mcu-stubs` alias is still accepted for backward compatibility).

## Quick Examples

```bash
# Generate stubs for all connected MCUs
stubber firmware-stubs

# Generate stubs for specific serial port
stubber firmware-stubs --serial COM3
```

This command will do the following:

1. It determines the serial ports that are available on your system.
2. It runs a small script to determine the {ref}`firmware <firmware>` family, the version and the {ref}`port <port>` of the device, and looks up the {ref}`board's <board>` description in a list of known boards.
3. It uses `mpremote mip` to install the files needed to generate the stubs on the device.
4. It runs a variant of the `createstubs.py` script on the device to generate the stubs.
5. It cleans the stub folder.
6. It generates stubs, using a predetermined list of module names.
   For each found module or submodule a stub file is written to the device and progress is output to the console/{ref}`REPL <repl>`.
7. A {ref}`module manifest <module-manifest>` (`modules.json`) is created that contains the pertinent information determined from the {ref}`board <board>`, the version of createstubs.py and a list of the successfully generated {ref}`stubs <stub-files>`.
8. The generated {ref}`stubs <stub-files>` are downloaded to a folder on the PC, in a subfolder named after the {ref}`firmware ID <firmware-id>` and version.
9. The stubs are post-processed using `stubgen` to format the stubs and generate the .pyi files.
10. The stubs are enriched with typing information from the reference stubs where matching.
11. A new package is created in the publish folder ready for use in your {ref}`IDE <ide>` or publication to PyPI.

**Module duplication**

Due to the module naming convention in MicroPython some modules will be duplicated, i.e. `uos` and `os` will both be included.

## Running the script

The `createstubs.py` script can either be run as a script or imported as a module depending on your preferences.

Running as a script is used on the Linux or Win32 platforms in order to pass a --path parameter to the script.

The steps are:

1. Connect to your board.
2. Upload the script(s) to your board. All variants of the script are located in the [`/board`](https://github.com/Josverl/micropython-stubber/tree/main/board) folder of this repo.
3. Run/import the `createstubs.py` script.
4. Download the generated stubs to a folder on your PC.
5. Run the post-processor [optional, but recommended].

![createstubs-flow][]

**_Note:_** There is a {ref}`memory allocation bug <memory-allocation-bug>` in MicroPython 1.13.0 that prevents createstubs.py from working. This was fixed in nightly build v1.13-103 and newer.

If you try to create stubs on the defective v1.13.0 version, the stubber will raise _{ref}`NotImplementedError <notimplementederror>`_("MicroPython 1.13.0 cannot be stubbed")

## Generating Stubs for a specific Firmware

The {ref}`stub files <stub-files>` are generated on a MicroPython {ref}`board <board>` by running the script `{ref}`createstubs.py <createstubspy>``. This will generate the stubs on the board and store them, either on {ref}`flash <flash-memory>` or on the {ref}`SD card <sd-card>`.
If your firmware does not include the `logging` module, you will need to upload this to your board, or use the minified version.

```python
import createstubs
```

The generation will take a few minutes (2-5 minutes) depending on the speed of the board and the number of included modules.

As the stubs are generated on the board, and as MicroPython is highly optimized to deal with the scarce resources, this unfortunately does mean that the stubs lack parameter details. So for these you must still use the documentation provided for that firmware.

## Downloading the files

After the stub files have been generated, you will need to download the generated stubs from the MicroPython board and most likely you will want to copy and save them in a folder on your computer.
If you work with multiple firmwares, ports or versions it is simple to keep the stub files in a common folder as the firmware ID is used to generate unique names:

- ./stubs
  - /micropython-v1_10-stm32
  - /micropython-v1_12-esp32
  - /micropython-v1_11-linux
  - /loboris-v3_1_20-esp32
  - /loboris-v3_2_24-esp32

## Custom firmware

The script tries to determine a {ref}`firmware ID <firmware-id>` and version from the information provided in `{ref}`sys.implementation <sysimplementation>``, `{ref}`sys.uname() <sysuname>`` and the existence of specific modules.

This firmware ID is used in the stubs, and in the folder name to store the stubs.

If you need, or prefer, to specify a firmware ID you can do so by setting the firmware_id variable before importing createstubs.
For this you will need to edit the createstubs.py file.

The recommendation is to keep the firmware ID short, and add a version as in the below example.

```python
# almost at the end of the file
def main():
    stubber = Stubber(firmware_id='HoverBot v1.2.1')
    # Add specific additional modules to be stubbed
    stubber.add_modules(['hover','rudder'])

```

After this, upload the file and import it to generate the stubs using your custom firmware ID.

## The Unstubbables

There are a limited number of modules that cannot be stubbed by createstubs.py for a number of different reasons. Some simply raise errors, others may reboot the {ref}`MCU <mcu>`, or require a specific configuration or state before they are loaded.

A few of the {ref}`frozen modules <frozen-modules>` are just included as a sample rather than being useful to generate stubs for.

The {ref}`problematic category <problematic-modules>` throw errors or lock up the stubbing process altogether:

```python
 self.problematic=["upysh","webrepl_setup","http_client","http_client_ssl","http_server","http_server_ssl"]
```

The {ref}`excluded category <excluded-modules>` provides no relevant stub information:

```python
 self.excluded=["webrepl","_webrepl","port_diag","example_sub_led.py","example_pub_button.py"]
```

`createstubs.py` will not process a module in either category.

Note that some of these modules are also included in the {ref}`frozen modules <frozen-modules>` that are gathered for those {ref}`ports <port>` or {ref}`boards <board>`.
For those modules it makes sense to use/prioritize the {ref}`.pyi stubs <pyi-files>` for the frozen modules over the {ref}`firmware stubs <mcu-stubs>`.
