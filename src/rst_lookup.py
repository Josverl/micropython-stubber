"""
this is an list with manual overrides for function returns that couls not efficiently be determined 
from their docstring description 
Format: a dictionary with :
- key = function name
- value : two-tuple with ( return type , priority )

"""


LOOKUP_LIST = {
    "bytearray_at": ("int", 0.95),
    "isnan": ("boolean", 0.95),
    "to_bytes": ("bytes", 0.95),
    "bytes_at": ("bytes", 0.95),
    "bytearray_at": ("bytearray", 0.95),
    "listdir": ("List[Any]", 0.95),
    "enable": ("None", 0.95),
    "disable": ("None", 0.95),
    "collect": ("None", 0.95),
    "reset": ("None", 0.95),
    "soft_reset": ("None", 0.95),
    "hard_reset": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
    # "": ("None", 0.95),
}
