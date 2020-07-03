class Crypto:
    _split = '.'
    _flag = 65535

    def __init__(self, offset: int = -1):
        # offset: encrypt and decrypt need to be consistent,
        # and cannot be an integer multiple of 0 or `len (data)`.
        self.offset = offset

    def encrypt(self, data: str) -> str:
        lst = [ord(i) for i in data]
        len(lst) == 1 and lst.append(self._flag)
        for i in range(len(lst)):
            lst[i] += self._(lst, i)
        return self._split.join(str(i) for i in lst)

    def decrypt(self, data: str) -> str:
        lst = [int(i) for i in data.split(self._split)]
        for i in range(len(lst) - 1, -1, -1):
            lst[i] -= self._(lst, i)
        lst[-1] == self._flag and lst.remove(lst[-1])
        return ''.join(chr(i) for i in lst)

    def _(self, data: list, i: int):
        """索引加偏移量余长度取值"""
        return data[(i + self.offset) % len(data)]


def encrypt(data: str, offset: int = -1) -> str:
    return Crypto(offset).encrypt(data)


def decrypt(data: str, offset: int = -1) -> str:
    return Crypto(offset).decrypt(data)
