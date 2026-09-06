# coding:utf-8
import pytest

from flanker import _email
from flanker.mime.message.errors import DecodingError
from flanker.mime.message.scanner import scan, ContentType, Boundary
from ... import *

C = ContentType
B = Boundary


def no_ctype_headers_and_and_boundaries_test():
    """We are ok, when there is no content type and boundaries"""
    message = scan(NO_CTYPE)
    assert C('text', 'plain', dict(charset='ascii')) == message.content_type
    pmessage = _email.message_from_string(NO_CTYPE)
    assert message.body == pmessage.get_payload(decode=True).decode('utf-8')
    for a, b in zip(NO_CTYPE_HEADERS, message.headers.iteritems()):
        assert a == b


def multipart_message_test():
    message = scan(EIGHT_BIT)
    pmessage = _email.message_from_string(EIGHT_BIT)

    assert C('multipart', 'alternative', dict(boundary='=-omjqkVTVbwdgCWFRgIkx')) == message.content_type

    p = pmessage.get_payload()[0].get_payload()
    assert p == message.parts[0].body

    p = pmessage.get_payload()[1].get_payload()
    assert p == message.parts[1].body


def enclosed_message_test():
    message = scan(ENCLOSED)
    pmessage = _email.message_from_string(ENCLOSED)

    assert C('multipart', 'mixed', dict(boundary='===============6195527458677812340==')) == message.content_type
    assert u'"Александр Клижентас☯" <bob@example.com>' == message.headers['To']

    assert pmessage.get_payload()[0].get_payload() == message.parts[0].body

    enclosed = message.parts[1]
    penclosed = pmessage.get_payload(1)

    assert ('message/rfc822', {'name': u'thanks.eml'},) == enclosed.headers['Content-Type']

    pbody = penclosed.get_payload()[0].get_payload()[0].get_payload(decode=True)
    pbody = pbody.decode('utf-8')
    body = enclosed.enclosed.parts[0].body
    assert pbody == body

    body = enclosed.enclosed.parts[1].body
    pbody = penclosed.get_payload()[0].get_payload()[1].get_payload(decode=True)
    pbody = pbody.decode('utf-8')
    assert pbody == body

def enclosed_global_message_test():
    message = scan(ENCLOSED_GLOBAL)
    pmessage = _email.message_from_string(ENCLOSED_GLOBAL)

    assert C('multipart', 'mixed', dict(boundary='===============6195527458677812340==')) == message.content_type
    assert u'"Александр Клижентас☯" <bob@example.com>' == message.headers['To']

    assert pmessage.get_payload()[0].get_payload() == message.parts[0].body

    enclosed = message.parts[1]
    penclosed = pmessage.get_payload(1)

    assert ('message/global', {'name': u'thanks.eml'},) == enclosed.headers['Content-Type']

    pbody = penclosed.get_payload()[0].get_payload()[0].get_payload(decode=True)
    pbody = pbody.decode('utf-8')
    body = enclosed.enclosed.parts[0].body
    assert pbody == body

    body = enclosed.enclosed.parts[1].body
    pbody = penclosed.get_payload()[0].get_payload()[1].get_payload(decode=True)
    pbody = pbody.decode('utf-8')
    assert pbody == body

def torture_message_test():
    message = scan(TORTURE)
    tree = tree_to_string(message).splitlines()
    expected = TORTURE_PARTS.splitlines()
    assert len(tree) == len(expected)
    for a, b in zip(expected, tree):
        assert a == b


def fbl_test():
    message = scan(AOL_FBL)
    assert 3 == len(message.parts)


def ndn_test():
    message = scan(NDN)
    assert message.is_delivery_notification()
    assert 3 == len(message.parts)
    assert 'Returned mail: Cannot send message for 5 days' == message.headers['Subject']
    assert 'text/plain' == message.parts[0].content_type
    assert message.parts[1].content_type.is_delivery_status()
    assert message.parts[2].content_type.is_message_container()
    assert 'Hello, how are you' == message.parts[2].enclosed.headers['Subject']


def ndn_2_test():
    message = scan(BOUNCE)
    assert message.is_delivery_notification()
    assert 3 == len(message.parts)
    assert 'text/plain' == message.parts[0].content_type
    assert message.parts[1].content_type.is_delivery_status()
    assert message.parts[2].content_type.is_message_container()


def mailbox_full_test():
    message = scan(MAILBOX_FULL)
    assert message.is_delivery_notification()
    assert 3 == len(message.parts)
    assert 'text/plain' == message.parts[0].content_type
    assert message.parts[1].content_type.is_delivery_status()
    assert message.parts[2].content_type.is_headers_container()


def test_uservoice_case():
    message = scan(LONG_LINKS)
    html = message.body
    message._container._body_changed = True
    val = message.to_string()
    for line in val.splitlines():
        print(line)
        assert len(line) < 200
    message = scan(val)
    assert html == message.body


def test_mangle_case():
    m = scan("From: a@b.com\r\nTo:b@a.com\n\nFrom here")
    m.body = m.body + "\nFrom there"
    m = scan(m.to_string())
    assert 'From here\nFrom there' == m.body


def test_non_ascii_content_type():
    data = """From: me@domain.com
To: you@domain.com
Content-Type: text/点击链接绑定邮箱; charset="us-ascii"

Body."""
    message = scan(data)
    with pytest.raises(DecodingError):
        (lambda x: message.headers)(1)


def test_non_ascii_from():
    message = scan(FROM_ENCODING)
    assert u'"Ingo Lütkebohle" <ingo@blank.pages.de>' == message.headers.get('from')


