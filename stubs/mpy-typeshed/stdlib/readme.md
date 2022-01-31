

file(s)                     | source             | comments
----------------------------|--------------------|----------------
_typeshed/**                | typeshed
collections/**              | typeshed
importlib/**                | typeshed
_ast.pyi                    | typeshed
_collections_abc.pyi        | typeshed
_importlib_modulespec.pyi   | typeshed
abc.pyi                     | typeshed
array.pyi                   | custom        | --> uarray.pyi
ast.pyi                     | typeshed
binascii.pyi                | custom        | --> ubinascii
builtins.pyi * .py          | docstubs 1.18
cmapth.pyi & py             | docstubs 1.18
CP_builtins.pyi             | typeshed  | unused
CP_cmath.pyi                | typeshed | unused
CP_thread.pyi               | typeshed | unused
errno.pyi                   | custom   | from uerrno import *
gc.pyi                      | docstubs 1.18
hashlib.pyi                 | custom | --> from uhashlib import *
io.pyi                      | custom | --> 
math.pyi                    | docstubs 
mmap.pyi                    | typeshed
os.pyi                      | custom | --> 
random.pyi                  | custom | --> 
re.pyi                      | custom | --> 
select.pyi                  | custom | --> 
struct.pyi                  | custom | --> 
sys.pyi                     | custom | --> 
time.pyi                    | custom | --> 
types.pyi                   | typeshed
typing.pyi                  | typeshed
uarray.pyi                  | typeshed | commented method : def decode(self) -> str: ...
ubinascii.pyi               | docstubs 1.18
uctypes.pyi                 | *** GET typeshed ***
uerrno.pyi                  | ?? seems to be manual
uhashlib.pyi                | typeshed , only single class ?- missing sha1
uio.pyi                     | typeshed / digi 
uos.pyi                     | typeshed / digi 
urandom.pyi                 | typeshed
ure.pyi                     | typeshed
uselect.pyi                 | typeshed / digi - customized
ustruct.pyi                 | digi
usys.pyi                    | digi
utime.pyi                   | digi
uzlib.pyi                   | ??
zlib.pyi                    | reference to uzlib
















# from mypi
- types
- typing




# docstubs 
- builtins
- gc.py --> gp.pyi