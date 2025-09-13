
## MUST FIX 

# Longer term things to fix 
 - [ ] generate badges for the stubs 
        https://github.com/python/typing/discussions/1391
        ![PyPI - Types](https://img.shields.io/pypi/types/micropython-esp32-stubs?style=plastic&label=esp32%20generic-S3)


## pyright: 

 - [ ] `d = OrderedDict([("z", 1), ("a", 2)])`
        Argument of type "list[tuple[str, int]]" cannot be assigned to parameter "map" of type "Mapping[_KT@OrderedDict, _VT@OrderedDict]" in function "__init__"
          "list[tuple[str, int]]" is not assignable to "Mapping[_KT@OrderedDict, _VT@OrderedDict]"
## MYPY 
 - [ ] allow overriding stdlib  https://github.com/Josverl/micropython-stubs/issues/781 
    - [ ] needs extras optional install to avoid regressions 
    - [ ] preferably configurable via a config file rather than cmdline param 

# Reference stubs  
- [ ] create docpages for reference stubs (using  AutoDoc201 approach  )

## Merge 

- [ ] network : should proably not add 
     - from .WLANWiPy import *
    - from .WIZNET5K import *

- [ ] avoid using @overloads to push methods to classes that do not have the method, change to @_required / @_merge 
- [ ] Add @mpy_port('port', 'board') decorator to indicate the port the class / functions  is for
- [ ] imports :  copy trailing comments "# type: ignore "
- [ ] copy `FOO_BAR = const(0)` from source to dest
- [ ] copy `FOO_BAR:Final = something` from source to dest

## stdlib 

- [ ] fix duplication of os module in os and stdlib/os      - Keep stdlib version
- [ ] fix duplication of ssl module in ssl and stdlib/ssl ( also for tls) ( ? not sure if this should be in stdlib - not on all ports)

 - [ ] _TimeTuple has different formats/lengths on different platforms ( esp32 )
        - allow both 8 and 9-tuples and just aplin tuple 
        - add docstring to timetuple , refer to existing docpage


Frozen modules
- [ ] optimize the creation of stubs for the frozen modules. This is taken really long , 
      and the same files are being processed multiple times as they are used for eavery board.
      this should be cached and only processed once.




## stubber enrich 

 -[x] enrich cmdline : change to source and destination

 - [x]  enrich : File comments are dupllicated within the same file
    - likely cause : merge same commont from multiple source 

 -[x] enrich : TypeAlias are copied in multiple times `
  - likely cause : merge same typealias from multiple source files 

 -[x] enrich : `_rp2.submodules` recieve too many imports that cannot be resolved 

- [x] during import - do not enhance the "u-module" stubs as this creates a tangle of incorrect imports 
    - there is already a list of u-modules in the stubber, so they should be simple to skip


- [x] improve copy imports during enrich
    - [x] do not copy imports from umodules to non-umodules
    - [x] do not copy `from foo import *` to module foo 


## merge targets
- [x] rewrite logic for determining source --> target selection 
    - [x] reduce the number of candidates 
    - [x] avoid merging from umodule to module 
    - [x] avoid merging from __mpy_shed 
    - [x] avoid merging from pyb.__init to pyb.Accell
## stubber merge 
- [ ] Docstring is added multiple times s from multiple source files. 
    - likely cause : merge same docstring from multiple source files

- [x] machine.Pin.__call__ @overload decorator ends up only a single time in merged Stub ?
- [x] push @overloaded functions to modules that do not have the function 
- [x] push @overload methods to modules that do not have the method 
- [x] push @overload methods to modules that do not have the containing class 
- [x] remove the special case code to ensure Pin.__call__ is in machine.Pin and pyb.Pin  replaced bij @overloads in reference stubs


## micropython-Reference
 
- [x] _rp2.* 
    [x] fix  `from foo import bas as bar`
    [x] remove duplicate comments in `_rp2` files. 
    [x] remove duplicated docstrings 
    [x] remove rp2.irq module ( not needed, _IRQ provided from _mpy_shed )

    [x] for now revert to exposing just the 'rp2' module and hide the implementation details of `_rp2`

## _mpy_shed 
- [x] deque : `deque` is not a generic class.
- [x] publish _mpy_shed to pypi ( or add to micropython-stdlib-stubs )
      > d:\mypython\micropython-stubber\repos\micropython-stubs\stubs\micropython-v1_24_1-docstubs\_mpy_shed\collections\__init__.pyi:327:35 - error: Expected no type arguments for class "deque" (reportInvalidTypeArguments)
      
      fix: class deque(MutableSequence[_T]):

        ![Inconsistent __call__ definitions](image.png)

## rp2 / _rp2 documentation 
- [x] duplicate imports in `_rp2` files. 
    WORAROUND - remove _rp2 from stubs 
- [x] remove `rp2.irq` module ( not needed, _IRQ provided from _mpy_shed )

## neopixel
 - [x] class NeoPixel: - indexing
        https://github.com/Josverl/micropython-stubs/issues/764

        ERROR    root:typecheck.py:171 "tests/quality_tests/check_rp2/check_neopixel.py"(10,0): "__setitem__" method not defined on type "NeoPixel"
        ERROR    root:typecheck.py:171 "tests/quality_tests/check_rp2/check_neopixel.py"(12,10): "__getitem__" method not defined on type "NeoPixel"


## vfs 
- [x] vfs.class AbstractBlockDev(ABC, _BlockDeviceProtocol): 
        AbstractBlockDev does not exist in the firmware-stubs , so is not merged into the merged stubs.

## stdlib

- [x] remove the `from from stdlib.xx import *` from lookup.py 
- [x] remove the `from from stdlib.xx import *` reference-stubs

- [x] fix duplication of sys module in sy and stdlib/sys    = keep stdlib version



- [x]  fix type stubs asyncio.StreamReader
- [x] Update all stdlib  modules from new docstubs - Add to current test/update script 


- [x] find a way to install local stdlib during testing
        - [x] converted stdlib packaging to uv & hathling 
        - [x] updated the `update.py` script tofor the above 
        - [x] install local stdlib during testing together with the local stub package 


### io

- [x] stdib - io 
- [x] IOBase changed to IOBase_mp 
- [x]    class StringIO(IOBase): -->  143:15 - error: Argument to class must be a base class

### time 



    ```
        d:\mypython\micropython-stubber\repos\micropython-stubs\stubs\micropython-v1_24_1-esp32-ESP32_GENERIC-merged\time.pyi:43:18 - warning: Import symbol "mktime" has type "(time_tuple: _TimeTuple | struct_time, /) -> float", which is not assignable to declared type "(local_time: _TimeTuple, /) -> int"
        Type "(time_tuple: _TimeTuple | struct_time, /) -> float" is not assignable to type "(local_time: _TimeTuple, /) -> int"
        Parameter 1: type "_TimeTuple" is incompatible with type "_TimeTuple | struct_time"
            Type "_TimeTuple" is not assignable to type "_TimeTuple | struct_time"
            "Tuple[int, int, int, int, int, int, int, int]" is not assignable to "tuple[int, int, int, int, int, int, int, int, int]"
                Tuple size mismatch; expected 9 but received 8
            "Tuple[int, int, int, int, int, int, int, int]" is not assignable to "struct_time"
    ```
    

    ```py
    <!-- # Peter Hinch  -->
    # Value of RTC time at current instant. This is a notional arbitrary
    # precision integer in μs since Y2K. Notional because RTC is set to
    # local time.
    def _get_rtc_usecs(self):
        y, m, d, weekday, hrs, mins, secs, subsecs = rtc.datetime()
        tim = 1000000 * utime.mktime((y, m, d, hrs, mins, secs, weekday - 1, 0))
        return tim + ((1000000 * (255 - subsecs)) >> 8)


    def inner(tnow):
        tev = tnow  # Time of next event: work forward from time now
        yr, mo, md, h, m, s, wd = localtime(tev)[:7]
        init_mo = mo  # Month now
        toff = do_arg(secs, s)
        tev += toff if toff >= 0 else 60 + toff

        yr, mo, md, h, m, s, wd = localtime(tev)[:7]
        toff = do_arg(mins, m)
        tev += 60 * (toff if toff >= 0 else 60 + toff)

        yr, mo, md, h, m, s, wd = localtime(tev)[:7]
        toff = do_arg(hrs, h)
        tev += 3600 * (toff if toff >= 0 else 24 + toff)

        yr, mo, md, h, m, s, wd = localtime(tev)[:7]
        toff = do_arg(month, mo)
        mo += toff
        md = md if mo == init_mo else 1
        if toff < 0:
            yr += 1
        tev = mktime((yr, mo, md, h, m, s, wd, 0))
        yr, mo, md, h, m, s, wd = localtime(tev)[:7]
        if mday is not None:
            if mo == init_mo:  # Month has not rolled over or been changed
                toff = do_arg(mday, md)  # see if mday causes rollover
                md += toff
                if toff < 0:
                    toff = do_arg(month, mo + 1)  # Get next valid month
                    mo += toff + 1  # Offset is relative to next month
                    if toff < 0:
                        yr += 1
            else:  # Month has rolled over: day is absolute
                md = do_arg(mday, 0)

        if wday is not None:
            if mo == init_mo:
                toff = do_arg(wday, wd)
                md += toff % 7  # mktime handles md > 31 but month may increment
                tev = mktime((yr, mo, md, h, m, s, wd, 0))
                cur_mo = mo
                mo = localtime(tev)[1]  # get month
                if mo != cur_mo:
                    toff = do_arg(month, mo)  # Get next valid month
                    mo += toff  # Offset is relative to new, incremented month
                    if toff < 0:
                        yr += 1
                    tev = mktime((yr, mo, 1, h, m, s, wd, 0))  # 1st of new month
                    yr, mo, md, h, m, s, wd = localtime(tev)[:7]  # get day of week
                    toff = do_arg(wday, wd)
                    md += toff % 7
            else:
                md = 1 if mday is None else md
                tev = mktime((yr, mo, md, h, m, s, wd, 0))  # 1st of new month
                yr, mo, md, h, m, s, wd = localtime(tev)[:7]  # get day of week
                md += (do_arg(wday, 0) - wd) % 7

        return mktime((yr, mo, md, h, m, s, wd, 0)) - tnow    

    ```
  
### socket
 - [ ] mod:socket - missing module constants 
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(5,7): "AF_INET" is not defined
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(5,16): "SOCK_STREAM" is not defined
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(7,7): "AF_INET" is not defined
    ERROR    root:typecheck.py:171 "tests/quality_tests/feat_micropython/check_functions.py"(7,16): "SOCK_DGRAM" is not defined
### asyncio / uasyncio

- [x] uasyncio.Task 
        subclass : 
            class Task(futures._PyFuture):
        methods : 
        - cancel
        - __await__
        - s.read()  / __call__ ?>?


        INFO     root:typecheck.py:175 "tests/quality_tests/feat_uasyncio/check_demo/aiorepl.py"(67,26): Cannot access attribute "cancel" for class "Task"
        Attribute "cancel" is unknown
        INFO     root:typecheck.py:175 "tests/quality_tests/feat_uasyncio/check_demo/aiorepl.py"(69,26): "Task" is not awaitable
        "Task" is incompatible with protocol "Awaitable[_T_co@Awaitable]"
            "__await__" is not present

- [x] uasyncio.pyi should be `from asyncio import *`


 - [x] Disable ruff warnings 
        - UP015, UP031, UP032

 - [x] merge the PinLike TypeAlias and the AnyPin TypeVar 
        - makes it simpler to understand
# -------------------------------------------------------
# QA Tests
# -------------------------------------------------------

- [x] machine.UART - baudrate is not a keyword argument

- [x] AnyReadableBuf - not assignable from  Literal['hello']
        uart_1.write("hello")
        "tests/quality_tests/feat_machine/check_machine/check_machine.py"(33,12): Argument of type "Literal['hello']" cannot be assigned to parameter "buf" of type "AnyReadableBuf" in function "write"
          Type "Literal['hello']" is not assignable to type "AnyReadableBuf"
            "Literal['hello']" is not assignable to "bytearray"
            "Literal['hello']" is not assignable to "array[Unknown]"
            "Literal['hello']" is not assignable to "memoryview[int]"
            "Literal['hello']" is not assignable to "bytes"
        [x] Workaround ; Add Incomplete: 
        `AnyReadableBuf: TypeAlias = bytearray | array | memoryview | bytes | Incomplete`
- [x] AnyWritableBuf - 
        Similar workaround applied for now 
        
- [x] io.BufferedWriter - Missing Class caused by stdlib in wrong location 
        "BufferedWriter" is not a known attribute of module "io"
        >>> dir(io)
        ['__class__', '__name__', 'open', 'BufferedWriter', 'BytesIO', 'IOBase', 'StringIO', '__dict__']



- [x] asyncio - consider changing how the stubs that are used 
      currently in the merge process there are multiple sources for asyncio
        1. reference Stubs 
        2. the docstubs --> [createstub] --> (2b) uasyncio.pyi
        3. the frozen modules --> [createstub] --> uasyncio.pyi
        4. the firmware stubs - merged with Docstubs --> (4b)

        (1) -- merged --> (2)
        (2) -- merged into --> (2b)

        During Build : 
            (2b) overwrites (4b)
            [ ] option : Copy (1.asyncio) --> (4b) if there is an asyncio module 
                ( THEN ALSO  AVOID COPYING & stubbing ASYNCIO DURIGN frozen MERGE )

        3) Manuallu update of the stdlib asyncio/subs 
            - Seems to do well on 1 test repo & machine 


            d:\mypython\!-stubtestprojects\cpython\as_drivers\nec_ir\aremote.py:62:19 - error: "Message" is not awaitable
            d:\mypython\!-stubtestprojects\cpython\as_drivers\i2c\asi2c_i.py:92:39 - error: Object of type "Literal[True]" is not callable
            d:\mypython\!-stubtestprojects\cpython\as_drivers\i2c\asi2c_i.py:107:23 - error: Object of type "Literal[True]" is not callable
                Attribute "__call__" is unknown (reportCallIssue)

- [ ] sys.implementation._machine
