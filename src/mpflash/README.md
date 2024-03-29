# mpflash
mpflash is a command-line tool for working with MicroPython firmware. It provides various features to help you develop, build, and manage your MicroPython projects.

This tool was created to be used in a CI/CD pipeline to automate the process of downloading and flashing MicroPython firmware to multiple boards, but it can also be used for manual flashing and development.

mpflash has been tested on Windows x64, Linux X64 and ARM64, but not (yet) macOS.

## Features
 1. List the connected boards including their firmware details, in a tabular or json format
 2. Download MicroPython firmware for specific boards and versions.
 3. Flash one or all connected MicroPython boards with a specific firmware or version.
    Tested ports: rp2, samd, esp32, esp32s3, esp8266 and stm32 (requires cubeprogrammer)
 
## Installation
To install mpflash, you can use pip: `pip install mpflash`

## Basic usage
You can use mpflash to perform various operations on your MicroPython boards. Here is an example of basic usage:

| Command | Description |
|---------|-------------|
| `mpflash list` | List the connected board(s) including their firmware details |
| `mpflash download` | Download the MicroPython firmware(s) for the connected board(s) |
| `mpflash flash` | Flash the latest stable firmware to the connected board(s) |


## Linux permissions for usb devices 
In order to flash the firmware to the board, you need to have the correct permissions to access the USB devices.
On Windows this will not be an issue, but on Linux you can use  udev rules to give non-root users access to the USB devices.
[See thestm32_permissions documentation](./stm32_udev_rules.md) for more information.


## Advanced use
You can list the connected boards using the following command:
```bash
$ mpflash list
D:\MyPython\micropython-stubber> mpflash list
Getting board info ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02
                                       Connected boards
┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Serial ┃ Family      ┃ Port    ┃ Board              ┃ CPU         ┃ Version        ┃ build ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ COM11  │ micropython │ rp2     │ RPI_PICO_W         │ RP2040      │ 1.20.0         │       │
│ COM12  │ micropython │ esp8266 │ ESP8266_GENERIC    │ ESP8266     │ 1.22.2         │       │
│ COM18  │ micropython │ rp2     │ RPI_PICO_W         │ RP2040      │ 1.23.0-preview │ 155   │
│ COM3   │ micropython │ samd    │ SEEED_WIO_TERMINAL │ SAMD51P19A  │ 1.23.0-preview │ 155   │
│ COM5   │ micropython │ stm32   │ PYBV11             │ STM32F405RG │ 1.23.0-preview │ 166   │
│ COM8   │ micropython │ esp32   │ ESP32_GENERIC_S3   │ ESP32S3     │ 1.23.0-preview │ 155   │
└────────┴─────────────┴─────────┴────────────────────┴─────────────┴────────────────┴───────┘
```

Suppose you want to download the MicroPython firmware for some boards, you can use the following command: 

```bash
# download the firmware
$ mpflash download --board ESP8266_GENERIC --board SEEED_WIO_TERMINAL
```	
This will download the latest stable version of the MicroPython firmware for the boards and save it in the `firmware` directory.
The stable version (default) is determined based on the most recent published release,
other optionse are `--version preview` and `--version x.y.z` to download the latest preview or version x.y.z respectively.

by default the firmware will be downloaded to  Downloads  in a `firmware` folder in your, but you can specify a different directory using the `--dir` option.

```bash
The directory structure will be something like this:
```
Downloads/firmware
|   firmware.jsonl
+---esp8266
|       ESP8266_GENERIC-FLASH_1M-v1.22.2.bin
|       ESP8266_GENERIC-FLASH_512K-v1.22.2.bin
|       ESP8266_GENERIC-OTA-v1.22.2.bin
|       ESP8266_GENERIC-v1.22.2.bin
\---samd
        SEEED_WIO_TERMINAL-v1.22.2.uf2
```
You can then flash the firmware to the board using the following command: `mpflash flash`
This will (try to) autodetect the connected boards, and determine the correct firmware to flash to each board.

```bash
> mpflash flash
22:15:55 | ℹ️  - Using latest stable version: v1.22.2
                                       Connected boards
┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Serial ┃ Family      ┃ Port    ┃ Board              ┃ CPU         ┃ Version        ┃ build ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ COM11  │ micropython │ rp2     │ RPI_PICO_W         │ RP2040      │ 1.20.0         │       │
│ COM12  │ micropython │ esp8266 │ ESP8266_GENERIC    │ ESP8266     │ 1.22.2         │       │
│ COM18  │ micropython │ rp2     │ RPI_PICO_W         │ RP2040      │ 1.23.0-preview │ 155   │
│ COM3   │ micropython │ samd    │ SEEED_WIO_TERMINAL │ SAMD51P19A  │ 1.23.0-preview │ 155   │
│ COM5   │ micropython │ stm32   │ PYBV11             │ STM32F405RG │ 1.23.0-preview │ 166   │
│ COM8   │ micropython │ esp32   │ ESP32_GENERIC_S3   │ ESP32S3     │ 1.23.0-preview │ 155   │
└────────┴─────────────┴─────────┴────────────────────┴─────────────┴────────────────┴───────┘
22:15:58 | ℹ️  - Found v1.22.2 firmware rp2\RPI_PICO_W-v1.22.2.uf2 for RPI_PICO_W on COM11.
22:15:58 | ℹ️  - Found v1.22.2 firmware esp8266\ESP8266_GENERIC-v1.22.2.bin for ESP8266_GENERIC on COM12.
22:15:58 | ℹ️  - Found v1.22.2 firmware rp2\RPI_PICO_W-v1.22.2.uf2 for RPI_PICO_W on COM18.
22:15:58 | ℹ️  - Found v1.22.2 firmware samd\SEEED_WIO_TERMINAL-v1.22.2.uf2 for SEEED_WIO_TERMINAL on COM3.
22:15:58 | ⚠️  - Trying to find a firmware for the board PYBV11
22:15:58 | ❌  - No v1.22.2 firmware found for PYBV11 on COM5.
22:15:58 | ⚠️  - Trying to find a firmware for the board ESP32-GENERIC-S3
22:15:58 | ❌  - No v1.22.2 firmware found for ESP32_GENERIC_S3 on COM8.
22:15:58 | ℹ️  - Updating RPI_PICO_W on COM11 to 1.22.2
22:15:58 | ℹ️  - Erasing not yet implemented for UF2 flashing.
22:15:58 | ℹ️  - Entering UF2 bootloader on RPI_PICO_W on COM11
22:15:58 | ℹ️  - Waiting for mcu to mount as a drive : 10 seconds left
22:15:59 | ℹ️  - Waiting for mcu to mount as a drive : 9 seconds left
22:16:00 | ℹ️  - Board is in bootloader mode
22:16:00 | ℹ️  - Copying firmware\rp2\RPI_PICO_W-v1.22.2.uf2 to F:
22:16:13 | ✅  - Done copying, resetting the board and wait for it to restart
22:16:23 | ℹ️  - Updating ESP8266_GENERIC on COM12 to 1.22.2
22:16:23 | ℹ️  - Flashing firmware\esp8266\ESP8266_GENERIC-v1.22.2.bin on ESP8266_GENERIC on COM12
22:16:23 | ℹ️  - Running esptool --chip ESP8266 --port COM12 erase_flash 
esptool.py v4.7.0
Serial port COM12
Connecting....
...
Chip erase completed successfully in 6.5s
Hard resetting via RTS pin...
22:16:31 | ℹ️  - Running esptool --chip ESP8266 --port COM12 -b 460800 write_flash --flash_size=detect 0x0 firmware\esp8266\ESP8266_GENERIC-v1.22.2.bin 
esptool.py v4.7.0
Serial port COM12
Connecting....
...
Leaving...
Hard resetting via RTS pin...
22:16:43 | ℹ️  - Done flashing, resetting the board and wait for it to restart
22:16:49 | ✅  - Flashed 1.22.2 to ESP8266_GENERIC on COM12 done
22:16:49 | ℹ️  - Updating RPI_PICO_W on COM18 to 1.22.2
22:16:49 | ℹ️  - Erasing not yet implemented for UF2 flashing.
22:16:49 | ℹ️  - Entering UF2 bootloader on RPI_PICO_W on COM18
22:16:49 | ℹ️  - Waiting for mcu to mount as a drive : 10 seconds left
22:16:50 | ℹ️  - Waiting for mcu to mount as a drive : 9 seconds left
22:16:51 | ℹ️  - Board is in bootloader mode
22:16:51 | ℹ️  - Copying firmware\rp2\RPI_PICO_W-v1.22.2.uf2 to F:[/bold]
22:17:02 | ✅  - Done copying, resetting the board and wait for it to restart
22:17:12 | ℹ️  - Updating SEEED_WIO_TERMINAL on COM3 to 1.22.2
22:17:12 | ℹ️  - Erasing not yet implemented for UF2 flashing.
22:17:12 | ℹ️  - Entering UF2 bootloader on SEEED_WIO_TERMINAL on COM3
22:17:12 | ℹ️  - Waiting for mcu to mount as a drive : 10 seconds left
22:17:13 | ℹ️  - Waiting for mcu to mount as a drive : 9 seconds left
22:17:14 | ℹ️  - Board is in bootloader mode
22:17:14 | ℹ️  - Copying firmware\samd\SEEED_WIO_TERMINAL-v1.22.2.uf2 to F:[/bold]
22:17:17 | ✅  - Done copying, resetting the board and wait for it to restart
22:17:27 | ℹ️  - Flashed 4 boards
                               Connected boards after flashing
┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Serial ┃ Family      ┃ Port    ┃ Board              ┃ CPU         ┃ Version        ┃ build ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ COM11  │ micropython │ rp2     │ RPI_PICO_W         │ RP2040      │ 1.22.2         │       │
│ COM12  │ micropython │ esp8266 │ ESP8266_GENERIC    │ ESP8266     │ 1.22.2         │       │
│ COM18  │ micropython │ rp2     │ RPI_PICO_W         │ RP2040      │ 1.22.2         │       │
│ COM3   │ micropython │ samd    │ SEEED_WIO_TERMINAL │ SAMD51P19A  │ 1.22.2         │       │
│ COM5   │ micropython │ stm32   │ PYBV11             │ STM32F405RG │ 1.23.0-preview │ 166   │
│ COM8   │ micropython │ esp32   │ ESP32_GENERIC_S3   │ ESP32S3     │ 1.23.0-preview │ 155   │
└────────┴─────────────┴─────────┴────────────────────┴─────────────┴────────────────┴───────┘
```
Note that if no matching firmware can be found for a board, it will be skipped.
(For example, the PYBV11 and ESP32_GENERIC_S3 boards in the example above.)

## Issues and bug reports
mpflash is currently co-located in the [micropython-stubber](https://github.com/Josverl/micropython-stubber) repository.
Please report any issues or bugs in the [issue tracker](https://github.com/Josverl/micropython-stubber/issues) with '[mpflash]' in the subject.

## License
mpflash is licensed under the MIT license. See the LICENSE file for more details.
