"""
this is an list with manual overrides for function returns that could not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = module.[class.]function name
- value : two-tuple with ( return type , priority )

"""
# These are shown to import
__all__ = [
    "LOOKUP_LIST",
    "NONE_VERBS",
    "CHILD_PARENT_CLASS",
    "PARAM_FIXES",
    "MODULE_GLUE",
    "RST_DOC_FIXES",
    "DOCSTUB_SKIP",
    "U_MODULES",
]


# modules documented with base name only
U_MODULES = [
    "os",
    "time",
    "array",
    "binascii",
    "io",
    "json",
    "select",
    "socket",
    "ssl",
    "struct",
    "zlib",
]


# Some classes are documented as functions
# This table is used to try to correct the errors in the documentation.
# it is applied to each .rst file after loading the contents.

RST_DOC_FIXES = [
    # ------------------------------------------------------------------------------------------------
    # re.rst - function and class with the same name
    # todo: issue https://github.com/micropython/micropython/issues/8273
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
]

# docstubs generation, exclude stub generation for below stubs.
DOCSTUB_SKIP = [
    "uasyncio.rst",  # can create better stubs from frozen python modules.
    "builtins.rst",  # conflicts with static type checking , has very little information anyway
    "re.rst",  # regex is too complex
]

# contains return types for functions and methods that are not clearly documented.
LOOKUP_LIST = {
    "builtins.bytes": ("bytes", 0.95),
    "builtins.from_bytes": ("int", 0.95),
    "builtins.to_bytes": ("bytes", 0.95),
    "bytearray_at": ("bytearray", 0.95),
    "gc.collect": ("None", 0.95),
    "machine.deepsleep": ("NoReturn", 0.95),
    "machine.reset_cause": ("int", 0.95),
    "machine.reset": ("NoReturn", 0.95),  # never returns
    "machine.Signal.value": ("int", 0.95),
    "machine.soft_reset": ("NoReturn", 0.95),  # never returns
    "machine.UART.irq": ("Any", 0.95),  # no IRQ type defined
    "math.isnan": ("bool", 0.95),
    "micropython.opt_level": ("Any", 0.95),  # Not clear in docstring
    "micropython.const": ("int", 0.95),  # const is always an int
    "pyb.hard_reset": ("NoReturn", 0.95),  # never returns
    "pyb.I2C.recv": ("bytes", 0.95),  # complex in docstring
    "pyb.SPI.recv": ("bytes", 0.95),  # complex in docstring
    "ubluetooth.BLE.irq": ("Any", 0.95),  # never returns
    "uctypes.bytearray_at": ("bytearray", 0.95),
    "uctypes.bytes_at": ("bytes", 0.95),
    "uio.open": ("IO", 0.95),  #  Open a file.
    "uos.listdir": ("List[Any]", 0.95),
    "os.uname": ("uname_result", 0.95),
    "ussl.ussl.wrap_socket": ("IO", 0.95),  # undocumented class ssl.SSLSocket
    "usys.exit": ("NoReturn", 0.95),  # never returns
    "utime.sleep_ms": (
        "Coroutine[None, None, None]",  # Micropython V1.15+ ?
        0.95,
    ),
    "stm.mem8": ("bytearray", 0.95),  # Read/write 8 bits of memory.
    "stm.mem16": ("bytearray", 0.95),  # Read/write 16 bits of memory.
    "stm.mem32": ("bytearray", 0.95),  # Read/write 32 bits of memory.
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

MODULE_GLUE = {
    "lcd160cr": ["from .machine import SPI"],  # module returns SPI objects defined in machine
    "esp32": ["from __future__ import annotations"],  # Class methods return Class
    "collections": ["from queue import Queue"],  # dequeu is a subclass
    "os": ["from stdlib.os import uname_result"],  # uname returns uname_result
    # "machine": ["from network import AbstractNIC"],  # NIC is an abstract class, although not defined or used as such
}

# manual fixes needed for parameters ( micropython v.16 & v1.17)
# [
#   ( "from", "to"),
#   ( "from", "to", "optional function, Class or Class.Method"),
# ]
PARAM_FIXES = [
    ("\\*", "*"),  # change weirdly written wildcards \* --> *
    (r"\**", "*"),  # change weirdly written wildcards \* --> *
    (r"/*", "*"),  # change weirdly written wildcards \* --> *
    # ("**", "*"),  # change weirdly written wildcards \* --> *
    ("'param'", "param"),  # loose notation in documentation
    # illegal keywords
    (
        "lambda",
        "lambda_fn",
    ),
    # method:: ADC.read_timed_multi((adcx, adcy, ...), (bufx, bufy, ...), timer)
    (
        "(adcx, adcy, ...), (bufx, bufy, ...)",
        "adcs, bufs",
    ),
    # network.AbstractNIC
    # ifconfig([(ip, subnet, gateway, dns)])
    (
        "(ip, subnet, gateway, dns)",
        "configtuple",
    ),
    # pyb.hid((buttons, x, y, z))
    (
        "(buttons, x, y, z)",
        "hidtuple:Tuple",
    ),
    # esp v1.15.2 .. function:: getaddrinfo((hostname, port, lambda))
    (
        "(hostname, port, lambda)",
        "tuple[str,int,Callable]",
    ),
    # ussl. TODO
    # wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True)
    # (
    #     "cert_reqs=CERT_NONE",
    #     "cert_reqs=None",
    # ),
    # network
    # WLANWiPy.ifconfig(if_id=0, config=['dhcp' or configtuple])
    (
        "='dhcp' or configtuple: Optional[Any]=None",
        ": Union[str,Tuple]='dhcp'",
    ),
    # network
    # CC3K.patch_program('pgm')
    (
        "'pgm')",
        "cmd:str ,/)",
    ),
    # network
    (
        "block_device or path",
        "block_device_or_path",
    ),  #
    # network
    # ifconfig
    (
        "(ip, subnet, gateway, dns):Optional[Any]=None",
        "configtuple: Optional[Tuple]",
    ),
    # framebuffer
    # unresolvable parameter defaults # FrameBuffer: def __init__
    (
        "stride=width",
        "stride=-1",
    ),
    # machine.Pin.__init__ constructor - Defaults assumed from the documentation.
    # fixed in doc v1.18+
    (
        ", value, drive, alt",
        ", value=None, drive=0, alt=-1",
    ),
    # machine.Pin.irq ...
    (
        "trigger=(IRQ_FALLING | IRQ_RISING)",
        "trigger=IRQ_FALLING ",
    ),
    ## fixes for machine.py class constants
    # # BUG: This is not OK
    (
        "pins=(SCK, MOSI, MISO)",
        "pins:Optional[Tuple]",
    ),  #
    ## rp2.PIO.irq
    (
        "trigger=IRQ_SM0|IRQ_SM1|IRQ_SM2|IRQ_SM3",
        "trigger=IRQ_SM0",
    ),
    # SPI.INIT - to fix error: Non-default argument follows default argument
    # ✅ fixed in doc v1.18+
    (
        "prescaler, polarity=1",
        "prescaler=1, polarity=1",
    ),
    # network.LAN.init
    # def __init__(self, id, *, phy_type=<board_default>, phy_addr=<board_default>, phy_clock=<board_default>) -> None:
    ("=<board_default>", "=0"),
    # ssl
    # def wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True) -> Any:
    ("cert_reqs=CERT_NONE", "cert_reqs=None"),
    # struct.pack & pack_into
    # def pack(fmt, v1, v2, *args) -> bytes:
    (", v1, v2,", ", v1,"),
    # esp32.RMT
    #     # def write_pulses(self, duration, data=True) -> Any:
    #     def write_pulses(self, duration, data:Union[bool,int]=True) -> Any:
    ("duration, data=True", "duration, data:Union[bool,int]=True"),
    # --------------------------------------------------------------------
    # machine
    # machine.PWM
    #     # def __init__(self, dest, *, freq, duty_u16, duty_ns) -> None: ...
    #     def __init__(self, dest, *, freq=0,duty=0, duty_u16=0, duty_ns=0) -> None: ...
    ("dest, *, freq, duty_u16, duty_ns", "dest, *, freq=0,duty=0, duty_u16=0, duty_ns=0"),
    # machine.ADC
    #     # def __init__(self, id, *, sample_ns, atten) -> None: ...
    #     def __init__(self, id, *, sample_ns:Optional[int]=0, atten:Optional[int]=ATTN_0DB) -> None: ...
    ("id, *, sample_ns, atten", "id, *, sample_ns:Optional[int]=0, atten:Optional[int]=ATTN_0DB"),
    # machine.I2C
    #     # def __init__(self, id, *, scl, sda, freq=400000) -> None: ...
    #     def __init__(self, id=-1, *, scl:Optional[Pin]=None, sda:Optional[Pin]=None, freq=400000) -> None: ...
    (
        "id, *, scl, sda, freq=400000",
        "id:Union[int,str]=-1, *, scl:Optional[Union[Pin,str]]=None, sda:Optional[Union[Pin,str]]=None, freq=400_000",
    ),
    # network.WLAN
    # def config(self, param) -> Any:
    # def config(self, *args, **kwargs) -> Any:
    ("param", "*args, **kwargs", "WLAN.config"),
    # machine.UART
    #     def __init__(self, id, ...) -> None: ...
    #     def __init__(self, id, *args, **kwargs) -> None: ...
    ("id, ...", "id, *args, **kwargs", "UART.__init__"),
    # machine.SPI
    #     #    def __init__(self, id, *args) -> None: ...
    #     def __init__(self, id, *args, **kwargs) -> None: ...
    ("id, ...", "id, *args, **kwargs", "SPI.__init__"),
    # machine.Signal
    # def __init__(self, pin_obj, invert=False) -> None: ...
    # def __init__(self, pin_obj, *args, invert=False) -> None: ...
    ("pin_obj, invert", "pin_obj, *args, invert", "Signal.__init__"),
    # machine.Timer
    # def __init__(self, id, /, *args) -> None: ...
    # def init(self,id, *, mode=PERIODIC, period=-1, callback=None) -> None: ...
    ("id, /, ...", "id=-1, *args, **kwargs", "Timer.__init__"),
    # --------------------------------------------------------------------
    # pyb
    # def freq(sysclk, hclk, pclk1, pclk2) -> Tuple:
    # def freq(sysclk=0, hclk=0, pclk1=0, pclk2=0) -> Tuple:
    ("sysclk, hclk, pclk1, pclk2", "sysclk=0, hclk=0, pclk1=0, pclk2=0"),
    # Timer.__init__
    # def __init__(self, id, *args) -> None: ...
    # def __init__(self, id, *, freq=..., prescaler=..., period=..., mode=UP, div=1, callback=None, deadtime=0) -> None:
    (
        "id, *args",
        "id, *, freq=-1, prescaler=-1, period=-1, mode=UP, div=1, callback=None, deadtime=0",
        "Timer.__init__",
    ),
    # Timer.channel
    # def channel(self, channel, mode, *args) -> Any:
    # def channel(self, channel, mode, pin=None, *args) -> Any:
    ("channel, mode, ...", "channel, mode, pin=None, *args"),
    # pyb SPI
    # def __init__(self, bus, *args) -> None: ...
    # def __init__(self,bus,  mode, baudrate=328125, *, prescaler=-1, polarity=1, phase=0, bits=8, firstbit=MSB, ti=False, crc=None) -> None:
    (
        "bus, ...",
        "bus,  mode, baudrate=328125, *, prescaler=-1, polarity=1, phase=0, bits=8, firstbit=MSB, ti=False, crc=None",
    ),
    # PYB CAN.setfiler
    # def setfilter(self, bank, mode, fifo, params, *, rtr, extframe=False) -> None:
    # def setfilter(self, bank, mode, fifo, params, *, rtr=..., extframe=False) -> None:
    (
        "bank, mode, fifo, params, *, rtr, extframe=False",
        "bank, mode, fifo, params, *, rtr=None, extframe=False",
    ),
]

# List of classes and their parent classes that should be added to the class definition
CHILD_PARENT_CLASS = {
    # machine
    "SoftSPI": "SPI",
    "SoftI2C": "I2C",
    "Switch": "Pin",
    # uio # unclear regarding deprecation in python 3.12
    "FileIO": "IO",
    "textIOWrapper": "IO",
    "StringIO": "IO",
    "BytesIO": "IO",
    # uzlib
    "DecompIO": "IO",  # https://docs.python.org/3/library/typing.html#other-concrete-types
    # -------------------------------------------------------------------------------------
    # network - AbstractNIC is definined in docstub network.pyi , but not actually used
    # "WLAN": "AbstractNIC",
    # "WLANWiPy": "AbstractNIC",
    # "CC3K": "AbstractNIC",
    # "WIZNET5K": "AbstractNIC",
    # -------------------------------------------------------------------------------------
    # uhashlib
    "md5": "hash",
    "sha1": "hash",
    "sha265": "hash",
    # collections
    "OrderedDict": "dict",
    "namedtuple": "tuple",
    "deque": "Queue",
}
