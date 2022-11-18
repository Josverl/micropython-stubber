import uio

# from typing import Any, IO, Optional

alloc_size = 512

buffer = uio.StringIO(alloc_size)
buffer = uio.BytesIO(alloc_size)

stream = open("file")
buf = uio.BufferedWriter(stream, 8)
print(buf.write(bytearray(16)))

stream.close()
