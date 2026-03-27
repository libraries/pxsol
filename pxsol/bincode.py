import io
import itertools
import pxsol.io
import struct
import typing

# A python implementation of bincode encoding/decoding for basic types.
# Source: https://crates.io/crates/solana-bincode


class U8:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 1), 'little')

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= 0x00
        assert number <= 0xff
        return bytearray(number.to_bytes(1, 'little'))


class U16:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 2), 'little')

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= 0x00
        assert number <= 0xffff
        return bytearray(number.to_bytes(2, 'little'))


class U32:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 4), 'little')

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= 0x00
        assert number <= 0xffffffff
        return bytearray(number.to_bytes(4, 'little'))


class U64:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 8), 'little')

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= 0x00
        assert number <= 0xffffffffffffffff
        return bytearray(number.to_bytes(8, 'little'))


class U128:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 16), 'little')

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= 0x00
        assert number <= 0xffffffffffffffffffffffffffffffff
        return bytearray(number.to_bytes(16, 'little'))


class I8:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 1), 'little', signed=True)

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= -0x80
        assert number <= +0x7f
        return bytearray(number.to_bytes(1, 'little', signed=True))


class I16:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 2), 'little', signed=True)

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= -0x8000
        assert number <= +0x7fff
        return bytearray(number.to_bytes(2, 'little', signed=True))


class I32:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 4), 'little', signed=True)

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= -0x80000000
        assert number <= +0x7fffffff
        return bytearray(number.to_bytes(4, 'little', signed=True))


class I64:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 8), 'little', signed=True)

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= -0x8000000000000000
        assert number <= +0x7fffffffffffffff
        return bytearray(number.to_bytes(8, 'little', signed=True))


class I128:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pxsol.io.read_full(reader, 16), 'little', signed=True)

    @classmethod
    def encode(cls, number: int) -> bytearray:
        assert number >= -0x80000000000000000000000000000000
        assert number <= +0x7fffffffffffffffffffffffffffffff
        return bytearray(number.to_bytes(16, 'little', signed=True))


class F32:
    @classmethod
    def decode(cls, reader: io.IOBase) -> float:
        return struct.unpack('<f', pxsol.io.read_full(reader, 4))[0]

    @classmethod
    def encode(cls, number: float) -> bytearray:
        return bytearray(struct.pack('<f', number))


class F64:
    @classmethod
    def decode(cls, reader: io.IOBase) -> float:
        return struct.unpack('<d', pxsol.io.read_full(reader, 8))[0]

    @classmethod
    def encode(cls, number: float) -> bytearray:
        return bytearray(struct.pack('<d', number))


class Bool:
    @classmethod
    def decode(cls, reader: io.IOBase) -> bool:
        return pxsol.io.read_full(reader, 1)[0] != 0

    @classmethod
    def encode(cls, pybool: bool) -> bytearray:
        return bytearray([int(pybool)])


class Enum:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return U32.decode(reader)

    @classmethod
    def encode(cls, number: int) -> bytearray:
        return U32.encode(number)


class String:
    @classmethod
    def decode(cls, reader: io.IOBase) -> str:
        return pxsol.io.read_full(reader, U64.decode(reader)).decode()

    @classmethod
    def encode(cls, string: str) -> bytearray:
        return U64.encode(len(string)) + bytearray(string.encode())


class Array:
    def __init__(self, kype: typing.Any, size: int) -> None:
        self.kype = kype
        self.size = size

    def decode(self, reader: io.IOBase) -> list[typing.Any]:
        return [self.kype.decode(reader) for _ in range(self.size)]

    def encode(self, pylist: list[typing.Any]) -> bytearray:
        return bytearray(itertools.chain(*[self.kype.encode(e) for e in pylist]))


class Slice:
    def __init__(self, kype: typing.Any) -> None:
        self.kype = kype

    def decode(self, reader: io.IOBase) -> list[typing.Any]:
        return [self.kype.decode(reader) for _ in range(U64.decode(reader))]

    def encode(self, pylist: list[typing.Any]) -> bytearray:
        return U64.encode(len(pylist)) + bytearray(itertools.chain(*[self.kype.encode(e) for e in pylist]))


class Struct:
    def __init__(self, kype: list[typing.Any]) -> None:
        self.kype = kype

    def decode(self, reader: io.IOBase) -> list[typing.Any]:
        return [kype.decode(reader) for kype in self.kype]

    def encode(self, pylist: list[typing.Any]) -> bytearray:
        assert len(pylist) == len(self.kype)
        return bytearray(itertools.chain(*[e[0].encode(e[1]) for e in zip(self.kype, pylist)]))


class Dict:
    def __init__(self, kype: list[typing.Any]) -> None:
        self.kype = kype

    def decode(self, reader: io.IOBase) -> dict[typing.Any, typing.Any]:
        return dict([[self.kype[0].decode(reader), self.kype[1].decode(reader)] for _ in range(U64.decode(reader))])

    def encode(self, pydict: dict[typing.Any, typing.Any]) -> bytearray:
        data = []
        for k, v in pydict.items():
            data.append([self.kype[0].encode(k), self.kype[1].encode(v)])
        data.sort(key=lambda x: x[0])
        r = U64.encode(len(data))
        for e in data:
            r.extend(e[0])
            r.extend(e[1])
        return r


class Option:
    def __init__(self, kype: typing.Any) -> None:
        self.kype = kype

    def decode(self, reader: io.IOBase) -> typing.Any | None:
        return self.kype.decode(reader) if U8.decode(reader) != 0 else None

    def encode(self, pydata: typing.Any | None) -> bytearray:
        return bytearray([1]) + self.kype.encode(pydata) if pydata is not None else bytearray([0])


class Custom:
    def __init__(self, func: typing.Callable[[io.IOBase], typing.Any]) -> None:
        self.func = func

    def decode(self, reader: io.IOBase) -> typing.Any:
        return self.func(reader)

    def encode(self, pydata: bytearray) -> bytearray:
        return pydata
