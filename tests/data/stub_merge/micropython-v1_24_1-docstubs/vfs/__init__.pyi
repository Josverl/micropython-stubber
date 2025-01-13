"""
Virtual filesystem control.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/vfs.html

The ``vfs`` module contains functions for creating filesystem objects and
mounting/unmounting them in the Virtual Filesystem.

Filesystem mounting
-------------------

Some ports provide a Virtual Filesystem (VFS) and the ability to mount multiple
"real" filesystems within this VFS.  Filesystem objects can be mounted at either
the root of the VFS, or at a subdirectory that lives in the root.  This allows
dynamic and flexible configuration of the filesystem that is seen by Python
programs.  Ports that have this functionality provide the :func:`mount` and
:func:`umount` functions, and possibly various filesystem implementations
represented by VFS classes.
"""

# source version: v1.24.1
# origin module:: repos/micropython/docs/library/vfs.rst
from __future__ import annotations

from typing import Optional

from _mpy_shed.blockdevice import AbstractBlockDev as _AbstractBlockDev
from _typeshed import Incomplete

class VfsFat:
    """
    Create a filesystem object that uses the FAT filesystem format.  Storage of
    the FAT filesystem is provided by *block_dev*.
    Objects created by this constructor can be mounted using :func:`mount`.
    """

    def __init__(self, block_dev: AbstractBlockDev) -> None: ...
    @staticmethod
    def mkfs(block_dev: AbstractBlockDev) -> None:
        """
        Build a FAT filesystem on *block_dev*.
        """
        ...

class VfsLfs1:
    """
    Create a filesystem object that uses the `littlefs v1 filesystem format`_.
    Storage of the littlefs filesystem is provided by *block_dev*, which must
    support the :ref:`extended interface <block-device-interface>`.
    Objects created by this constructor can be mounted using :func:`mount`.

    See :ref:`filesystem` for more information.
    """

    def __init__(self, block_dev: AbstractBlockDev, readsize=32, progsize=32, lookahead=32) -> None: ...
    @staticmethod
    def mkfs(block_dev: AbstractBlockDev, readsize=32, progsize=32, lookahead=32) -> None:
        """
            Build a Lfs1 filesystem on *block_dev*.

        ``Note:`` There are reports of littlefs v1 failing in certain situations,
                  for details see `littlefs issue 347`_.
        """
        ...

class VfsLfs2:
    """
    Create a filesystem object that uses the `littlefs v2 filesystem format`_.
    Storage of the littlefs filesystem is provided by *block_dev*, which must
    support the :ref:`extended interface <block-device-interface>`.
    Objects created by this constructor can be mounted using :func:`mount`.

    The *mtime* argument enables modification timestamps for files, stored using
    littlefs attributes.  This option can be disabled or enabled differently each
    mount time and timestamps will only be added or updated if *mtime* is enabled,
    otherwise the timestamps will remain untouched.  Littlefs v2 filesystems without
    timestamps will work without reformatting and timestamps will be added
    transparently to existing files once they are opened for writing.  When *mtime*
    is enabled `os.stat` on files without timestamps will return 0 for the timestamp.

    See :ref:`filesystem` for more information.
    """

    def __init__(self, block_dev: AbstractBlockDev, readsize=32, progsize=32, lookahead=32, mtime=True) -> None: ...
    @staticmethod
    def mkfs(block_dev: AbstractBlockDev, readsize=32, progsize=32, lookahead=32) -> None:
        """
            Build a Lfs2 filesystem on *block_dev*.

        ``Note:`` There are reports of littlefs v2 failing in certain situations,
                  for details see `littlefs issue 295`_.
        """
        ...

class VfsPosix:
    """
    Create a filesystem object that accesses the host POSIX filesystem.
    If *root* is specified then it should be a path in the host filesystem to use
    as the root of the ``VfsPosix`` object.  Otherwise the current directory of
    the host filesystem is used.
    """

    def __init__(self, root: str | None = None) -> None: ...

