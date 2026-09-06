# coding:utf-8


from flanker.addresslib.address import is_email
from flanker.mime.message.headers.encodedword import mime_to_unicode


def test_is_email():
    assert is_email("ev@host")
    assert is_email("ev@host.com.com.com")

    assert not (is_email("evm"))
    assert not (is_email(None))


def test_header_to_unicode():
    assert u'Eugueny ώ Kontsevoy' == mime_to_unicode("=?UTF-8?Q?Eugueny_=CF=8E_Kontsevoy?=")
    assert u'hello' == mime_to_unicode("hello")
    assert None == mime_to_unicode(None)
