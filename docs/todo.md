# TO-DO (provisional)

Docstubs : 
Add `= ...` to module and class level constants to avoid errors when they are used as a default value in function of nethod 

TYPE_DATA : Any = ...

# Upstream Documentation

## esp module

def osdebug(level: int = 0) -> None: 
    """
    Turn vendor O/S debugging messages on or off
    None,           No log output
    1 = ERROR,      Critical errors, software module can not recover on its own
    2 = WARN,       Error conditions from which recovery measures have been taken
    3 = INFO,       Information messages which describe normal flow of events
    4 = DEBUG,      Extra information which is not necessary for normal use (values, pointers, sizes, etc).
    5 = VERBOSE     Bigger chunks of debugging information, or frequent messages which can potentially flood the output.
    """
    ...

## network
add module constants

STA_IF:int =0 
AP_IF:int =1

in docstubs: 
### ifconfig 
in order to accept `ifconfig()` withouth any parameters 
from : 	configtuple: Optional[Any] 
to : 	configtuple: Optional[Tuple] = None 

### ap.config
from:	def config(self, param) -> Any:
to:		def config(self, param:str="", **kwargs) -> Any:

## esp32

### module defines

HEAP_EXEC = 1  # type: int
HEAP_DATA = 4  # type: int

## Class Partition

Add
TYPE APP =1 is needed 

- TYPE_APP = 0  # type: int	
- BOOT = 0  # type: int
- RUNNING = 1  # type: int
- TYPE_DATA = 1  # type: int


### write_pulses
Argument of type "Literal[0]" cannot be assigned to parameter "data" of type "bool" in function "write_pulses"
  "Literal[0]" is incompatible with "bool"

from:
    def write_pulses(self, duration, data=True) -> Any:
to:	
	    def write_pulses(self, duration:Union[List, Tuple], data:int=1) -> None:

or even better an overload 

    @overload
    def write_pulses(self, duration:Union[List, Tuple], data:int=1) -> None:
        ...
    @overload
    def write_pulses(self, duration:int, data: Union[List, Tuple]) -> None:
        ...
    def write_pulses(self, duration:Union[List, Tuple], data:Union[List, Tuple]) -> None:



## working on it 


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


