import io
import pxsol.io

# Compact-u16 Encoding Specification
#
# A variable-length encoding for unsigned 16-bit integers, using 1 to 3 bytes.
# This is a variant of LEB128 where only the first 2 bytes use the continuation bit.
#
# Encoding rules:
#   - If value <= 0x7f (127):           1 byte  [0xxxxxxx]
#   - If value <= 0x3fff (16383):       2 bytes [1xxxxxxx] [0xxxxxxx]
#   - If value <= 0xffff (65535):       3 bytes [1xxxxxxx] [1xxxxxxx] [xxxxxxxx]
#
# The high bit (0x80) of bytes 1-2 indicates continuation. Byte 3 uses all 8 bits.
#
# Decoding formula:
#   n = (byte1 & 0x7f) + ((byte2 & 0x7f) << 7) + (byte3 << 14)
#
# Canonical encoding:
#   - Byte 2 must != 0x00 (otherwise value fits in 1 byte)
#   - Byte 3 must != 0x00 (otherwise value fits in 2 byte)
#   - Byte 3 must <= 0x03 (otherwise it exceeds u16 range)


def encode(n: int) -> bytearray:
    # Same as u16, but serialized with 1 to 3 bytes. If the value is above 0x7f, the top bit is set and the remaining
    # value is stored in the next bytes. Each byte follows the same pattern until the 3rd byte. The 3rd byte, if
    # needed, uses all 8 bits to store the last byte of the original value.
    assert n >= 0
    assert n <= 0xffff
    if n <= 0x7f:
        return bytearray([n])
    if n <= 0x3fff:
        a = n & 0x7f | 0x80
        b = n >> 7
        return bytearray([a, b])
    if n <= 0xffff:
        a = n & 0x7f | 0x80
        n = n >> 7
        b = n & 0x7f | 0x80
        c = n >> 7
        return bytearray([a, b, c])
    raise Exception


def decode(data: bytearray) -> int:
    # Decode from a buffer. Raises EOFError or AssertionError on invalid data.
    assert len(data) <= 3
    return decode_reader(io.BytesIO(data))


def decode_reader(reader: io.IOBase) -> int:
    # Decode from a reader. Raises EOFError or AssertionError on invalid data.
    c = pxsol.io.read_full(reader, 1)[0]
    if c <= 0x7f:
        return c
    n = c & 0x7f
    c = pxsol.io.read_full(reader, 1)[0]
    assert c != 0x00
    m = c & 0x7f
    n += m << 7
    if c <= 0x7f:
        return n
    c = pxsol.io.read_full(reader, 1)[0]
    assert c != 0x00
    assert c <= 0x03
    n += c << 14
    return n
