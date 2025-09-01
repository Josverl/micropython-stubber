# fmt: off
"""
MicroPython Pin class
"""

class Pin:
    """GPIO Pin control"""
    
    # Interrupt triggers
    IRQ_FALLING = 1
    IRQ_RISING = 2
    IRQ_LOW_LEVEL = 4
    IRQ_HIGH_LEVEL = 8
    
    # Pin modes
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2
    
    def __init__(self, pin): ...
    
    def irq(self): ...

class Timer:
    """Hardware timer"""
    
    # Timer modes
    ONE_SHOT = 0
    PERIODIC = 1
    
    def __init__(self): ...