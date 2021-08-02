"""
this is an list with manual overrides for function returns that couls not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = module.[class.]function name
- value : two-tuple with ( return type , priority )

"""


LOOKUP_LIST = {
    "uctypes.bytearray_at": ("bytearray", 0.95),
    "math.isnan": ("boolean", 0.95),
    "builtins.to_bytes": ("bytes", 0.95),
    "builtins.bytes": ("bytes", 0.95),
    "uctypes.bytes_at": ("bytes", 0.95),
    "bytearray_at": ("bytearray", 0.95),
    "uos.listdir": ("List[Any]", 0.95),
    "gc.enable": ("None", 0.95),
    "gc.disable": ("None", 0.95),
    "gc.collect": ("None", 0.95),
    "machine.reset": ("None", 0.95),
    "machine.soft_reset": ("None", 0.95),
    "pyb.hard_reset": ("None", 0.95),
    "lcd160cr.LCD160CR.set_power": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
}
