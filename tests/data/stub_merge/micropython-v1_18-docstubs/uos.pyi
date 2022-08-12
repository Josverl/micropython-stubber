"""
basic "operating system" services. See: https://docs.micropython.org/en/v1.18/library/os.html

|see_cpython_module| :mod:`python:os` https://docs.python.org/3/library/os.html .

The ``os`` module contains functions for filesystem access and mounting,
terminal redirection and duplication, and the ``uname`` and ``urandom``
functions.
"""

# source version: v1_18
# origin module:: repos/micropython/docs/library/os.rst
from typing import IO, Any, Callable, Coroutine, Dict, Generator, Iterator, List, NoReturn, Optional, Tuple, Union

class VfsFat:
    """
    Create a filesystem object that uses the FAT filesystem format.  Storage of
    the FAT filesystem is provided by *block_dev*.
    Objects created by this constructor can be mounted using :func:`mount`.
    """

    def __init__(self, block_dev) -> None: ...
    @staticmethod
    def mkfs(block_dev) -> None:
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

    def __init__(self, block_dev, readsize=32, progsize=32, lookahead=32) -> None: ...
    @staticmethod
    def mkfs(block_dev, readsize=32, progsize=32, lookahead=32) -> None:
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

    def __init__(self, block_dev, readsize=32, progsize=32, lookahead=32, mtime=True) -> None: ...
    @staticmethod
    def mkfs(block_dev, readsize=32, progsize=32, lookahead=32) -> None:
        """
            Build a Lfs2 filesystem on *block_dev*.

        ``Note:`` There are reports of littlefs v2 failing in certain situations,
                  for details see `littlefs issue 295`_.
        """
        ...

class AbstractBlockDev:
    """
    Construct a block device object.  The parameters to the constructor are
    dependent on the specific block device.
    """

    def __init__(self, *args) -> None: ...
    def readblocks(self, block_num, buf, offset: Optional[int] = 0) -> Any:
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
    def writeblocks(self, block_num, buf, offset: Optional[int] = 0) -> Any:
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
    def ioctl(self, op, arg) -> int:
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

def uname() -> Tuple:
    """
    Return a tuple (possibly a named tuple) containing information about the
    underlying machine and/or its operating system.  The tuple has five fields
    in the following order, each of them being a string:

         * ``sysname`` -- the name of the underlying system
         * ``nodename`` -- the network name (can be the same as ``sysname``)
         * ``release`` -- the version of the underlying system
         * ``version`` -- the MicroPython version and build date
         * ``machine`` -- an identifier for the underlying hardware (eg board, CPU)
    """
    ...

def urandom(n) -> bytes:
    """
    Return a bytes object with *n* random bytes. Whenever possible, it is
    generated by the hardware random number generator.
    """
    ...

def chdir(path) -> Any:
    """
    Change current directory.
    """
    ...

def getcwd() -> Any:
    """
    Get the current directory.
    """
    ...

def ilistdir(dir: Optional[Any] = None) -> Iterator[Tuple]:
    """
    This function returns an iterator which then yields tuples corresponding to
    the entries in the directory that it is listing.  With no argument it lists the
    current directory, otherwise it lists the directory given by *dir*.

    The tuples have the form *(name, type, inode[, size])*:

     - *name* is a string (or bytes if *dir* is a bytes object) and is the name of
       the entry;
     - *type* is an integer that specifies the type of the entry, with 0x4000 for
       directories and 0x8000 for regular files;
     - *inode* is an integer corresponding to the inode of the file, and may be 0
       for filesystems that don't have such a notion.
     - Some platforms may return a 4-tuple that includes the entry's *size*.  For
       file entries, *size* is an integer representing the size of the file
       or -1 if unknown.  Its meaning is currently undefined for directory
       entries.
    """
    ...

def listdir(dir: Optional[Any] = None) -> Any:
    """
    With no argument, list the current directory.  Otherwise list the given directory.
    """
    ...

def mkdir(path) -> Any:
    """
    Create a new directory.
    """
    ...

def remove(path) -> None:
    """
    Remove a file.
    """
    ...

def rmdir(path) -> None:
    """
    Remove a directory.
    """
    ...

def rename(old_path, new_path) -> None:
    """
    Rename a file.
    """
    ...

def stat(path) -> Any:
    """
    Get the status of a file or directory.
    """
    ...

def statvfs(path) -> Tuple:
    """
    Get the status of a fileystem.

    Returns a tuple with the filesystem information in the following order:

         * ``f_bsize`` -- file system block size
         * ``f_frsize`` -- fragment size
         * ``f_blocks`` -- size of fs in f_frsize units
         * ``f_bfree`` -- number of free blocks
         * ``f_bavail`` -- number of free blocks for unprivileged users
         * ``f_files`` -- number of inodes
         * ``f_ffree`` -- number of free inodes
         * ``f_favail`` -- number of free inodes for unprivileged users
         * ``f_flag`` -- mount flags
         * ``f_namemax`` -- maximum filename length

    Parameters related to inodes: ``f_files``, ``f_ffree``, ``f_avail``
    and the ``f_flags`` parameter may return ``0`` as they can be unavailable
    in a port-specific implementation.
    """
    ...

def sync() -> None:
    """
    Sync all filesystems.
    """
    ...

def dupterm(stream_object, index=0, /) -> IO:
    """
    Duplicate or switch the MicroPython terminal (the REPL) on the given `stream`-like
    object. The *stream_object* argument must be a native stream object, or derive
    from ``io.IOBase`` and implement the ``readinto()`` and
    ``write()`` methods.  The stream should be in non-blocking mode and
    ``readinto()`` should return ``None`` if there is no data available for reading.

    After calling this function all terminal output is repeated on this stream,
    and any input that is available on the stream is passed on to the terminal input.

    The *index* parameter should be a non-negative integer and specifies which
    duplication slot is set.  A given port may implement more than one slot (slot 0
    will always be available) and in that case terminal input and output is
    duplicated on all the slots that are set.

    If ``None`` is passed as the *stream_object* then duplication is cancelled on
    the slot given by *index*.

    The function returns the previous stream-like object in the given slot.
    """
    ...

def mount(fsobj, mount_point, *, readonly) -> Any:
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

def umount(mount_point) -> Any:
    """
    Unmount a filesystem. *mount_point* can be a string naming the mount location,
    or a previously-mounted filesystem object.  During the unmount process the
    method ``umount()`` is called on the filesystem object.

    Will raise ``OSError(EINVAL)`` if *mount_point* is not found.
    """
    ...
