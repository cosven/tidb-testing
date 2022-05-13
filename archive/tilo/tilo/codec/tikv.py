from .number import decode_uint_desc


def decode_write_key(key: bytes):
    ts_len = 8
    if len(key) < ts_len:
        raise InsufficientBytesError
    ts_bytes = key[-ts_len:]
    user_key = key[:-ts_len]
    _, ts = decode_uint_desc(user_key)
    return user_key, ts
