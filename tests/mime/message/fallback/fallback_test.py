# coding:utf-8

from contextlib import closing

from io import StringIO

from flanker import _email
from flanker.mime.message import ContentType
from flanker.mime.message.fallback import create
from flanker.mime.message.scanner import scan
from tests import (IPHONE, ENCLOSED, TORTURE, TEXT_ONLY, MAILFORMED_HEADERS,
                   SPAM_BROKEN_HEADERS, BILINGUAL, MULTI_RECEIVED_HEADERS,
                   MAILGUN_PIC, BOUNCE, ATTACHED_PDF)


def bad_string_test():
    mime = "Content-Type: multipart/broken\r\n\r\n"
    message = create.from_string("Content-Type:multipart/broken")
    assert mime == message.to_string()
    with closing(StringIO()) as out:
        message.to_stream(out)
        assert mime == out.getvalue()
    list(message.walk())
    message.remove_headers()
    assert not (message.is_attachment())
    assert not (message.is_inline())
    assert not (message.is_delivery_notification())
    assert not (message.is_bounce())
    assert message.to_python_message()
    assert None == message.get_attached_message()
    assert str(message)


def bad_string_test_2():
    mime = "Content-Mype: multipart/broken\n\n"
    message = create.from_string(mime)
    assert message.content_type
    assert (None, {}) == message.content_disposition


def bad_python_test():
    message = create.from_python(
        _email.message_from_string("Content-Type:multipart/broken"))
    assert message.to_string()
    with closing(StringIO()) as out:
        message.to_stream(out)
        assert out.getvalue()
    list(message.walk())
    message.remove_headers()
    assert not (message.is_attachment())
    assert not (message.is_inline())
    assert not (message.is_delivery_notification())
    assert not (message.is_bounce())
    assert message.to_python_message()
    assert None == message.get_attached_message()
    assert str(message)


def message_alter_body_and_serialize_test():
    message = create.from_string(IPHONE)

    parts = list(message.walk())
    assert 3 == len(parts)
    assert u'\r\n\r\n\r\n~Danielle' == parts[2].body
    assert (None, {}) == parts[2].content_disposition
    assert ('inline', {'filename': 'photo.JPG'}) == parts[1].content_disposition

    part = list(message.walk())[2]
    part.body = u'Привет, Danielle!\r\n\r\n'

    with closing(StringIO()) as out:
        message.to_stream(out)
        message1 = create.from_string(out.getvalue())
        message2 = create.from_string(message.to_string())

    parts = list(message1.walk())
    assert 3 == len(parts)
    assert u'Привет, Danielle!\r\n\r\n' == parts[2].body

    parts = list(message2.walk())
    assert 3 == len(parts)
    assert u'Привет, Danielle!\r\n\r\n' == parts[2].body


def message_content_dispositions_test():
    message = create.from_string(IPHONE)

    parts = list(message.walk())
    assert (None, {}) == parts[2].content_disposition
    assert ('inline', {'filename': 'photo.JPG'}) == parts[1].content_disposition

    message = create.from_string("Content-Disposition: Нельзя распарсить")
    parts = list(message.walk(with_self=True))
    # content disposition value is anything (including unicode chars) up to the first space, tab or semicolon
    # but non-ascii value will raise DecodeError
    # FIXME: In python 2 the returned value is binary, should it be unicode?
    expected_cd = u'нельзя'
    assert (expected_cd, {}) == parts[0].content_disposition


def message_from_python_test():
    message = create.from_string(ENCLOSED)
    assert 2 == len(message.parts)
    assert 'multipart/alternative' == message.parts[1].enclosed.content_type
    assert 'multipart/mixed' == message.content_type
    assert not (message.body)

    message.headers['Sasha'] = 'Hello!'
    message.parts[1].enclosed.headers['Yo'] = u'Man'
    assert message.to_string()
    assert str(message)
    assert str(message.parts[0])
    assert '4FEEF9B3.7060508@example.net' == message.message_id
    assert 'Wow' == message.subject

    m = message.get_attached_message()
    assert 'multipart/alternative' == str(m.content_type)
    assert 'Thanks!' == m.subject


def set_message_id_test():
    # Given
    message = create.from_string(ENCLOSED)

    # When
    message.message_id = 'some.message.id@example.net'

    # Then
    assert 'some.message.id@example.net' == message.message_id
    assert '<some.message.id@example.net>' == message.headers['Message-Id']


def clean_subject_test():
    # Given
    message = create.from_string(ENCLOSED)
    message.headers['Subject'] = 'FWD: RE: FW: Foo Bar'

    # When/Then
    assert 'Foo Bar' == message.clean_subject


def references_test():
    # Given
    message = create.from_python(
        _email.message_from_string(MULTI_RECEIVED_HEADERS))

    # When/Then
    assert {'AANLkTi=1ANR2FzeeQ-vK3-_ty0gUrOsAxMRYkob6CL-c@mail.gmail.com', 'AANLkTinUdYK2NpEiYCKGnCEp_OXKqst_bWNdBVHsfDVh@mail.gmail.com'} == set(message.references)


def detected_fields_test():
    # Given
    message = create.from_string(MAILGUN_PIC)
    attachment = message.parts[1]

    # When/Then
    assert 'mailgun.png' == attachment.detected_file_name
    assert 'png' == attachment.detected_subtype
    assert 'image' == attachment.detected_format
    assert not attachment.is_body()


