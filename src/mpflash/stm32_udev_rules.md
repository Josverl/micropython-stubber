## Linux permissions for usb devices 

In order to flash the firmware to the board, you need to have the correct permissions to access the USB devices.
The details will depend on the specific USB device and the operating system you are using.

You can use the following udev rules to give non-root users access to the USB devices.

File: `/etc/udev/rules.d/65-mpflash.rules`
```bash
# allow non-root users to access to stm32 device in dfu mode (bootloader)
SUBSYSTEM=="usb", ACTION=="add", ATTR{product}=="STM32  BOOTLOADER", GROUP="plugdev", MODE="0660"
```
reload the udev rules with the following command:
```bash
sudo udevadm control --reload
```
Unplug and replug the usb device to apply the new rules.


## to check 
Enter the stm32 bootloader mode
``` bash
mpremote bootloader 
```


List usb devices
```bash
(.venv) jos@jvnuc:~/projects/micropython-stubber$ lsusb -vv -t
/:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/6p, 10000M
    ID 1d6b:0003 Linux Foundation 3.0 root hub
    /sys/bus/usb/devices/usb2  /dev/bus/usb/002/001
/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/12p, 480M
    ID 1d6b:0002 Linux Foundation 2.0 root hub
    /sys/bus/usb/devices/usb1  /dev/bus/usb/001/001
    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/4p, 12M
        ID 0a05:7211 Unknown Manufacturer hub
        /sys/bus/usb/devices/1-1  /dev/bus/usb/001/002
        |__ Port 1: Dev 4, If 0, Class=Hub, Driver=hub/4p, 12M
            ID 0a05:7211 Unknown Manufacturer hub
            /sys/bus/usb/devices/1-1.1  /dev/bus/usb/001/004
        |__ Port 2: Dev 22, If 0, Class=Application Specific Interface, Driver=, 12M
            ID 0483:df11 STMicroelectronics STM Device in DFU Mode
            /sys/bus/usb/devices/1-1.2  /dev/bus/usb/001/022
    |__ Port 10: Dev 3, If 0, Class=Wireless, Driver=btusb, 12M
        ID 8087:0aaa Intel Corp. Bluetooth 9460/9560 Jefferson Peak (JfP)
        /sys/bus/usb/devices/1-10  /dev/bus/usb/001/003
    |__ Port 10: Dev 3, If 1, Class=Wireless, Driver=btusb, 12M
        ID 8087:0aaa Intel Corp. Bluetooth 9460/9560 Jefferson Peak (JfP)
        /sys/bus/usb/devices/1-10  /dev/bus/usb/001/003
```
Lookup the stm32 device device path ( /dev/bus/usb/001/022),  
and check if the group `plugdev` is granted access using `ll`
```bash
(.venv) jos@jvnuc:~/projects/micropython-stubber$ ll /dev/bus/usb/001/022
crw-rw-r-- 1 root plugdev 189, 21 mrt 11 22:38 /dev/bus/usb/001/022
```

Check `groups` to see if user is in plugdev group
```
(.venv) jos@jvnuc:~/projects/micropython-stubber$ groups
jos adm disk dialout cdrom sudo dip plugdev kvm lpadmin lxd sambashare usb
```