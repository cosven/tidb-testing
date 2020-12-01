from .number import encode_int
from .bytes_ import encode_bytes


def encode_int_row_key(table_id: int, row_id: int) -> bytes:
    """

    >>> encode_int_row_key(11, 10).hex()
    '7480000000000000ff0b5f728000000000ff00000a0000000000fa'
    """
    result = bytearray()
    result.extend(b't')
    result.extend(encode_int(b'', table_id))
    result.extend(b'_r')
    result.extend(encode_int(b'', row_id))
    return encode_bytes(b'', result)
