# fmt: off
"""
MicroPython Pin class - documentation version
"""

class Pin:
    """GPIO Pin control with rich documentation"""
    
    # Interrupt triggers
    IRQ_FALLING = 1
    """Trigger on falling edge"""
    IRQ_RISING = 2
    """Trigger on rising edge"""
    IRQ_LOW_LEVEL = 4
    """Trigger on low level"""
    IRQ_HIGH_LEVEL = 8
    """Trigger on high level"""
    
    # Pin modes
    IN = 0
    """Input mode"""
    OUT = 1
    """Output mode"""
    OPEN_DRAIN = 2
    """Open-drain output mode"""
    
    def __init__(self, pin):
        """Initialize Pin with pin number"""
        ...
    
    def irq(self):
        """Configure interrupt"""
        ...

class Timer:
    """Hardware timer with documentation"""
    
    # Timer modes
    ONE_SHOT = 0
    """Single execution timer"""
    PERIODIC = 1
    """Repeating timer"""
    
    def __init__(self):
        """Initialize timer"""
        ...