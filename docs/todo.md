# TO-DO (provisional)

## working on it 

### read RST files 
- add prototypes from RST 
        ref: https://github.com/python/mypy/blob/master/mypy/stubdoc.py



### documentation 
- how to run post-processing
- how the debug setup works 


### stubber : 

- document - that gc and sys modules are somehow ignored by pylint and will keep throwing errors 
- add mpy information to manifest 
- use 'nightly' naming convention in createstubs.py
- change firmware naming 

### frozen stubs 
- add simple readme.md ?

### Stub augmentation/ merging typeinformation from copied / generated typerich info
https://libcst.readthedocs.io/en/latest/tutorial.html

- add prototypes from Source ? 
        check if https://github.com/python/mypy/blob/master/mypy/stubgenc.py
        might be useful

- test to auto-merge common prototypes by stubber
        ie. add common return types to make_stub_files.cfg

- resolve import time issues 


### SYS en GC 
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


### Webrepl
Unable to import 'webrepl'
can include in common modules 
C:\develop\MyPython\micropython\extmod\webrepl\webrepl.py


