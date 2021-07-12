from typing import Any, Optional, Union, Tuple

# .. module:: cmath
# origin: micropython\docs\library\cmath.rst
# v1.16
"""
   :synopsis: mathematical functions for complex numbers

|see_cpython_module| :mod:`python:cmath`.

The ``cmath`` module provides some basic mathematical functions for
working with complex numbers.

Availability: not available on WiPy and ESP8266. Floating point support
required for this module.
"""
# .. function:: cos(z)
def cos(z) -> Any:
    """
    Return the cosine of ``z``.
    """
    ...


# .. function:: exp(z)
def exp(z) -> Any:
    """
    Return the exponential of ``z``.
    """
    ...


# .. function:: log(z)
def log(z) -> Any:
    """
    Return the natural logarithm of ``z``.  The branch cut is along the negative real axis.
    """
    ...


# .. function:: log10(z)
def log10(z) -> Any:
    """
    Return the base-10 logarithm of ``z``.  The branch cut is along the negative real axis.
    """
    ...


# .. function:: phase(z)
def phase(z) -> Any:
    """
    Returns the phase of the number ``z``, in the range (-pi, +pi].
    """
    ...


# .. function:: polar(z)
def polar(z) -> Any:
    """
    Returns, as a tuple, the polar form of ``z``.
    """
    ...


# .. function:: rect(r, phi)
def rect(r, phi) -> Any:
    """
    Returns the complex number with modulus ``r`` and phase ``phi``.
    """
    ...


# .. function:: sin(z)
def sin(z) -> Any:
    """
    Return the sine of ``z``.
    """
    ...


# .. function:: sqrt(z)
def sqrt(z) -> Any:
    """
    Return the square-root of ``z``.
    """
    ...


# .. data:: e
# .. data:: pi
