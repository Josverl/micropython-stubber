"""
this is an list with manual overrides for function returns that could not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = module.[class.]function name
- value : two-tuple with ( return type , priority )

"""
# These are shown to import
__all__ = ["LOOKUP_LIST", "NONE_VERBS", "CHILD_PARENT_CLASS", "PARAM_FIXES", "MODULE_GLUE"]

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
}

# manual fixes needed for parameters ( micropython v.16 & v1.17)
PARAM_FIXES = [
    ("\\*", "*"),  # change weirdly written wildcards \* --> *
    (r"\**", "*"),  # change weirdly written wildcards \* --> *
    (r"/*", "*"),  # change weirdly written wildcards \* --> *
    ("**", "*"),  # change weirdly written wildcards \* --> *
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
    (
        "cert_reqs=CERT_NONE",
        "cert_reqs=None",
    ),  # .. function:: ussl.wrap_socket(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=CERT_NONE, ca_certs=None, do_handshake=True)
    (
        "='dhcp' or configtuple: Optional[Any]",
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
        "(ip, subnet, gateway, dns):Optional[Any]",
        "config: Optional[Tuple]",
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
    (
        "trigger=IRQ_SM0 | IRQ_SM1 | IRQ_SM2 | IRQ_SM3",
        "trigger=IRQ_SM0",
    ),  ## rp2.PIO.irq
    #            (), #
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
}