def bounce_test():
    # When
    message = create.from_string(BOUNCE)

    # Then
    assert message.is_bounce()
    assert '5.1.1' == message.bounce.status

    expected_code = (
        'smtp; 550-5.1.1 The email account that you tried to reach does    '
        'not exist. Please try 550-5.1.1 double-checking the recipient\'s email    '
        'address for typos or 550-5.1.1 unnecessary spaces. Learn more at    '
        '550 5.1.1 http://mail.google.com/support/bin/answer.py?answer=6596    '
        '17si20661415yxe.22')

    # In Python 2 email.message.Message used to truncate leading spaces, but
    # in Python 3 leading spaces are preserved.
    assert expected_code == message.bounce.diagnostic_code

def torture_test():
    message = create.from_string(TORTURE)
    assert list(message.walk(with_self=True))
    assert message.size
    message.parts[0].content_encoding = 'blablac'


def text_only_test():
    message = create.from_string(TEXT_ONLY)
    assert u"Hello,\r\nI'm just testing message parsing\r\n\r\nBR,\r\nBob" == message.body
    assert not message.is_bounce()
    assert None == message.get_attached_message()


def message_headers_equivalence_test():
    """
    FallbackMimePart headers match MimePart headers exactly for the same input.
    """
    # Given
    message = scan(ENCLOSED)
    fallback_message = create.from_string(ENCLOSED)

    # When
    assert message.headers.items() == fallback_message.headers.items()


def message_headers_mutation_test():
    """
    FallbackMimePart headers match MimePart headers exactly for the same input.
    """
    # Given
    orig = create.from_string(ENCLOSED)
    assert 'Wow' == orig.headers['Subject']
    assert ContentType('multipart', 'mixed', {'boundary': u'===============6195527458677812340=='}) == orig.headers['Content-Type']

    # When
    del orig.headers['Subject']
    orig.headers['Content-Type'] = ContentType('text', 'foo')
    orig.headers.prepend('foo-bar', 'hello')
    orig.headers.add('blah', 'kitty')
    restored = create.from_python(orig.to_python_message())

    # Then
    assert 'Subject' not in restored.headers
    assert '' == restored.subject
    assert ContentType('text', 'foo') == restored.headers['Content-Type']


def message_headers_append_test():
    """
    `prepend` and `add` both insert a header at the beginning and the end of the
    header list.
    """
    # Given
    orig = create.from_string(ENCLOSED)

    # When
    orig.headers.prepend('foo-bar', 'hello')
    orig.headers.add('blah', 'kitty')
    restored = create.from_python(orig.to_python_message())

    # Then
    assert ('Blah', 'kitty') == restored.headers.items()[0]
    assert ('Foo-Bar', 'hello') == restored.headers.items()[1]


def message_headers_transform_test():
    """
    Header transformation is reflected in the underlying Python standard
    library email object.
    """
    # Given
    orig = create.from_string(ENCLOSED)

    # When
    orig.headers.transform(lambda k, v: ('X-{}'.format(k), v[:1]))
    restored = create.from_python(orig.to_python_message())

    # Then
    assert [('X-Delivered-To', 'b'), ('X-Received', 'b'), ('X-Received', 'b'), ('X-Return-Path', '<'), ('X-Received', 'f'), ('X-Received-Spf', 'p'), ('X-Authentication-Results', 'm'), ('X-Dkim-Signature', 'a'), ('X-Domainkey-Signature', 'a'), ('X-Content-Type', 'm'), ('X-Mime-Version', '1'), ('X-Received', 'b'), ('X-Received', 'f'), ('X-Message-Id', '<'), ('X-Date', 'S'), ('X-From', 'B'), ('X-User-Agent', 'M'), ('X-To', u'"'), ('X-Subject', 'W'), ('X-X-Example-Sid', 'W')] == restored.headers.items()


def bilingual_test():
    message = create.from_string(BILINGUAL)
    assert u"Simple text. How are you? Как ты поживаешь?" == message.headers['Subject']

    message.headers['Subject'] = u"Да все ок!"
    assert u"Да все ок!" == message.headers['Subject']

    message = create.from_string(message.to_string())
    assert u"Да все ок!" == message.headers['Subject']

    assert "" == message.headers.get("SashaNotExists", "")


def broken_headers_test():
    message = create.from_string(MAILFORMED_HEADERS.decode('utf-8', 'replace'))

    assert message.headers['Subject']
    assert str == type(message.headers['Subject'])


def broken_headers_test_2():
    message = create.from_string(SPAM_BROKEN_HEADERS.decode('utf-8', 'replace'))

    assert message.headers['Subject']
    assert str == type(message.headers['Subject'])
    assert ('text/plain', {'charset': 'iso-8859-1'}) == message.headers['Content-Type']
    assert str == type(message.body)


def test_walk():
    message = create.from_string(ENCLOSED)
    expected = [
        'multipart/mixed',
        'text/plain',
        'message/rfc822',
        'multipart/alternative',
        'text/plain',
        'text/html'
        ]
    assert expected[1:] == [str(p.content_type) for p in message.walk()]
    assert expected == [str(p.content_type) for p in message.walk(with_self=True)]
    assert ['text/plain', 'message/rfc822'] == [str(p.content_type) for p in message.walk(skip_enclosed=True)]


def test_binary_attachment():
    """
    A text part body is returned as a unicode string, but any other part type
    body is returned as a binary string.
    """
    # Given
    message = create.from_string(ATTACHED_PDF)

    # When
    parts = [p for p in message.walk(with_self=True)]

    # Then
    def part_spec(p):
        return str(p.content_type), type(p.body)

    assert ('multipart/mixed', type(None)) == part_spec(parts[0])
    assert ('multipart/alternative', type(None)) == part_spec(parts[1])
    assert ('text/plain', str) == part_spec(parts[2])
    assert ('application/pdf', bytes) == part_spec(parts[3])
