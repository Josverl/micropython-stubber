Flash partitions
----------------

This class gives access to the partitions in the device's flash memory and includes
methods to enable over-the-air (OTA) updates.

.. class:: Partition(id)

    Create an object representing a partition.  *id* can be a string which is the label
    of the partition to retrieve, or one of the constants: ``BOOT`` or ``RUNNING``.

.. classmethod:: Partition.find(type=TYPE_APP, subtype=0xff, label=None)

    Find a partition specified by *type*, *subtype* and *label*.  Returns a
    (possibly empty) list of Partition objects. Note: ``subtype=0xff`` matches any subtype
    and ``label=None`` matches any label.

.. method:: Partition.info()

    Returns a 6-tuple ``(type, subtype, addr, size, label, encrypted)``.

.. method:: Partition.readblocks(block_num, buf)
            Partition.readblocks(block_num, buf, offset)
.. method:: Partition.writeblocks(block_num, buf)
            Partition.writeblocks(block_num, buf, offset)
.. method:: Partition.ioctl(cmd, arg)