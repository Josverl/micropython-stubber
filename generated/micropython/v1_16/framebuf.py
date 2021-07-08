# .. module:: framebuf
# origin: micropython\docs\library\framebuf.rst
# v1.16
"""
   :synopsis: Frame buffer manipulation

This module provides a general frame buffer which can be used to create
bitmap images, which can then be sent to a display.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: framebuf
# .. class:: FrameBuffer(buffer, width, height, format, stride=width, /)
# .. class:: FrameBuffer(buffer, width, height, format, stride=width, /)

# class:: FrameBuffer
class FrameBuffer:
    """
    Construct a FrameBuffer object.  The parameters are:

        - *buffer* is an object with a buffer protocol which must be large
          enough to contain every pixel defined by the width, height and
          format of the FrameBuffer.
        - *width* is the width of the FrameBuffer in pixels
        - *height* is the height of the FrameBuffer in pixels
        - *format* specifies the type of pixel used in the FrameBuffer;
          permissible values are listed under Constants below. These set the
          number of bits used to encode a color value and the layout of these
          bits in *buffer*.
          Where a color value c is passed to a method, c is a small integer
          with an encoding that is dependent on the format of the FrameBuffer.
        - *stride* is the number of pixels between each horizontal line
          of pixels in the FrameBuffer. This defaults to *width* but may
          need adjustments when implementing a FrameBuffer within another
          larger FrameBuffer or screen. The *buffer* size must accommodate
          an increased step size.

    One must specify valid *buffer*, *width*, *height*, *format* and
    optionally *stride*.  Invalid *buffer* size or dimensions may lead to
    unexpected errors.
    """

    def __init__(self, buffer, width, height, format, stride=width, /) -> None:
        ...

    # .. method:: FrameBuffer.fill(c)
    def fill(self, c) -> Any:
        """
        Fill the entire FrameBuffer with the specified color.
        """
        ...

    # .. method:: FrameBuffer.hline(x, y, w, c)
    def hline(self, x, y, w, c) -> Any:
        """ """
        ...

    # .. method:: FrameBuffer.rect(x, y, w, h, c)
    def rect(self, x, y, w, h, c) -> Any:
        """ """
        ...

    # .. method:: FrameBuffer.text(s, x, y[, c])
    def text(self, s, x, y, c: Optional[Any]) -> Any:
        """
        Write text to the FrameBuffer using the the coordinates as the upper-left
        corner of the text. The color of the text can be defined by the optional
        argument but is otherwise a default value of 1. All characters have
        dimensions of 8x8 pixels and there is currently no way to change the font.

        """
        ...

    # .. method:: FrameBuffer.scroll(xstep, ystep)
    def scroll(self, xstep, ystep) -> Any:
        """
        Shift the contents of the FrameBuffer by the given vector. This may
        leave a footprint of the previous colors in the FrameBuffer.
        """
        ...


# .. data:: framebuf.MONO_VLSB
# .. data:: framebuf.MONO_HLSB
# .. data:: framebuf.MONO_HMSB
# .. data:: framebuf.RGB565
# .. data:: framebuf.GS2_HMSB
# .. data:: framebuf.GS4_HMSB
# .. data:: framebuf.GS8
