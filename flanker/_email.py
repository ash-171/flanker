import email
from contextlib import closing
from email.generator import Generator
from email.header import Header
from email.mime import audio
from email.utils import make_msgid
from io import StringIO

_CRLF = '\r\n'
_SPLIT_CHARS = ' ;,'

# The value of email.header.MAXLINELEN constant changed from 76 to 78 in
# Python 3. To make sure that the library behaviour is consistent across all
# Python versions we introduced our own constant.
_MAX_LINE_LEN = 76


from email.policy import Compat32


class _Compat32CRLF(Compat32):
    linesep = _CRLF


_compat32_crlf = _Compat32CRLF()


def message_from_string(string):
    if isinstance(string, bytes):
        return email.message_from_bytes(string, policy=_compat32_crlf)

    return email.message_from_string(string, policy=_compat32_crlf)


def message_to_string(msg):
    """
    Converts python message to string in a proper way.
    """
    with closing(StringIO()) as fp:
        g = Generator(fp, mangle_from_=False, policy=_compat32_crlf)
        g.flatten(msg, unixfrom=False)
        return fp.getvalue()


def format_param(name, val):
    return email.message._formatparam(name, val)


def decode_base64(val):
    return email.base64mime.decode(val)


def encode_base64(val):
    return email.encoders._bencode(val)


def decode_quoted_printable(val):
    return email.quoprimime.header_decode(val)


def detect_audio_type(val):
    return audio._whatsnd(val)


def make_message_id():
    return make_msgid()


def encode_header(name, val, encoding='ascii', max_line_len=_MAX_LINE_LEN):
    header = Header(val, encoding, max_line_len, name)
    return header.encode(_SPLIT_CHARS, linesep=_CRLF)
