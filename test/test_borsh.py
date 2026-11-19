import io

import pxsol


def test_bool():
    for case in [
        [bool(0), bytearray([0])],
        [bool(1), bytearray([1])],
    ]:
        assert pxsol.borsh.Bool.encode(case[0]) == case[1]
        assert pxsol.borsh.Bool.decode(io.BytesIO(case[1])) == case[0]


def test_number():
    case = [255, bytearray([255])]
    assert pxsol.borsh.U8.encode(case[0]) == case[1]
    assert pxsol.borsh.U8.decode(io.BytesIO(case[1])) == case[0]
    case = [-128, bytearray([128])]
    assert pxsol.borsh.I8.encode(case[0]) == case[1]
    assert pxsol.borsh.I8.decode(io.BytesIO(case[1])) == case[0]
    case = [65535, bytearray([255, 255])]
    assert pxsol.borsh.U16.encode(case[0]) == case[1]
    assert pxsol.borsh.U16.decode(io.BytesIO(case[1])) == case[0]
    case = [-32768, bytearray([0, 128])]
    assert pxsol.borsh.I16.encode(case[0]) == case[1]
    assert pxsol.borsh.I16.decode(io.BytesIO(case[1])) == case[0]
    case = [4294967295, bytearray([255, 255, 255, 255])]
    assert pxsol.borsh.U32.encode(case[0]) == case[1]
    assert pxsol.borsh.U32.decode(io.BytesIO(case[1])) == case[0]
    case = [-2147483648, bytearray([0, 0, 0, 128])]
    assert pxsol.borsh.I32.encode(case[0]) == case[1]
    assert pxsol.borsh.I32.decode(io.BytesIO(case[1])) == case[0]
    case = [18446744073709551615, bytearray([255, 255, 255, 255, 255, 255, 255, 255])]
    assert pxsol.borsh.U64.encode(case[0]) == case[1]
    assert pxsol.borsh.U64.decode(io.BytesIO(case[1])) == case[0]
    case = [-9223372036854775808, bytearray([0, 0, 0, 0, 0, 0, 0, 128])]
    assert pxsol.borsh.I64.encode(case[0]) == case[1]
    assert pxsol.borsh.I64.decode(io.BytesIO(case[1])) == case[0]
    case = [340282366920938463463374607431768211455, bytearray([255] * 16)]
    assert pxsol.borsh.U128.encode(case[0]) == case[1]
    assert pxsol.borsh.U128.decode(io.BytesIO(case[1])) == case[0]
    case = [-170141183460469231731687303715884105728, bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128])]
    assert pxsol.borsh.I128.encode(case[0]) == case[1]
    assert pxsol.borsh.I128.decode(io.BytesIO(case[1])) == case[0]
    case = [0.5, bytearray([0, 0, 0, 63])]
    assert pxsol.borsh.F32.encode(case[0]) == case[1]
    assert pxsol.borsh.F32.decode(io.BytesIO(case[1])) == case[0]
    case = [-0.5, bytearray([0, 0, 0, 0, 0, 0, 224, 191])]
    assert pxsol.borsh.F64.encode(case[0]) == case[1]
    assert pxsol.borsh.F64.decode(io.BytesIO(case[1])) == case[0]


def test_array():
    case = [[1, 2, 3], bytearray([1, 0, 2, 0, 3, 0])]
    assert pxsol.borsh.Array(pxsol.borsh.I16, 3).encode(case[0]) == case[1]
    assert pxsol.borsh.Array(pxsol.borsh.I16, 3).decode(io.BytesIO(case[1])) == case[0]


def test_slice():
    case = [[1, 1], bytearray([2, 0, 0, 0, 1, 0, 1, 0])]
    assert pxsol.borsh.Slice(pxsol.borsh.I16).encode(case[0]) == case[1]
    assert pxsol.borsh.Slice(pxsol.borsh.I16).decode(io.BytesIO(case[1])) == case[0]


def test_struct():
    case = [
        [123, 'hello', 1400, 13],
        bytearray([
            0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x05, 0x00, 0x00, 0x00, 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x78, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x01, 0x0d, 0x00,
        ])
    ]
    kype = pxsol.borsh.Struct([
        pxsol.borsh.U128,
        pxsol.borsh.String,
        pxsol.borsh.I64,
        pxsol.borsh.Option(pxsol.borsh.U16),
    ])
    assert kype.encode(case[0]) == case[1]
    assert kype.decode(io.BytesIO(case[1])) == case[0]


def test_dict():
    case = [{'k': 'v'}, bytearray([1, 0, 0, 0, 1, 0, 0, 0, 107, 1, 0, 0, 0, 118])]
    assert pxsol.borsh.Dict([pxsol.borsh.String, pxsol.borsh.String]).encode(case[0]) == case[1]
    assert pxsol.borsh.Dict([pxsol.borsh.String, pxsol.borsh.String]).decode(io.BytesIO(case[1])) == case[0]


def test_option():
    case = [1, bytearray([1, 1])]
    assert pxsol.borsh.Option(pxsol.borsh.U8).encode(case[0]) == case[1]
    assert pxsol.borsh.Option(pxsol.borsh.U8).decode(io.BytesIO(case[1])) == case[0]


def test_string():
    case = ['hello', bytearray([5, 0, 0, 0, 104, 101, 108, 108, 111])]
    assert pxsol.borsh.String.encode(case[0]) == case[1]
    assert pxsol.borsh.String.decode(io.BytesIO(case[1])) == case[0]
