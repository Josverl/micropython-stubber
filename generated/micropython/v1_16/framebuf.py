from typing import Any, Optional, Union, Tuple

# .. module:: framebuf
# origin: micropython\docs\library\framebuf.rst
# v1.16
"""
   :synopsis: Frame buffer manipulation

This module provides a general frame buffer which can be used to create
bitmap images, which can then be sent to a display.
"""
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

# .. method:: FrameBuffer.pixel(x, y[, c])
    def pixel(self, x, y, c: Optional[Any]) -> Any:
        """
            If *c* is not given, get the color value of the specified pixel.
            If *c* is given, set the specified pixel to the given color.
        """
        ...

# .. method:: FrameBuffer.hline(x, y, w, c)
    def hline(self, x, y, w, c) -> Any:
        """
        """
        ...

# .. method:: FrameBuffer.vline(x, y, h, c)
    def vline(self, x, y, h, c) -> Any:
        """
        """
        ...

# .. method:: FrameBuffer.line(x1, y1, x2, y2, c)
    def line(self, x1, y1, x2, y2, c) -> Any:
        """
            Draw a line from a set of coordinates using the given color and
            a thickness of 1 pixel. The `line` method draws the line up to
            a second set of coordinates whereas the `hline` and `vline`
            methods draw horizontal and vertical lines respectively up to
            a given length.
        """
        ...

# .. method:: FrameBuffer.rect(x, y, w, h, c)
    def rect(self, x, y, w, h, c) -> Any:
        """
        """
        ...

# .. method:: FrameBuffer.fill_rect(x, y, w, h, c)
    def fill_rect(self, x, y, w, h, c) -> Any:
        """
            Draw a rectangle at the given location, size and color. The `rect`
            method draws only a 1 pixel outline whereas the `fill_rect` method
            draws both the outline and interior.
        """
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

# .. method:: FrameBuffer.blit(fbuf, x, y[, key])
    def blit(self, fbuf, x, y, key: Optional[Any]) -> Any:
        """
            Draw another FrameBuffer on top of the current one at the given coordinates.
            If *key* is specified then it should be a color integer and the
            corresponding color will be considered transparent: all pixels with that
            color value will not be drawn.
        
            This method works between FrameBuffer instances utilising different formats,
            but the resulting colors may be unexpected due to the mismatch in color
            formats.
        """
        ...

# .. data:: framebuf.MONO_VLSB
# .. data:: framebuf.MONO_HLSB
# .. data:: framebuf.MONO_HMSB
# .. data:: framebuf.RGB565
# .. data:: framebuf.GS2_HMSB
# .. data:: framebuf.GS4_HMSB
# .. data:: framebuf.GS8
