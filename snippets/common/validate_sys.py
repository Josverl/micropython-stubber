import sys

bits = 0
v = sys.maxsize
while v:
    bits += 1
    v >>= 1
# 64-bit (or more) platform
...
print(sys.version_info[0], sys.version_info[1], sys.version_info[2])
print(sys.implementation)

exc = BaseException
sys.print_exception(exc)  # type: ignore - BUG https://github.com/Josverl/micropython-stubber/issues/270


def byebye():
    print("so long")


sys.atexit(byebye)  # type: ignore - BUG https://github.com/Josverl/micropython-stubber/issues/270
