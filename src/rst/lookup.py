"""
this is an list with manual overrides for function returns that could not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = module.[class.]function name
- value : two-tuple with ( return type , priority )

"""
# These are shown to import
__all__ = ["LOOKUP_LIST", "NONE_VERBS", "CHILD_PARENT_CLASS", "PARAM_FIXES", "MODULE_GLUE", "RST_DOC_FIXES"]

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
    "machine.deepsleep": ("None", 0.95),
    "machine.reset_cause": ("int", 0.95),
    "machine.reset": ("NoReturn", 0.95),  # never returns
    "machine.Signal.value": ("int", 0.95),
    "machine.soft_reset": ("NoReturn", 0.95),  # never returns
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
    "ussl.ussl.wrap_socket": ("IO", 0.95),  # undocumented class ssl.SSLSocket
    "usys.exit": ("NoReturn", 0.95),  # never returns
    "utime.sleep_ms": (
        "Coroutine[None, None, None]",  # Micropython V1.15+ ?
        0.95,
    ),  # class typing.Coroutine(Awaitable[V_co], Generic[T_co, T_contra, V_co])
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

# Add additional imports to generated modules to allow one module te refer to another,
# or to import other supporting modules
MODULE_GLUE = {
    "lcd160cr": ["from .machine import SPI"],  # module returns SPI objects defined in machine
    "esp32": ["from __future__ import annotations"],  # Class methods return Class
    "collections": ["from queue import Queue"],  # dequeu is a subclass
}

# manual fixes needed for parameters ( micropython v.16 & v1.17)
PARAM_FIXES = [
    ("\\*", "*"),  # change weirdly written wildcards \* --> *
    (r"\**", "*"),  # change weirdly written wildcards \* --> *
    (r"/*", "*"),  # change weirdly written wildcards \* --> *
    # ("**", "*"),  # change weirdly written wildcards \* --> *
    ("'param'", "param"),  # loose notation in documentation
    (
        "(adcx, adcy, ...), (bufx, bufy, ...)",
        "adcs, bufs",
    ),  # method:: ADC.read_timed_multi((adcx, adcy, ...), (bufx, bufy, ...), timer)
    (
        "(ip, subnet, gateway, dns)",
        "configtuple",
    ),  # network: # .. method:: AbstractNIC.ifconfig([(ip, subnet, gateway, dns)])
    (
        "(buttons, x, y, z)",
        "hidtuple",
    ),  # pyb  .. function:: hid((buttons, x, y, z))
    (
        "(hostname, port, lambda)",
        "tuple",
    ),  # esp v1.15.2 .. function:: getaddrinfo((hostname, port, lambda))
    # (
    #     "cert_reqs=CERT_NONE",
    #     "cert_reqs=None",
    # ),  # .. function:: ussl.wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True)
    (
        "='dhcp' or configtuple: Optional[Any]=None",
        ": Union[str,Tuple]='dhcp'",
    ),  # network.rst method:: WLANWiPy.ifconfig(if_id=0, config=['dhcp' or configtuple])
    (
        "'pgm')",
        "cmd:str ,/)",
    ),  # network.rst .. method:: CC3K.patch_program('pgm')
    (
        "block_device or path",
        "block_device_or_path",
    ),  #
    (
        "(ip, subnet, gateway, dns):Optional[Any]=None",
        "configtuple: Optional[Tuple]",
    ),  # ifconfig
    (
        "lambda",
        "lambda_fn",
    ),  # illegal keywords
    (
        "stride=width",
        "stride=-1",
    ),  # # unresolvable parameter defaults # FrameBuffer: def __init__
    (
        "trigger=(IRQ_FALLING | IRQ_RISING)",
        "trigger=IRQ_FALLING ",
    ),  ## fixes for machine.py class constants
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
    # TODO: Upstream Fix
    # PR: https://github.com/micropython/micropython/pull/7976
    (
        "prescaler, polarity=1",
        "prescaler=1, polarity=1",
    ),
    # machine.Pin.__init__ constructor - Defaults assumed from the documentation.
    # # TODO: Pin init differs per port : Search '// pin.init' in micropython repo for
    # PR: https://github.com/micropython/micropython/pull/7976
    # https://github.com/micropython/micropython/blob/b47b245c2eeb734f69d5445372d0947f1ea43259/ports/stm32/pin.c#L331-L339
    (
        ", value, drive, alt",
        ", value=None, drive=0, alt=-1",
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
    # network
    "WLAN": "AbstractNIC",
    "WLANWiPy": "AbstractNIC",
    # uhashlib
    "md5": "hash",
    "sha1": "hash",
    "sha265": "hash",
    # collections
    "OrderedDict": "dict",
    "namedtuple": "tuple",
    "deque": "Queue",  # TODO: Check if this is correct
}
