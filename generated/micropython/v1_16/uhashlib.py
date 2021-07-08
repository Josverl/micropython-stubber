# .. module:: uhashlib
# origin: micropython\docs\library\uhashlib.rst
# v1.16
"""
   :synopsis: hashing algorithms

|see_cpython_module| :mod:`python:hashlib`.

This module implements binary data hashing algorithms. The exact inventory
of available algorithms depends on a board. Among the algorithms which may
be implemented:

* SHA256 - The current generation, modern hashing algorithm (of SHA2 series).
  It is suitable for cryptographically-secure purposes. Included in the
  MicroPython core and any board is recommended to provide this, unless
  it has particular code size constraints.

* SHA1 - A previous generation algorithm. Not recommended for new usages,
  but SHA1 is a part of number of Internet standards and existing
  applications, so boards targeting network connectivity and
  interoperability will try to provide this.

* MD5 - A legacy algorithm, not considered cryptographically secure. Only
  selected boards, targeting interoperability with legacy applications,
  will offer this.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: uhashlib
# .. class:: uhashlib.sha256([data])
# .. class:: uhashlib.sha256([data])

# class:: sha256
class sha256:
    """
    Create an SHA256 hasher object and optionally feed ``data`` into it.
    """

    def __init__(self, data: Optional[Any]) -> None:
        ...

    # .. class:: uhashlib.md5([data])
    # .. class:: uhashlib.md5([data])

    # class:: md5
    class md5:
        """
        Create an MD5 hasher object and optionally feed ``data`` into it.
        """

        def __init__(self, data: Optional[Any]) -> None:
            ...

        # .. method:: hash.update(data)
        class hash:
            """ """

            def update(self, data) -> Any:
                """
                Feed more binary data into hash.
                """
                ...

            # .. method:: hash.hexdigest()
            def hexdigest(
                self,
            ) -> Any:
                """
                This method is NOT implemented. Use ``ubinascii.hexlify(hash.digest())``
                to achieve a similar effect.
                """
                ...
