"""
Lookup tables for the rst documentation stubber
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

# These are shown to import
__all__ = [
    "TYPING_IMPORT",
    "LOOKUP_LIST",
    "NONE_VERBS",
    "CHILD_PARENT_CLASS",
    "PARAM_FIXES",
    "PARAM_RE_FIXES",
    "MODULE_GLUE",
    "RST_DOC_FIXES",
    "DOCSTUB_SKIP",
]

# all possible Types needed for the stubs - excess types should be removed later , and otherwise won't do much harm
TYPING_IMPORT: List[str] = [
    "from __future__ import annotations",
    "from _typeshed import Incomplete",
    "from typing import IO, Any, Callable, Coroutine, Dict, Generator, Iterator, List, NoReturn, Optional, Tuple, Union, NamedTuple",
    "from typing_extensions import TypeVar, TypeAlias, Awaitable",
    # "# TYPING_IMPORT",
]


@dataclass
class Fix:
    """A fix for a parameter or return type in the documentation that is needed to render it to a valid type annotation

    - from_ : the string or regex that should be fixed
    - to : the improved version to replace it with
    - module : filter the fix to be only applied to a specific module
    - name : filter the fix to be only applied to a specific member
    - is_re : the from_ string is a regular expression
    """

    from_: str
    "The string or regex that should be fixed"
    to: str
    "The improved version to replace it with"
    name: Optional[str] = None
    "Filter the fix to be only applied to a specific module member"
    module: Optional[str] = None
    "Filter the fix to be only applied to a specific module"
    is_re: bool = False
    "the from_ string is a regular expression"



# This table is used to try to correct the errors in the documentation,
#  or adapt the human readable documentation to machine readable.
# it is applied to each .rst file after loading the contents.
# also applies correction for some classes are documented as functions

RST_DOC_FIXES: List[Tuple[str, str]] = [
    # ------------------------------------------------------------------------------------------------
    # re.rst - function and class with the same name
    # done: issue https://github.com/micropython/micropython/issues/8273
    # TODO: Create PR fix class Match
    (".. method:: match.", ".. method:: Match."),
    ("            match.end", "            Match.end"),
    # ------------------------------------------------------------------------------------------------
    # collections.rst - should be fixed in v1.19
    # PR: https://github.com/micropython/micropython/pull/7976
    # keep around for older docstubs
    (".. function:: deque(", ".. class:: deque("),
    (".. function:: OrderedDict(", ".. class:: OrderedDict("),
    # ------------------------------------------------------------------------------------------------
    # generator functions - WILL_NOT_FIX in the MicroPython documentation
    # these are documented as functions, but return an object with the the same name as the function.
    # for static type analysis this is best considered as a Class, so morph them before processing.
    # uselect.rst
    (".. function:: poll(", ".. class:: poll("),
    # ESPNow.rst - multiple methods on a single line, split to multiline
    (
        ".. method:: AIOESPNow._aiter__() / async AIOESPNow.__anext__()",
        ".. method:: AIOESPNow._aiter__()\n            async AIOESPNow.__anext__()",
    ),
    # appended to in ssl.constant name  - ssl.PROTOCOL_DTLS_CLIENT(when DTLS support is enabled)
    # Ugly hack to fix the documentation
    ( '(when DTLS support is enabled)', " : Incomplete # (when DTLS support is enabled)")
]


# docstubs generation, exclude stub generation for below stubs.
DOCSTUB_SKIP = [
    "uasyncio.rst",  # can create better stubs from frozen python modules.
    "builtins.rst",  # conflicts with static type checking , has very little information anyway
    "re.rst",  # regex is too complex
]

# contains return types for functions and methods that are not clearly documented.
"""
this is an list with manual overrides for function returns that could not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = module.[class.]function name
- value : two-tuple with ( return type , priority )
"""
LOOKUP_LIST = {
    "builtins.bytes": ("bytes", 0.95),
    "builtins.from_bytes": ("int", 0.95),
    "builtins.to_bytes": ("bytes", 0.95),
    "bytearray_at": ("bytearray", 0.95),
    "collections.namedtuple": ("type[Tuple[Any, ...]]", 0.95),
    "gc.collect": ("None", 0.95),
    "machine.deepsleep": ("NoReturn", 0.95),
    "machine.reset_cause": ("int", 0.95),
    "machine.reset": ("NoReturn", 0.95),  # never returns
    "machine.Signal.value": ("int", 0.95),
    "machine.soft_reset": ("NoReturn", 0.95),  # never returns
    "machine.UART.irq": ("_IRQ", 0.95),  # no IRQ type defined
    "machine.UART.write": ("Union[int,None]", 0.95),
    "machine.UART.readinto": ("Union[int,None]", 0.95),
    "machine.UART.readline": ("Union[str,None]", 0.95),
    "math.isnan": ("bool", 0.95),
    "micropython.opt_level": ("Incomplete", 0.95),  # Not clear in docstring
    # since 1.19 const can also be string , bytes or tuple
    "micropython.const": ("Const_T", 1),  # const: 1 -  paired with param typing
    "micropython.heap_lock": ("int", 1),
    "micropython.heap_unlock": ("int", 1),
    "micropython.heap_locked": ("bool", 1),
    "pyb.hard_reset": ("NoReturn", 0.95),  # never returns
    "pyb.I2C.recv": ("bytes", 0.95),  # complex in docstring
    "pyb.SPI.recv": ("bytes", 0.95),  # complex in docstring
    "pyb.hid_keyboard": ("HID_Tuple", 0.95),  # ?
    "pyb.hid_mouse": ("HID_Tuple", 0.95),  # plain wrong
    "bluetooth.BLE.irq": ("_IRQ", 0.95),
    "ubluetooth.BLE.irq": ("_IRQ", 0.95),
    "uctypes.bytearray_at": ("bytearray", 0.95),
    "uctypes.bytes_at": ("bytes", 0.95),
    "uio.open": ("IO", 0.95),  #  Open a file.
    "uos.listdir": ("List[Incomplete]", 0.95),
    "os.uname": ("uname_result", 0.95),
    # ssl.SSLSocket is defined in reference/micropython/ssl
    
    "ssl.wrap_socket": ("SSLSocket", 0.95),
    "ussl.wrap_socket": ("SSLSocket", 0.95),
    #
    "usys.exit": ("NoReturn", 0.95),  # never returns
    "utime.sleep_ms": (
        "Coroutine[None, None, None]",  # Micropython V1.15+ ?
        0.95,
    ),
    "stm.mem8": ("bytearray", 0.95),  # Read/write 8 bits of memory.
    "stm.mem16": ("bytearray", 0.95),  # Read/write 16 bits of memory.
    "stm.mem32": ("bytearray", 0.95),  # Read/write 32 bits of memory.
    # Onewire documented mostly in sourcecode
    "_onewire.reset": ("bool", 0.95),
    "_onewire.scan": ("List[int]", 0.95),
    "_onewire.readbit": ("int", 0.95),
    "_onewire.readbyte": ("int", 0.95),
    "_onewire.writebyte": ("None", 0.95),
    "_onewire.writebit": ("None", 0.95),
    "_onewire.crc8": ("int", 0.95),
    # espnow
    "espnow.ESPNow.recv": ("Union[List, Tuple[None,None]]", 0.95),  # list / ? tuple of bytestrings
    # esp32
    "esp32.Partition.readblocks": ("None", 0.95),
    "esp32.Partition.writeblocks": ("None", 0.95),
    "_rp2.bootsel_button": ("int", 0.95),
    "_rp2.DMA.active": ("bool", 0.95),
    "_rp2.DMA.pack_ctrl": ("int", 0.95),
    "_rp2.DMA.unpack_ctrl": ("dict", 0.95),
    "_rp2.DMA.close": ("None", 0.95),
    "_rp2.DMA.config": ("None", 0.95),
    "_rp2.DMA.irq": ("_IRQ", 0.95),
    "_rp2.PIO.state_machine": ("StateMachine", 0.95),
    "_rp2.PIO.irq": ("_IRQ", 0.95),
    "_rp2.PIO.remove_program": ("None", 0.95),
    "_rp2.PIO.add_program": ("None", 0.95),
    "rp2.bootsel_button": ("int", 0.95),
    "rp2.DMA.active": ("bool", 0.95),
    "rp2.DMA.pack_ctrl": ("int", 0.95),
    "rp2.DMA.unpack_ctrl": ("dict", 0.95),
    "rp2.DMA.close": ("None", 0.95),
    "rp2.DMA.config": ("None", 0.95),
    "rp2.DMA.irq": ("_IRQ", 0.95),
    "rp2.PIO.state_machine": ("StateMachine", 0.95),
    "rp2.PIO.irq": ("_IRQ", 0.95),
    "rp2.PIO.remove_program": ("None", 0.95),
    "rp2.PIO.add_program": ("None", 0.95),
}


# if no type has been determined, and the docstring starts with one of these verbs, then assume the return type is None
# - The starting word or words with a training space
NONE_VERBS = [
    "Activate ",
    "Build a ",
    "Cancel ",
    "Clear ",
    "Close ",
    "cancel ",
    "Configure ",
    "Connect ",
    "Deactivate ",
    "De-initialises ",
    "Deinitialises ",
    "Delay ",
    "Disable ",
    "Display ",
    "Disconnect ",
    "Draw ",
    "Enable ",
    "Feed the ",
    "Fill the ",
    "Generate ",
    "Initialise the ",
    "Initialize ",  # US/UK spelling
    "Issue a ",
    "Load ",
    "Modify ",
    "Print ",
    "Register ",
    "Remove ",
    "Rename ",
    "Reset ",
    "Resets ",
    "Send ",
    "Sends ",
    "Set Pin ",
    "Set the ",
    "Sets",
    "Show ",
    "Stop ",
    "Stops ",
    "Sync ",
    "Turn ",
    "Wait ",
    "Write ",
    "Writes ",
]

# Add additional imports to generated modules
# - to allow one module te refer to another,
# - to import other supporting modules
# - to add missing abstract classes
# - to add TypeAliases and TypeVars

# avoid defining AnyReadableBuf and AnyWritableBuf in m modules
ANY_BUF = ["from _mpy_shed import AnyReadableBuf, AnyWritableBuf"]

MODULE_GLUE = {
    "array": ['_T = TypeVar("_T", int, float, str)'],
    "asyncio": ANY_BUF,
    "bluetooth": ANY_BUF
    + [
        "from _mpy_shed import _IRQ",
    ],
    "collections": [
        "from queue import Queue",
        # "from _mpy_shed.collections import namedtuple as stdlib_namedtuple  # type: ignore",
        '_KT = TypeVar("_KT")',
        '_VT = TypeVar("_VT")',
    ],
    "cmath": [
        "from typing_extensions import TypeAlias",
        # "_C: TypeAlias = SupportsFloat | SupportsComplex | SupportsIndex | complex",
    ],
    "cryptolib": ANY_BUF,
    "esp": ANY_BUF,
    "espnow": [
        "from _espnow import ESPNowBase  # type: ignore",
    ],  # ESPNowBase is an undocumented base class
    "framebuf": ANY_BUF,
    "hashlib": ANY_BUF
    + [
        "from _mpy_shed import _Hash",
    ],
    "heapq": [
        '_T = TypeVar("_T")',
    ],
    "io": ANY_BUF
    + [
        "from _mpy_shed import IOBase_mp",
    ],
    "lcd160cr": ANY_BUF + ["from pyb import SPI"],  # uses SPI
    # "machine": ["from network import AbstractNIC"],  # NIC is an abstract class, although not defined or used as such
    "machine.ADC": [
        "from .Pin import Pin",
        "ATTN_0DB:int = ...",
    ],
    "machine.I2C": ANY_BUF + ["from .Pin import Pin"],  #  uses Pin
    "machine.I2S": ANY_BUF + ["from .Pin import Pin"],
    "machine.PWM": ANY_BUF + ["from .Pin import Pin"],
    "machine.RTC": [
        "from machine import IDLE",
    ],
    "machine.SD": ["from .Pin import Pin"],  #  uses Pin
    "machine.SDCard": ["from .Pin import Pin"],  #  uses Pin
    "machine.Signal": ["from .Pin import Pin"],  #  uses Pin
    "machine.SPI": ANY_BUF + ["from .Pin import Pin"],  #  uses Pin
    "machine.UART": ANY_BUF
    + [
        "from machine import IDLE",
        "from .Pin import Pin",
        "from _mpy_shed import _IRQ",
    ],  #  uses Pin
    "micropython": [
        "from typing import Tuple, Final",
        "from typing_extensions import TypeVar",
        '_T = TypeVar("_T")',
        '_F = TypeVar("_F", bound=Callable[..., Any])',
        'Const_T = TypeVar("Const_T", int, float, str, bytes, Tuple)  # constant',
    ],
    "network": ["from typing import Protocol"],  #  for AbstractNIC
    "neopixel": [
        "from _mpy_shed import _NeoPixelBase",
    ],  #  for AbstractNIC
    "os": [
        "from _mpy_shed import uname_result",
    ],
    "pyb": ANY_BUF
    + [
        "from .UART import UART",
        "from _mpy_shed import _OldAbstractBlockDev, _OldAbstractReadOnlyBlockDev, HID_Tuple",
    ],
    "pyb.ADC": ANY_BUF + ["from .Pin import Pin", "from .Timer import Timer"],
    "pyb.CAN": ANY_BUF,
    "pyb.DAC": ANY_BUF
    + [
        "from .Pin import Pin",
        "from .Timer import Timer",
    ],
    "pyb.ExtInt": ["from .Pin import Pin"],
    "pyb.I2C": ANY_BUF,
    "pyb.SPI": ANY_BUF,
    "pyb.UART": ANY_BUF,
    "pyb.USB_HID": ANY_BUF,
    "pyb.USB_VCP": ANY_BUF,
    "pyb.Switch": ["from .Pin import Pin"],  #  uses Pin
    "pyb.Timer": [
        "from abc import ABC, abstractmethod",
        "from .Pin import Pin",
    ],  #  uses Pin
    "_rp2.DMA": ["from _mpy_shed import _IRQ"],
    "_rp2.PIO": ["from _mpy_shed import _IRQ"],
    "rp2.PIO": ["from _mpy_shed import _IRQ"],
    "rp2.DMA": ["from _mpy_shed import _IRQ"],
    "socket": [
        "from typing_extensions import TypeAlias",
        "from _mpy_shed import AnyReadableBuf, AnyWritableBuf",
    ],
    "ssl": [
        "from typing_extensions import TypeAlias",
        "from _mpy_shed import StrOrBytesPath",
        # SSLSocket is part of the refence stubs
    ],
    "struct": ANY_BUF,
    "time": [
        "from typing_extensions import TypeAlias, TypeVar",
        "_TicksMs: TypeAlias = int",
        "_TicksUs: TypeAlias = int",
        "_TicksCPU: TypeAlias = int",
        '_Ticks = TypeVar("_Ticks", _TicksMs, _TicksUs, _TicksCPU, int)',
    ],
    "uctypes": ANY_BUF
    + [
        # "from typing_extensions import TypeAlias",
        # "_ScalarProperty: TypeAlias = int",
        # "_RecursiveProperty: TypeAlias = tuple[int, _property]",
        # "_ArrayProperty: TypeAlias = tuple[int, int]",
        # "_ArrayOfAggregateProperty: TypeAlias = tuple[int, int, _property]",
        # "_PointerToAPrimitiveProperty: TypeAlias = tuple[int, int]",
        # "_PointerToAaAggregateProperty: TypeAlias = tuple[int, _property]",
        # "_BitfieldProperty: TypeAlias = int",
        # "_property: TypeAlias = _ScalarProperty | _RecursiveProperty | _ArrayProperty | _ArrayOfAggregateProperty | _PointerToAPrimitiveProperty | _PointerToAaAggregateProperty | _BitfieldProperty",
        # "_descriptor: TypeAlias = tuple[str, _property]",
    ],
}


PARAM_FIXES = [
    Fix("\\*", "*"),  # change weirdly written wildcards \* --> *
    Fix(r"\**", "*"),  # change weirdly written wildcards \* --> *
    Fix(r"/*", "*"),  # change weirdly written wildcards /* --> *
    Fix(r"**", "*"),  # change weirdly written wildcards ** --> *
    # do not remove / , this indicates positional only notation before the ,/
    # RE to insert missing , before /
    Fix(from_=r"(\w+.*?[^,])\s*/", to=r"\1 ,/", is_re=True),
    Fix(",  ,/", ", /"),  # remove double commas ( cause by the above fix) its a kludge
    # Fix("]=None /)", "]=None, /)")
    # ref: https://regex101.com/r/crVQfA/1
    Fix("'param'", "param"),  # loose notation in documentation
    # illegal keywords
    Fix(
        "lambda",
        "lambda_fn",
    ),
    # method:: ADC.read_timed_multi((adcx, adcy, ...), (bufx, bufy, ...), timer)
    Fix(
        "(adcx, adcy, ...), (bufx, bufy, ...)",
        "adcs, bufs",
    ),
    # network.AbstractNIC
    # ifconfig([(ip, subnet, gateway, dns)])
    Fix(
        "(ip, subnet, gateway, dns)",
        "configtuple",
    ),
    # pyb.hid((buttons, x, y, z))
    Fix(
        "(buttons, x, y, z)",
        "hid_tuple:HID_Tuple",
    ),
    # esp v1.15.2 .. function:: getaddrinfo((hostname, port, lambda))
    Fix(
        "(hostname, port, lambda)",
        "tuple[str,int,Callable]",
    ),
    # # network
    # # WLANWiPy.ifconfig(if_id=0, config=['dhcp' or configtuple])
    # Fix(
    #     "config=['dhcp' or configtuple]",
    #     "config: Union[str,Tuple]='dhcp'"
    # ),
    Fix(
        "config='dhcp' or configtuple: Optional[Any]=None",
        "config: Union[str,Tuple]='dhcp'",
    ),
    # (
    #     "='dhcp' or configtuple: Optional[Any]=None",
    #     ": Union[str,Tuple]='dhcp'",
    # ),
    # network
    # CC3K.patch_program('pgm')
    Fix(
        "'pgm')",
        "cmd:str ,/)",
    ),
    # network
    Fix(
        "block_device or path",
        "block_device_or_path",
    ),  #
    # network
    # ifconfig
    Fix(
        "(ip, subnet, gateway, dns):Optional[Any]=None",
        "configtuple: Optional[Tuple]",
    ),
    # network.ipconfig
    Fix(
        "param=value",
        "param:Optional[str]=None",
        name="ipconfig",
    ),
    # framebuffer
    # unresolvable parameter defaults # FrameBuffer: def __init__
    Fix(
        "stride=width",
        "stride=-1",
    ),
    # machine.Pin.__init__ constructor - Defaults assumed from the documentation.
    # fixed in doc v1.18+
    Fix(
        ", value, drive, alt",
        ", value=None, drive=0, alt=-1",
    ),
    # machine.Pin.irq ...
    Fix(
        "trigger=(IRQ_FALLING | IRQ_RISING)",
        "trigger=IRQ_FALLING ",
    ),
    ## fixes for machine.py class constants
    # # BUG: This is not OK
    Fix(
        "pins=(SCK, MOSI, MISO)",
        "pins:Optional[Tuple]",
    ),  #
    ## rp2.PIO.irq
    # Fix( No longer needed with py 3.10 notation
    #     "trigger=IRQ_SM0|IRQ_SM1|IRQ_SM2|IRQ_SM3",
    #     "trigger=IRQ_SM0",
    # ),
    # SPI.INIT - to fix error: Non-default argument follows default argument
    # ✅ fixed in doc v1.18+
    Fix(
        "prescaler, polarity=1",
        "prescaler=1, polarity=1",
    ),
    # network.LAN.init
    # def __init__(self, id, *, phy_type=<board_default>, phy_addr=<board_default>, phy_clock=<board_default>) -> None:
    Fix("=<board_default>", "=0"),
    # ssl
    # def wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True) -> Any:
    Fix("cert_reqs=CERT_NONE", "cert_reqs=None"),
    # struct.pack & pack_into
    # def pack(fmt, v1, v2, *args) -> bytes:
    Fix(", v1, v2,", ", v1,"),
    # esp32.RMT
    #     # def write_pulses(self, duration, data=True) -> Any:
    #     def write_pulses(self, duration, data:Union[bool,int]=True) -> Any:
    Fix(
        "duration, data=True",
        "duration, data:Union[bool,int]=True",
    ),
    # --------------------------------------------------------------------
    # machine
    # machine.PWM
    #     # def __init__(self, dest, *, freq, duty_u16, duty_ns) -> None: ...
    #     def __init__(self, dest, *, freq=0,duty=0, duty_u16=0, duty_ns=0) -> None: ...
    Fix(
        "dest, *, freq, duty_u16, duty_ns, invert",
        "dest, *, freq=0,duty=0, duty_u16=0, duty_ns=0, invert=False",
    ),
    # most specific fix first
    Fix(
        "dest, *, freq, duty_u16, duty_ns",
        "dest, *, freq=0,duty=0, duty_u16=0, duty_ns=0",
    ),
    # machine.ADC
    #     # def __init__(self, id, *, sample_ns, atten) -> None: ...
    #     def __init__(self, id, *, sample_ns:Optional[int]=0, atten:Optional[int]=ATTN_0DB) -> None: ...
    Fix(
        "id, *, sample_ns, atten",
        "id, *, sample_ns:Optional[int]=0, atten:Optional[int]=ATTN_0DB",
    ),
    # machine.I2C
    #     # def __init__(self, id, *, scl, sda, freq=400000) -> None: ...
    #     def __init__(self, id=-1, *, scl:Optional[Pin]=None, sda:Optional[Pin]=None, freq=400000) -> None: ...
    Fix(
        "id, *, scl, sda, freq=400000",
        "id:Union[int,str]=-1, *, scl:Optional[Union[Pin,str]]=None, sda:Optional[Union[Pin,str]]=None, freq=400_000",
    ),
    # network.WLAN
    # def config(self, param) -> Any:
    # def config(self, *args, **kwargs) -> Any:
    Fix(
        "param",
        "*args, **kwargs",
        name="WLAN.config",
    ),
    # machine.UART
    #     def __init__(self, id, ...) -> None: ...
    #     def __init__(self, id, *args, **kwargs) -> None: ...
    Fix(
        "id, ...",
        "id, *args, **kwargs",
        name="UART.__init__",
    ),
    # machine.SPI
    #     #    def __init__(self, id, *args) -> None: ...
    #     def __init__(self, id, *args, **kwargs) -> None: ...
    Fix("id, ...", "id, *args, **kwargs", name="SPI.__init__"),
    # machine.Signal
    # def __init__(self, pin_obj, invert=False) -> None: ...
    # def __init__(self, pin_obj, *args, invert=False) -> None: ...
    Fix("pin_obj, invert", "pin_obj, *args, invert", name="Signal.__init__"),
    # machine.Timer
    # def __init__(self, id, /, *args) -> None: ...
    # def init(self,id, *, mode=PERIODIC, period=-1, callback=None) -> None: ...
    Fix("id, /, ...", "id=-1, *args, **kwargs", name="Timer.__init__"),
    # --------------------------------------------------------------------
    # pyb
    # def freq(sysclk, hclk, pclk1, pclk2) -> Tuple:
    # def freq(sysclk=0, hclk=0, pclk1=0, pclk2=0) -> Tuple:
    Fix("sysclk, hclk, pclk1, pclk2", "sysclk=0, hclk=0, pclk1=0, pclk2=0"),
    # Timer.__init__
    # def __init__(self, id, *args) -> None: ...
    # def __init__(self, id, *, freq=..., prescaler=..., period=..., mode=UP, div=1, callback=None, deadtime=0) -> None:
    Fix(
        "id, *args",
        "id, *, freq=-1, prescaler=-1, period=-1, mode=UP, div=1, callback=None, deadtime=0",
        name="Timer.__init__",
    ),
    # Timer.channel
    # def channel(self, channel, mode, *args) -> Any:
    # def channel(self, channel, mode, pin=None, *args) -> Any:
    Fix("channel, mode, ...", "channel, mode, pin=None, *args"),
    # pyb SPI
    # def __init__(self, bus, *args) -> None: ...
    # def __init__(self,bus,  mode, baudrate=328125, *, prescaler=-1, polarity=1, phase=0, bits=8, firstbit=MSB, ti=False, crc=None) -> None:
    Fix(
        "bus, ...",
        "bus,  mode, baudrate=328125, *, prescaler=-1, polarity=1, phase=0, bits=8, firstbit=MSB, ti=False, crc=None",
    ),
    # PYB CAN.setfiler
    # def setfilter(self, bank, mode, fifo, params, *, rtr, extframe=False) -> None:
    # def setfilter(self, bank, mode, fifo, params, *, rtr=..., extframe=False) -> None:
    Fix(
        "bank, mode, fifo, params, *, rtr, extframe=False",
        "bank, mode, fifo, params, *, rtr=None, extframe=False",
    ),
    # DOC: DocUpdate ? deal with overloads for Flash and Partition .readblock/writeblocks
    Fix(
        r"\s*block_num, buf, offset\s*\)",
        "block_num, buf, offset: Optional[int] = 0)",
        is_re=True,
    ),
    # # This is a cleanup something that went wrong before
    # Fix("**kwargs: Optional[Any]","**kwargs")
    # os.mount - optional parameters
    # fsobj, mount_point, *, readonly)
    Fix(
        "fsobj, mount_point, *, readonly)",
        "fsobj, mount_point, *, readonly=False)",
    ),
    # micropython.const
    Fix("expr)", "expr:Const_T)", name="const"),  # const: 3 - paired with return typing,
    # ------ ESPNow.rst uses   (ESP32 only) after the class / function prototype
    Fix(r"\(ESP\d+\s+only\)", "", is_re=True),  # ESP32 / ESP8266 Only
    # espnow.ESPNow.send is missing several params
    Fix(
        "msg)",
        "peer, msg,mac=None,sync=True)",
        name="ESPNow.send",
    ),
    Fix(
        "msg)",
        "peer, msg,mac=None,sync=True)",
        name="ESPNow.asend",
    ),
]

# and some param fixes that require a regex
PARAM_RE_FIXES = [
    Fix(
        r"\[angle, time=0\]", "[angle], time=0", is_re=True
    ),  # fix: method:: Servo.angle([angle, time=0])
    Fix(
        r"\[speed, time=0\]", "[speed], time=0", is_re=True
    ),  # fix: .. method:: Servo.speed([speed, time=0])
    Fix(
        r"\[service_id, key=None, \*, \.\.\.\]", "[service_id], [key], *, ...", is_re=True
    ),  # fix: network - AbstractNIC.connect
]
# List of classes and their parent classes that should be added to the class definition
CHILD_PARENT_CLASS = {
    # machine
    "SoftSPI": "SPI",
    "SoftI2C": "I2C",
    "Switch": "Pin",
    "Signal": "Pin",
    # uio # unclear regarding deprecation in python 3.12
    # "IOBase": "IO",  # DOC_ME  not in documentation
    "TextIOWrapper": "IO",  # "TextIOBase, TextIO",  # based on Stdlib
    "FileIO": "IO",  #  "RawIOBase, BinaryIO",  # based on Stdlib
    "StringIO": "IO",  #  "BufferedIOBase, BinaryIO",  # based on Stdlib
    "IOBase": "IOBase_mp",  # "BufferedIOBase, BinaryIO",  # based on Stdlib
    "BytesIO": "IO",  # "BufferedIOBase, BinaryIO",  # based on Stdlib
    "BufferedWriter": "IOBase_mp",  # DOC_ME: not in documentation #   "BufferedWriter": "BufferedIOBase",  # based on Stdlib
    # uzlib
    # "DecompIO": "IO",  # https://docs.python.org/3/library/typing.html#other-concrete-types
    # -------------------------------------------------------------------------------------
    # network - AbstractNIC is defined in docstub network.pyi , but not actually used
    # "WLAN": "AbstractNIC",
    # "WLANWiPy": "AbstractNIC",
    # "CC3K": "AbstractNIC",
    # "WIZNET5K": "AbstractNIC",
    # -------------------------------------------------------------------------------------
    # uhashlib
    #  "md5": "hash",   # BUG: hash is not defined in the MCU stubs
    # "sha1": "hash",
    # "sha256": "hash",
    # collections
    "OrderedDict": "stdlib_OrderedDict",
    "namedtuple": "tuple",
    "deque": "stdlib_deque",
    # ESPNow
    "ESPNow": "ESPNowBase, Iterator",  # causes issue with mypy
    "AIOESPNow": "ESPNow",
    # array
    "array": "List",
    # network
    "AbstractNIC": "Protocol",
    # neopixel
    "NeoPixel": "_NeoPixelBase",
}


# TODO : implement the execution of this list during merge
#  - this is a list of functions, classes methods and constants  that are not detected at runtime, but are available and documented
# the standard merge only adds documentation to detected functions.
FORCE_NON_DETECTED = [
    ("btree", "Btree", ["esp32", "esp8266"]),  # Is not detected runtime
    ("espnow", "ESPNow.peers_table", ["esp32"]),  # Is not detected runtime
]