def notification_about_multipart_test():
    message = scan(NOTIFICATION)
    assert 3 == len(message.parts)
    assert 'multipart/alternative' == message.parts[2].enclosed.content_type


def dashed_boundaries_test():
    message = scan(DASHED_BOUNDARIES)
    assert 2 == len(message.parts)
    assert 'multipart/alternative' == message.content_type
    assert 'text/plain' == message.parts[0].content_type
    assert 'text/html' == message.parts[1].content_type


def bad_messages_test():
    with pytest.raises(DecodingError):
        scan(ENCLOSED_ENDLESS)
    with pytest.raises(DecodingError):
        scan(NDN_BROKEN)

def apache_mime_message_news_test():
    message = scan(APACHE_MIME_MESSAGE_NEWS)
    assert '[Fwd: Netscape Enterprise vs. Apache Secure]' == message.subject


def missing_final_boundaries_enclosed_test():
    message = scan(ENCLOSED_BROKEN_BOUNDARY)
    assert ('message/rfc822', {'name': u'thanks.eml'},) == message.parts[1].headers['Content-Type']


def missing_final_boundary_test():
    message = scan(MISSING_FINAL_BOUNDARY)
    assert message.parts[0].body


def weird_bounce_test():
    message = scan(WEIRD_BOUNCE)
    assert 0 == len(message.parts)
    assert 'text/plain' == message.content_type

    message = scan(WEIRD_BOUNCE_2)
    assert 0 == len(message.parts)
    assert 'text/plain' == message.content_type

    message = scan(WEIRD_BOUNCE_3)
    assert 0 == len(message.parts)
    assert 'text/plain' == message.content_type


def bounce_headers_only_test():
    message = scan(NOTIFICATION)
    assert 3 == len(message.parts)
    assert 'multipart/alternative' == str(message.parts[2].enclosed.content_type)

def message_external_body_test():
    message = scan(MESSAGE_EXTERNAL_BODY)
    assert 2 == len(message.parts)
    assert message.parts[1].parts[1].content_type.params['access-type'] == 'anon-ftp'


def messy_content_types_test():
    message = scan(MISSING_BOUNDARIES)
    assert 0 == len(message.parts)


def disposition_notification_test():
    message = scan(DISPOSITION_NOTIFICATION)
    assert 3 == len(message.parts)


def yahoo_fbl_test():
    message = scan(YAHOO_FBL)
    assert 3 == len(message.parts)
    assert 'text/html' == message.parts[2].enclosed.content_type


def broken_content_type_test():
    message = scan(SPAM_BROKEN_CTYPE)
    assert 2 == len(message.parts)


def missing_newline_test():
    mime = "From: Foo <foo@example.com>\r\nTo: Bar <bar@example.com>\r\nMIME-Version: 1.0\r\nContent-type: text/html\r\nSubject: API Message\r\nhello, world\r\n.\r\n"
    message = scan(mime)
    assert "hello, world\r\n.\r\n" == message.body

    # check that works with mixed-style-newlines
    mime = "From: Foo <foo@example.com>\r\nTo: Bar <bar@example.com>\r\nMIME-Version: 1.0\r\nContent-type: text/html\r\nSubject: API Message\nhello, world"
    message = scan(mime)
    assert "hello, world" == message.body


def tree_to_string(part):
    parts = []
    print_tree(part, parts, "")
    return "\n".join(parts)


def print_tree(part, parts, delimiters=""):
    parts.append("{0}{1}".format(delimiters, part.content_type))

    if part.content_type.is_multipart():
        for p in part.parts:
            print_tree(p, parts, delimiters + "-")

    elif part.content_type.is_message_container():
        print_tree(part.enclosed, parts, delimiters + "-")




NO_CTYPE_HEADERS=[
    ('Mime-Version', '1.0'),
    ('Received', 'by 10.68.60.193 with HTTP; Thu, 29 Dec 2011 02:06:53 -0800 (PST)'),
    ('X-Originating-Ip', '[95.37.185.143]'),
    ('Date', 'Thu, 29 Dec 2011 14:06:53 +0400'),
    ('Delivered-To', 'bob@marley.com'),
    ('Message-Id', '<CAEAsyCbSF1Bk7CBuu6zp3Qs8=j2iUkNi3dPkGe6z40q4dmaogQ@mail.gmail.com>'),
    ('Subject', 'Testing message parsing'),
    ('From', 'Bob Marley <bob@marley.com>'),
    ('To', 'hello@there.com')]


TORTURE_PARTS = """multipart/mixed
-text/plain
-message/rfc822
--multipart/alternative
---text/plain
---multipart/mixed
----text/richtext
---application/andrew-inset
-message/rfc822
--audio/basic
-audio/basic
-image/pbm
-message/rfc822
--multipart/mixed
---multipart/mixed
----text/plain
----audio/x-sun
---multipart/mixed
----image/gif
----image/gif
----application/x-be2
----application/atomicmail
---audio/x-sun
-message/rfc822
--multipart/mixed
---text/plain
---image/pgm
---text/plain
-message/rfc822
--multipart/mixed
---text/plain
---image/pbm
-message/rfc822
--application/postscript
-image/gif
-message/rfc822
--multipart/mixed
---audio/basic
---audio/basic
-message/rfc822
--multipart/mixed
---application/postscript
---application/octet-stream
---message/rfc822
----multipart/mixed
-----text/plain
-----multipart/parallel
------image/gif
------audio/basic
-----application/atomicmail
-----message/rfc822
------audio/x-sun
"""