class AbstractBlockDev(_AbstractBlockDev):
    """
    Construct a block device object.  The parameters to the constructor are
    dependent on the specific block device.
    """

    def __init__(self, *args, **kwargs) -> None: ...
    def readblocks(self, block_num: int, buf, offset: Optional[int] = 0) -> Incomplete:
        """
        The first form reads aligned, multiples of blocks.
        Starting at the block given by the index *block_num*, read blocks from
        the device into *buf* (an array of bytes).
        The number of blocks to read is given by the length of *buf*,
        which will be a multiple of the block size.

        The second form allows reading at arbitrary locations within a block,
        and arbitrary lengths.
        Starting at block index *block_num*, and byte offset within that block
        of *offset*, read bytes from the device into *buf* (an array of bytes).
        The number of bytes to read is given by the length of *buf*.
        """
        ...

    def writeblocks(self, block_num: int, buf, offset: Optional[int] = 0) -> Incomplete:
        """
        The first form writes aligned, multiples of blocks, and requires that the
        blocks that are written to be first erased (if necessary) by this method.
        Starting at the block given by the index *block_num*, write blocks from
        *buf* (an array of bytes) to the device.
        The number of blocks to write is given by the length of *buf*,
        which will be a multiple of the block size.

        The second form allows writing at arbitrary locations within a block,
        and arbitrary lengths.  Only the bytes being written should be changed,
        and the caller of this method must ensure that the relevant blocks are
        erased via a prior ``ioctl`` call.
        Starting at block index *block_num*, and byte offset within that block
        of *offset*, write bytes from *buf* (an array of bytes) to the device.
        The number of bytes to write is given by the length of *buf*.

        Note that implementations must never implicitly erase blocks if the offset
        argument is specified, even if it is zero.
        """
        ...

    def ioctl(self, op: int, arg) -> int:
        """
         Control the block device and query its parameters.  The operation to
         perform is given by *op* which is one of the following integers:

           - 1 -- initialise the device (*arg* is unused)
           - 2 -- shutdown the device (*arg* is unused)
           - 3 -- sync the device (*arg* is unused)
           - 4 -- get a count of the number of blocks, should return an integer
             (*arg* is unused)
           - 5 -- get the number of bytes in a block, should return an integer,
             or ``None`` in which case the default value of 512 is used
             (*arg* is unused)
           - 6 -- erase a block, *arg* is the block number to erase

        As a minimum ``ioctl(4, ...)`` must be intercepted; for littlefs
        ``ioctl(6, ...)`` must also be intercepted. The need for others is
        hardware dependent.

        Prior to any call to ``writeblocks(block, ...)`` littlefs issues
        ``ioctl(6, block)``. This enables a device driver to erase the block
        prior to a write if the hardware requires it. Alternatively a driver
        might intercept ``ioctl(6, block)`` and return 0 (success). In this case
        the driver assumes responsibility for detecting the need for erasure.

        Unless otherwise stated ``ioctl(op, arg)`` can return ``None``.
        Consequently an implementation can ignore unused values of ``op``. Where
        ``op`` is intercepted, the return value for operations 4 and 5 are as
        detailed above. Other operations should return 0 on success and non-zero
        for failure, with the value returned being an ``OSError`` errno code.
        """
        ...

def mount(fsobj, mount_point: str, *, readonly=False) -> Incomplete:
    """
    Mount the filesystem object *fsobj* at the location in the VFS given by the
    *mount_point* string.  *fsobj* can be a a VFS object that has a ``mount()``
    method, or a block device.  If it's a block device then the filesystem type
    is automatically detected (an exception is raised if no filesystem was
    recognised).  *mount_point* may be ``'/'`` to mount *fsobj* at the root,
    or ``'/<name>'`` to mount it at a subdirectory under the root.

    If *readonly* is ``True`` then the filesystem is mounted read-only.

    During the mount process the method ``mount()`` is called on the filesystem
    object.

    Will raise ``OSError(EPERM)`` if *mount_point* is already mounted.
    """
    ...

def umount(mount_point: Incomplete) -> Incomplete:
    """
    Unmount a filesystem. *mount_point* can be a string naming the mount location,
    or a previously-mounted filesystem object.  During the unmount process the
    method ``umount()`` is called on the filesystem object.

    Will raise ``OSError(EINVAL)`` if *mount_point* is not found.
    """
    ...
