from typing import Any, Optional, Union, Tuple

# .. module:: wipy
# origin: micropython\docs\library\wipy.rst
# v1.16
"""
   :synopsis: WiPy specific features

The ``wipy`` module contains functions to control specific features of the
WiPy, such as the heartbeat LED.
"""
# .. function:: heartbeat([enable])
def heartbeat(enable: Optional[Any]) -> Any:
    """
    Get or set the state (enabled or disabled) of the heartbeat LED. Accepts and
    returns boolean values (``True`` or ``False``).
    """
    ...
