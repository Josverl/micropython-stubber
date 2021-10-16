




- how to run post-processing
- how the debug setup works 



# stubber : 
<!-- spell-checker: disable -->
-  improve generation of class methods to include (self,...) 
        Normal methods should have at least one parameter (the first of which should be 'self').

- document - that gc and sys modules are somehow ignored by pylint and will keep throwing errors 

- add mpy information to manifest 
- use 'nightly' naming convention in createstubs.py

# frozen stubs 
- Done - generate manifest.json 
- add simple readme.md ?


# Stub augmentation/ merging typeinfomration from copied / generated typerich info
https://libcst.readthedocs.io/en/latest/tutorial.html


# cpython

- read RST files 

- add prototypes from RST 
        ref: https://github.com/python/mypy/blob/master/mypy/stubdoc.py

- add prototypes from Source ? 
        check if https://github.com/python/mypy/blob/master/mypy/stubgenc.py
        might be useful

- test to auto-merge common prototypes by stubber
        ie. add common return types to make_stub_files.cfg

- resolve import time issues 

# Structure on machine 

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
and these are listed in the output window


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

## MyPy Stubgen errors


