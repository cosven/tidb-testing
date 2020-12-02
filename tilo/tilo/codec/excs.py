class CodecError:
    pass


class DecodeError(CodecError):
    pass


class InsufficientBytesError(DecodeError):
    """
    insufficient bytes to decode value
    """
