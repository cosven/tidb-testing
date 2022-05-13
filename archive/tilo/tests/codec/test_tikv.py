import pytest

from tilo.codec.tikv import decode_write_key


@pytest.fixture
def key1():
    return (b"t\x80\x00\x00\x00\x00\x00\x00\xff\x0f_"
            b"r\x80\x00\x00\x00\x00\xff\x00\x02\n\x00"
            b"\x00\x00\x00\x00\xfa\xfa'\xe3\x94\xb1\xf7\xff\xf9")


def test_decode_write_key(key1):
    user_key, ts = decode_write_key(key1)
    print(ts >> 18)
    print(ts - (ts >> 18 << 18))
