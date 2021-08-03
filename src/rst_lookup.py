"""
this is an list with manual overrides for function returns that could not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = module.[class.]function name
- value : two-tuple with ( return type , priority )

"""


LOOKUP_LIST = {
    "uctypes.bytearray_at": ("bytearray", 0.95),
    "math.isnan": ("bool", 0.95),
    "builtins.to_bytes": ("bytes", 0.95),
    "builtins.from_bytes": ("int", 0.95),
    "builtins.bytes": ("bytes", 0.95),
    "uctypes.bytes_at": ("bytes", 0.95),
    "bytearray_at": ("bytearray", 0.95),
    "uos.listdir": ("List[Any]", 0.95),
    "gc.enable": ("None", 0.95),
    "gc.disable": ("None", 0.95),
    "gc.collect": ("None", 0.95),
    "machine.reset": ("NoReturn", 0.95),  # never returns
    "machine.soft_reset": ("NoReturn", 0.95),  # never returns
    "machine.reset_cause": ("int", 0.95),
    "ussl.wrap_socket": ("stream", 0.95),  # undocumented class ssl.SSLSocket
    "pyb.hard_reset": ("NoReturn", 0.95),  # never returns
    "usys.exit": ("NoReturn", 0.95),  # never returns
    "lcd160cr.LCD160CR.set_power": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
}
