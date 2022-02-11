# TO-DO (provisional)
# Upstream Documentation


in docstubs: 
### ifconfig 
in order to accept `ifconfig()` withouth any parameters 
from : 	configtuple: Optional[Any] 
to : 	configtuple: Optional[Tuple] = None 

### ap.config
from:	def config(self, param) -> Any:
to:		def config(self, param:str="", **kwargs) -> Any:

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

- test to auto-merge common prototypes by stubber
        ie. add common return types to make_stub_files.cfg



### Webrepl
Unable to import 'webrepl'
can include in common modules 
C:\develop\MyPython\micropython\extmod\webrepl\webrepl.py


