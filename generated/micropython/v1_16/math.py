# .. module:: math
# origin: micropython\docs\library\math.rst
# v1.16
"""
   :synopsis: mathematical functions

|see_cpython_module| :mod:`python:math`.

The ``math`` module provides some basic mathematical functions for
working with floating-point numbers.

*Note:* On the pyboard, floating-point numbers have 32-bit precision.

Availability: not available on WiPy. Floating point support required
for this module.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: math
# .. function:: acos(x)
def acos(x) -> Any:
    """
    Return the inverse cosine of ``x``.
    """
    ...


# .. function:: asin(x)
def asin(x) -> Any:
    """
    Return the inverse sine of ``x``.
    """
    ...


# .. function:: atan(x)
def atan(x) -> Any:
    """
    Return the inverse tangent of ``x``.
    """
    ...


# .. function:: atanh(x)
def atanh(x) -> Any:
    """
    Return the inverse hyperbolic tangent of ``x``.
    """
    ...


# .. function:: copysign(x, y)
def copysign(x, y) -> Any:
    """
    Return ``x`` with the sign of ``y``.
    """
    ...


# .. function:: cosh(x)
def cosh(x) -> Any:
    """
    Return the hyperbolic cosine of ``x``.
    """
    ...


# .. function:: erf(x)
def erf(x) -> Any:
    """
    Return the error function of ``x``.
    """
    ...


# .. function:: exp(x)
def exp(x) -> Any:
    """
    Return the exponential of ``x``.
    """
    ...


# .. function:: fabs(x)
def fabs(x) -> Any:
    """
    Return the absolute value of ``x``.
    """
    ...


# .. function:: fmod(x, y)
def fmod(x, y) -> Any:
    """
    Return the remainder of ``x/y``.
    """
    ...


# .. function:: gamma(x)
def gamma(x) -> Any:
    """
    Return the gamma function of ``x``.
    """
    ...


# .. function:: isinf(x)
def isinf(x) -> Any:
    """
    Return ``True`` if ``x`` is infinite.
    """
    ...


# .. function:: ldexp(x, exp)
def ldexp(x, exp) -> Any:
    """
    Return ``x * (2**exp)``.
    """
    ...


# .. function:: log(x)
def log(x) -> Any:
    """
    Return the natural logarithm of ``x``.
    """
    ...


# .. function:: log2(x)
def log2(x) -> Any:
    """
    Return the base-2 logarithm of ``x``.
    """
    ...


# .. function:: pow(x, y)
def pow(x, y) -> Any:
    """
    Returns ``x`` to the power of ``y``.
    """
    ...


# .. function:: sin(x)
def sin(x) -> Any:
    """
    Return the sine of ``x``.
    """
    ...


# .. function:: sqrt(x)
def sqrt(x) -> Any:
    """
    Return the square root of ``x``.
    """
    ...


# .. function:: tanh(x)
def tanh(x) -> Any:
    """
    Return the hyperbolic tangent of ``x``.
    """
    ...


# .. data:: e
# .. data:: pi
