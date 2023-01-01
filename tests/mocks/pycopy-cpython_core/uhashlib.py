import hashlib


class _hash:
    def __init__(self, data=None):
        cls = getattr(hashlib, self.__class__.__name__)
        self._ = cls() if data is None else cls(data)

    def update(self, data):
        self._.update(data)

    def digest(self):
        return self._.digest()


class md5(_hash):
    pass


class sha1(_hash):
    pass


class sha256(_hash):
    pass
