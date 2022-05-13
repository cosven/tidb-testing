from .excs import InsufficientBytesError


i64_sign_mask = 0x8000000000000000
uint64_mask = 0xffffffffffffffff


def i64_to_u64(v: int) -> int:
    """
    >>> i64_to_u64(-2)
    18446744073709551614
    >>> i64_to_u64(0)
    0
    >>> i64_to_u64(2)
    2
    """
    if v < 0:
        return (~(-v) + 1) & uint64_mask
    return v


def encode_int_to_cmp_uint(v: int) -> int:
    """
    :param v: int64
    :return: uint64

    >>> encode_int_to_cmp_uint(-1)
    9223372036854775807
    """
    return i64_to_u64(v) ^ i64_sign_mask


def encode_int(b: bytes, v: int) -> bytes:
    """
    :param v: int64

    >>> import binascii
    >>> binascii.hexlify(encode_int(bytearray(), 1))
    b'8000000000000001'
    """
    u = encode_int_to_cmp_uint(v)
    return b + u.to_bytes(8, byteorder='big', signed=False)


def decode_uint_desc(b: bytes) -> (bytes, int):
    """decodes value encoded by encode_int before

    It returns the leftover un-decoded slice, decoded value if no error.
    """
    if len(b) < 8:
        raise InsufficientBytesError
    data = b[:8]
    v = int.from_bytes(data, byteorder='big', signed=False)
    return b[8:], (~v & 0xffffffffffffffff)
