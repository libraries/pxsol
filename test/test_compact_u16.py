import pxsol
import pytest
import random


def test_compact_u16_success():
    case = [
        [0x0000, bytearray([0x00])],
        [0x007f, bytearray([0x7f])],
        [0x0080, bytearray([0x80, 0x01])],
        [0x00ff, bytearray([0xff, 0x01])],
        [0x0100, bytearray([0x80, 0x02])],
        [0x07ff, bytearray([0xff, 0x0f])],
        [0x3fff, bytearray([0xff, 0x7f])],
        [0x4000, bytearray([0x80, 0x80, 0x01])],
        [0xffff, bytearray([0xff, 0xff, 0x03])],
    ]
    for e in case:
        assert pxsol.compact_u16.encode(e[0]) == e[1]
        assert pxsol.compact_u16.decode(e[1]) == e[0]


def test_compact_u16_invalid():
    case = [
        bytearray([0x80, 0x00]),
        bytearray([0x80, 0x80, 0x00]),
        bytearray([0xff, 0x00]),
        bytearray([0xff, 0x80, 0x00]),
        bytearray([0x80, 0x81, 0x00]),
        bytearray([0xff, 0x81, 0x00]),
        bytearray([0x80, 0x82, 0x00]),
        bytearray([0xff, 0x8f, 0x00]),
        bytearray([0xff, 0xff, 0x00]),
        bytearray([]),
        bytearray([0x80]),
        bytearray([0x80, 0x80, 0x80, 0x00]),
        bytearray([0x80, 0x80, 0x04]),
        bytearray([0x80, 0x80, 0x06]),
    ]
    for e in case:
        with pytest.raises((AssertionError, EOFError)):
            pxsol.compact_u16.decode(e)


def test_compact_u16_random():
    for _ in range(8):
        n = random.randint(0, 0xffff)
        assert pxsol.compact_u16.decode(pxsol.compact_u16.encode(n)) == n
