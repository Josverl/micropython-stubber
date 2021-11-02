# class Signal:
from typing import Optional


class Signal:
    """The Signal class is a simple extension of the Pin class. Unlike Pin, which can be only in “absolute”
    0 and 1 states, a Signal can be in “asserted” (on) or “deasserted” (off) states, while being inverted (active-low) or not.
    In other words, it adds logical inversion support to Pin functionality. While this may seem a simple addition, it is exactly what
    is needed to support wide array of simple digital devices in a way portable across different boards, which is one of the major
    MicroPython goals. Regardless of whether different users have an active-high or active-low LED, a normally open or normally closed
    relay - you can develop a single, nicely looking application which works with each of them, and capture hardware configuration
    differences in few lines in the config file of your app.

    """

    def __init__(self, pin_obj: Pin, *, invert: bool = False):
        """Create a Signal object. There’re two ways to create it:
        By wrapping existing Pin object - universal method which works for any board.
        By passing required Pin parameters directly to Signal constructor, skipping the need to create intermediate Pin object. Available on many, but not all boards.
        The arguments are:
        pin_obj is existing Pin object.
        pin_arguments are the same arguments as can be passed to Pin constructor.
        invert - if True, the signal will be inverted (active low).
        """
        pass

    def off(self):
        """Activate signal."""
        pass

    def on(self):
        """Deactivate signal."""
        pass

    def value(self, x: Optional[bool]):
        """This method allows to set and get the value of the signal, depending on whether the argument x is supplied or not.
        If the argument is omitted then this method gets the signal level, 1 meaning signal is asserted (active) and 0 - signal inactive.
        If the argument is supplied then this method sets the signal level. The argument x can be anything that converts to a boolean.
        If it converts to True, the signal is active, otherwise it is inactive.
        Correspondence between signal being active and actual logic level on the underlying pin depends on whether signal is inverted (active-low) or not.
        For non-inverted signal, active status corresponds to logical 1, inactive - to logical 0. For inverted/active-low signal, active status corresponds to logical 0,
        while inactive - to logical 1.
        """
        pass
