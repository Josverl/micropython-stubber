## stubber : 
###  main 

- resolve issues in main
- integrate changes by braden
- check/verify/add micropython frozen modules 

  - See ESP32 : C:\develop\MyPython\micropython\ports\esp32\boards\manifest.py

        freeze('$(PORT_DIR)/modules')                                       - included by braden 
        freeze('$(MPY_DIR)/tools', ('upip.py', 'upip_utarfile.py'))         - ?
        freeze('$(MPY_DIR)/ports/esp8266/modules', 'ntptime.py')            - ?
        freeze('$(MPY_DIR)/drivers/dht', 'dht.py')                          - ?
        freeze('$(MPY_DIR)/drivers/onewire')
        include('$(MPY_DIR)/extmod/webrepl/manifest.py')

- ESP8622 : C:\develop\MyPython\micropython\ports\esp8266\boards\manifest.py
        freeze('$(PORT_DIR)/modules')
        freeze('$(MPY_DIR)/tools', ('upip.py', 'upip_utarfile.py'))
        freeze('$(MPY_DIR)/drivers/dht', 'dht.py')
        freeze('$(MPY_DIR)/drivers/onewire')
        include('$(MPY_DIR)/extmod/webrepl/manifest.py')

        
        



- read RST files 
- add prototypes from source / RST 
- test to automerge common prototypes by stubber

- resolve import time issues 

pylint : disable a few more ?

support function decorators 
- @micropython.native / viper / bytecode
 there is a CPython Dummy function decorators placeholder : https://github.com/micropython/micropython/blob/master/examples/micropython.py


# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
- ssd1306 module
    from ssd1306 import  SSD1306_I2C


# micropy - added issue https://github.com/BradenM/micropy-cli/issues/96
.pylintrc logic 
- ./src/lib path 
- ./src/lib path 









