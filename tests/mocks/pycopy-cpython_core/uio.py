import io


class UioStream:

    def __init__(self, s, is_bin):
        self._s = s
        self._is_bin = is_bin

    def write(self, data, off=None, sz=None):
        if self._is_bin and isinstance(data, str):
            data = data.encode()

        if off is not None:
            if sz is None:
                sz = off
                off = 0
            data = memoryview(data)[off:off + sz]

        self._s.write(data)

    def __getattr__(self, attr):
        return getattr(self._s, attr)

    def __iter__(self):
        return self._s.__iter__()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self._s.__exit__(*args)


class StringIO(io.StringIO):

    def __iadd__(self, s):
        self.write(s)
        return self


class BytesIO(io.BytesIO):

    def __iadd__(self, s):
        self.write(s)
        return self


def open(name, mode="r", *args, **kw):
    f = io.open(name, mode, *args, **kw)
    return UioStream(f, "b" in mode)
