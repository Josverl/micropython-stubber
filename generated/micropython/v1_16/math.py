from typing import Any, Optional, Union, Tuple

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
# .. function:: acos(x)
def acos(x) -> Any:
    """
    Return the inverse cosine of ``x``.
    """
    ...


# .. function:: acosh(x)
def acosh(x) -> Any:
    """
    Return the inverse hyperbolic cosine of ``x``.
    """
    ...


# .. function:: asin(x)
def asin(x) -> Any:
    """
    Return the inverse sine of ``x``.
    """
    ...


# .. function:: asinh(x)
def asinh(x) -> Any:
    """
    Return the inverse hyperbolic sine of ``x``.
    """
    ...


# .. function:: atan(x)
def atan(x) -> Any:
    """
    Return the inverse tangent of ``x``.
    """
    ...


# .. function:: atan2(y, x)
def atan2(y, x) -> Any:
    """
    Return the principal value of the inverse tangent of ``y/x``.
    """
    ...


# .. function:: atanh(x)
def atanh(x) -> Any:
    """
    Return the inverse hyperbolic tangent of ``x``.
    """
    ...


# .. function:: ceil(x)
def ceil(x) -> Any:
    """
    Return an integer, being ``x`` rounded towards positive infinity.
    """
    ...


# .. function:: copysign(x, y)
def copysign(x, y) -> Any:
    """
    Return ``x`` with the sign of ``y``.
    """
    ...


# .. function:: cos(x)
def cos(x) -> Any:
    """
    Return the cosine of ``x``.
    """
    ...


# .. function:: cosh(x)
def cosh(x) -> Any:
    """
    Return the hyperbolic cosine of ``x``.
    """
    ...


# .. function:: degrees(x)
def degrees(x) -> Any:
    """
    Return radians ``x`` converted to degrees.
    """
    ...


# .. function:: erf(x)
def erf(x) -> Any:
    """
    Return the error function of ``x``.
    """
    ...


# .. function:: erfc(x)
def erfc(x) -> Any:
    """
    Return the complementary error function of ``x``.
    """
    ...


# .. function:: exp(x)
def exp(x) -> Any:
    """
    Return the exponential of ``x``.
    """
    ...


# .. function:: expm1(x)
def expm1(x) -> Any:
    """
    Return ``exp(x) - 1``.
    """
    ...


# .. function:: fabs(x)
def fabs(x) -> Any:
    """
    Return the absolute value of ``x``.
    """
    ...


# .. function:: floor(x)
def floor(x) -> Any:
    """
    Return an integer, being ``x`` rounded towards negative infinity.
    """
    ...


# .. function:: fmod(x, y)
def fmod(x, y) -> Any:
    """
    Return the remainder of ``x/y``.
    """
    ...


# .. function:: frexp(x)
def frexp(x) -> Any:
    """
    Decomposes a floating-point number into its mantissa and exponent.
    The returned value is the tuple ``(m, e)`` such that ``x == m * 2**e``
    exactly.  If ``x == 0`` then the function returns ``(0.0, 0)``, otherwise
    the relation ``0.5 <= abs(m) < 1`` holds.
    """
    ...


# .. function:: gamma(x)
def gamma(x) -> Any:
    """
    Return the gamma function of ``x``.
    """
    ...


# .. function:: isfinite(x)
def isfinite(x) -> Any:
    """
    Return ``True`` if ``x`` is finite.
    """
    ...


# .. function:: isinf(x)
def isinf(x) -> Any:
    """
    Return ``True`` if ``x`` is infinite.
    """
    ...


# .. function:: isnan(x)
def isnan(x) -> Any:
    """
    Return ``True`` if ``x`` is not-a-number
    """
    ...


# .. function:: ldexp(x, exp)
def ldexp(x, exp) -> Any:
    """
    Return ``x * (2**exp)``.
    """
    ...


# .. function:: lgamma(x)
def lgamma(x) -> Any:
    """
    Return the natural logarithm of the gamma function of ``x``.
    """
    ...


# .. function:: log(x)
def log(x) -> Any:
    """
    Return the natural logarithm of ``x``.
    """
    ...


# .. function:: log10(x)
def log10(x) -> Any:
    """
    Return the base-10 logarithm of ``x``.
    """
    ...


# .. function:: log2(x)
def log2(x) -> Any:
    """
    Return the base-2 logarithm of ``x``.
    """
    ...


# .. function:: modf(x)
def modf(x) -> Any:
    """
    Return a tuple of two floats, being the fractional and integral parts of
    ``x``.  Both return values have the same sign as ``x``.
    """
    ...


# .. function:: pow(x, y)
def pow(x, y) -> Any:
    """
    Returns ``x`` to the power of ``y``.
    """
    ...


# .. function:: radians(x)
def radians(x) -> Any:
    """
    Return degrees ``x`` converted to radians.
    """
    ...


# .. function:: sin(x)
def sin(x) -> Any:
    """
    Return the sine of ``x``.
    """
    ...


# .. function:: sinh(x)
def sinh(x) -> Any:
    """
    Return the hyperbolic sine of ``x``.
    """
    ...


# .. function:: sqrt(x)
def sqrt(x) -> Any:
    """
    Return the square root of ``x``.
    """
    ...


# .. function:: tan(x)
def tan(x) -> Any:
    """
    Return the tangent of ``x``.
    """
    ...


# .. function:: tanh(x)
def tanh(x) -> Any:
    """
    Return the hyperbolic tangent of ``x``.
    """
    ...


# .. function:: trunc(x)
def trunc(x) -> Any:
    """
    Return an integer, being ``x`` rounded towards 0.
    """
    ...


# .. data:: e
# .. data:: pi
