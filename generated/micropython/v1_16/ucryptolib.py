from typing import Any, Optional, Union, Tuple

# .. module:: ucryptolib
# origin: micropython\docs\library\ucryptolib.rst
# v1.16
"""
   :synopsis: cryptographic ciphers
"""
# .. class:: aes
# class:: aes
class aes:
    """ """

    #     .. classmethod:: __init__(key, mode, [IV])
    #     .. method:: encrypt(in_buf, [out_buf])
    def encrypt(self, in_buf, out_buf: Optional[Any]) -> Any:
        """
        Encrypt *in_buf*. If no *out_buf* is given result is returned as a
        newly allocated `bytes` object. Otherwise, result is written into
        mutable buffer *out_buf*. *in_buf* and *out_buf* can also refer
        to the same mutable buffer, in which case data is encrypted in-place.
        """
        ...

    #     .. method:: decrypt(in_buf, [out_buf])
    def decrypt(self, in_buf, out_buf: Optional[Any]) -> Any:
        """
        Like `encrypt()`, but for decryption.
        """
        ...
