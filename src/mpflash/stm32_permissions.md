UDEV  [18023.429878] add      /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.2 (usb)
ACTION=add
DEVPATH=/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.2
SUBSYSTEM=usb
DEVNAME=/dev/bus/usb/001/008
DEVTYPE=usb_device
PRODUCT=483/df11/2200
TYPE=0/0/0
BUSNUM=001
DEVNUM=008
SEQNUM=4234
USEC_INITIALIZED=18023429559
ID_VENDOR=STMicroelectronics
ID_VENDOR_ENC=STMicroelectronics
ID_VENDOR_ID=0483
ID_MODEL=STM32_BOOTLOADER
ID_MODEL_ENC=STM32\x20\x20BOOTLOADER
ID_MODEL_ID=df11
ID_REVISION=2200
ID_SERIAL=STMicroelectronics_STM32_BOOTLOADER_206437A1304E
ID_SERIAL_SHORT=206437A1304E
ID_BUS=usb
ID_USB_INTERFACES=:fe0102:
ID_VENDOR_FROM_DATABASE=STMicroelectronics
ID_MODEL_FROM_DATABASE=STM Device in DFU Mode
ID_PATH=pci-0000:00:14.0-usb-0:1.2
ID_PATH_TAG=pci-0000_00_14_0-usb-0_1_2
DRIVER=usb
ID_FOR_SEAT=usb-pci-0000_00_14_0-usb-0_1_2
MAJOR=189
MINOR=7
TAGS=:seat:
CURRENT_TAGS=:seat:


`udevadm info -a -n /dev/bus/usb/001/008`
ATTR{product}=="STM32  BOOTLOADER"


`lsusb`
Bus 001 Device 008: ID 0483:df11 STMicroelectronics STM Device in DFU Mode

`lsusb -v -d 0483:df11`
Bus 001 Device 008: ID 0483:df11 STMicroelectronics STM Device in DFU Mode
Couldn't open device, some information will be missing
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               1.00
  bDeviceClass            0 
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0        64
  idVendor           0x0483 STMicroelectronics
  idProduct          0xdf11 STM Device in DFU Mode
  bcdDevice           22.00
  iManufacturer           1 STMicroelectronics
  iProduct                2 STM32  BOOTLOADER
  iSerial                 3 206437A1304E
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0036
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          0 
    bmAttributes         0xc0
      Self Powered
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           0
      bInterfaceClass       254 Application Specific Interface
      bInterfaceSubClass      1 Device Firmware Update
      bInterfaceProtocol      2 
      iInterface              4 
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       1
      bNumEndpoints           0
      bInterfaceClass       254 Application Specific Interface
      bInterfaceSubClass      1 Device Firmware Update
      bInterfaceProtocol      2 
      iInterface              5 
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       2
      bNumEndpoints           0
      bInterfaceClass       254 Application Specific Interface
      bInterfaceSubClass      1 Device Firmware Update
      bInterfaceProtocol      2 
      iInterface              6 
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       3
      bNumEndpoints           0
      bInterfaceClass       254 Application Specific Interface
      bInterfaceSubClass      1 Device Firmware Update
      bInterfaceProtocol      2 
      iInterface              7 
      Device Firmware Upgrade Interface Descriptor:
        bLength                             9
        bDescriptorType                    33
        bmAttributes                       11
          Will Detach
          Manifestation Intolerant
          Upload Supported
          Download Supported
        wDetachTimeout                    255 milliseconds
        wTransferSize                    2048 bytes
        bcdDFUVersion                   1.1a


0483:df11

65-mpflash.rules
```
# allow non-root users to access to stm32 device in dfu mode (bootloader) 
SUBSYSTEM=="usb", ACTION=="add", ATTR{product}=="STM32  BOOTLOADER", GROUP="plugdev", MODE="0660"

# allow non-root users to mount usb storage devices
# SUBSYSTEM=="usb", ACTION=="add", ATTR{bInterfaceClass}=="08", GROUP="plugdev", MODE="0660"
```
sudo udevadm control --reload

Show usb devices in tree format with additional information
`lsusb -t -vvv`

/dev/bus/usb/001/009