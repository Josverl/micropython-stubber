import io

# from typing import Any, IO, Optional

alloc_size = 512

buffer = io.StringIO(alloc_size)
buffer = io.BytesIO(alloc_size)

stream = open("file")
buf = io.BufferedWriter(stream, 8)
print(buf.write(bytearray(16)))

stream.close()
