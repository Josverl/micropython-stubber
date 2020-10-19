## stubber : 

improve generation of class methods to include (self,...) 
        Normal methods should have at least one parameter (the first of which should be 'self').


###  main 

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

- exclude more modules 
        = logging, as this is distributed , and can instead be generated from micropylib/logging
        - standard frozen modules 

        Also allow for force option to stub them anyway

- read RST files 

- add prototypes from RST 
        ref: https://github.com/python/mypy/blob/master/mypy/stubdoc.py

- add prototypes from Source ? 
        check if https://github.com/python/mypy/blob/master/mypy/stubgenc.py
        might bge usefull

- test to automerge common prototypes by stubber
        ie. add common return types to make_stub_files.cfg

- resolve import time issues 

pylint : disable a few more ?

done -support function decorators 
        - @micropython.native / viper / bytecode
        is resolved by
        there is a CPython Dummy function decorators placeholder : https://github.com/micropython/micropython/blob/master/examples/micropython.py


# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
- ssd1306 module
    from ssd1306 import  SSD1306_I2C


# Structuur op machine 

- Apart Micropython-Stubs repo 
- ..\micropython-stubs  linked to Stubber stubs ( submodule ?)
- 


# SYS en GC 
#pylint: disable=no-member      ## workaround for sys and gc

Module 'sys' has no 'print_exception' member
Module 'gc' has no 'mem_free' member
Module 'gc' has no 'threshold' member
Module 'gc' has no 'mem_free' member
Module 'gc' has no 'mem_alloc' member
{
	"resource": "/c:/develop/MyPython/ESP32-P1Meter/src/main.py",
	"owner": "python",
	"code": "no-member",
	"severity": 8,
	"message": "Module 'gc' has no 'mem_free' member",
	"source": "pylint",
	"startLineNumber": 33,
	"startColumn": 22,
	"endLineNumber": 33,
	"endColumn": 22
}
--------------
# Webrepl
Unable to import 'webrepl'
can include in common modules 
C:\develop\MyPython\micropython\extmod\webrepl\webrepl.py


# strange messages in Python Language Server output

these seem to be the language predictions when autocompletion is used in the code editor 


import os
os.<tab>

--> this shows a dropdown with *
and thesre are listed in the output window


import uos
uos.<tab>
-->  no start , no returns in the output window

```
[Info  - 12:12:59] Initializing for C:\Python\Python38\python.exe
[Info  - 12:12:59] Analysis caching mode: None.
[Info  - 13:01:02] Current invocation parsing returned null, aborting IntelliCode recommendation!
[Info  - 13:01:02] Deep learning IntelliCode recommendations service returned in 68 millis
[Info  - 13:03:06] Current invocation parsing returned null, aborting IntelliCode recommendation!
[Info  - 13:03:06] Deep learning IntelliCode recommendations service returned in 6 millis
[Info  - 13:03:07] Current invocation parsing returned null, aborting IntelliCode recommendation!
[Info  - 13:03:07] Deep learning IntelliCode recommendations service returned in 4 millis
```

it seems to do something sometimes 
```
Info  - 13:07:10] Deep learning IntelliCode recommendations service returned in 5 millis
[Info  - 13:07:12] Predictions: message, host, exception, port, service, server, credentials, zone, timestamp, connectTCP, user_agent, token, decoder, makeConnection, days, iinfo, transport, float16, set_exception, utcnow
[Info  - 13:07:12] Time taken to get predictions: 43 ms, Memory increased: 44036096 bytes
[Info  - 13:07:12] Deep learning IntelliCode recommendations service returned in 55 millis
[Info  - 13:08:01] Current invocation parsing returned null, aborting IntelliCode recommendation!
[Info  - 13:08:01] Deep learning IntelliCode recommendations service returned in 4 millis
```





