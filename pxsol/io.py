import io


def read_full(reader: io.IOBase, n: int) -> bytearray:
    # Read exactly n bytes from reader, or raise EOFError.
    data = bytearray()
    while len(data) < n:
        once = reader.read(n - len(data))
        if not once:
            raise EOFError('io: EOF')
        data.extend(once)
    return data
