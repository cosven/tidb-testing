import sys


ENC_GROUP_SIZE = 8
ENC_MARKER = b'\xFF'
ENC_PAD = b'\x00'
PADS = b'\x00' * ENC_GROUP_SIZE


def encode_bytes(b: bytes, data: bytes) -> bytes:
    d_len = len(data)

    i = 0
    ba = bytearray(b)
    while i <= d_len:
        remain = d_len - i
        pad_count = 0
        if remain >= ENC_GROUP_SIZE:
            ba.extend(data[i:i+ENC_GROUP_SIZE])
        else:
            pad_count = ENC_GROUP_SIZE - remain
            ba.extend(data[i:])
            ba.extend(PADS[:pad_count])
        num = int.from_bytes(ENC_MARKER, sys.byteorder, signed=False)
        marker = (num - pad_count).to_bytes(1, sys.byteorder, signed=False)
        ba.extend(marker)

        i += ENC_GROUP_SIZE
    return ba
