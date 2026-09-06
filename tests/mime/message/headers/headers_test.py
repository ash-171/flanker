# coding:utf-8
import zlib

from io import StringIO

from flanker.mime.message.headers import MimeHeaders, encoding
from tests import BILINGUAL


def headers_case_insensitivity_test():
    h = MimeHeaders()
    h['Content-Type'] = 1
    assert 1 == h['Content-Type']
    assert 1 == h['conTenT-TyPE']
    assert 'cOnTenT-TyPE' in h
    assert 'Content-Type' in h
    assert 1 == h.get('Content-Type')
    assert None == h.get('Content-Type2')
    assert [('Content-Type', 1)] == h.items()


def headers_order_preserved_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]
    h = MimeHeaders(headers)

    # various types of iterations
    should_be = [('Mime-Version', '1'), ('Received', '2'), ('Mime-Version', '3'), ('Received', '4')]
    assert should_be == h.items()
    assert isinstance(h.items(), list)
    assert should_be == [p for p in h.iteritems()]

    # iterate over keys
    keys = ['Mime-Version', 'Received', 'Mime-Version', 'Received']
    assert keys == [p for p in h]
    assert keys == list(h.keys())


def headers_boolean_test():
    assert False == bool(MimeHeaders())
    assert True == bool(MimeHeaders([('A', 1)]))

def headers_to_string_test():
    assert str(MimeHeaders([('A', 1)]))


def headers_multiple_values_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]
    h = MimeHeaders(headers)
    assert ['1', '3'] == h.getall('Mime-Version')

    # set re-sets all values for the message
    h['Mime-Version'] = '5'
    assert ['5'] == h.getall('Mime-Version')

    # use add to add more values
    h.add('Received', '1')
    assert ['1', '2', '4'] == h.getall('Received')

    # use prepend to insert header in the begining of the list
    h.prepend('Received', '0')
    assert ['0', '1', '2', '4'] == h.getall('Received')

    # delete removes it all!
    del h['RECEIVED']
    assert [] == h.getall('Received')


def headers_length_test():
    h = MimeHeaders()
    assert 0 == len(h)

    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]
    h = MimeHeaders(headers)
    assert 4 == len(h)


def headers_alternation_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]

    h = MimeHeaders(headers)
    assert not (h.have_changed())

    h.prepend('Received', 'Yo')
    assert h.have_changed()

    h = MimeHeaders(headers)
    del h['Mime-Version']
    assert h.have_changed()

    h = MimeHeaders(headers)
    h['Mime-Version'] = 'a'
    assert h.have_changed()

    h = MimeHeaders(headers)
    h.add('Mime-Version', 'a')
    assert h.have_changed()

    h = MimeHeaders(headers)
    h.getall('Mime-Version')
    h.get('o')
    assert not (h.have_changed())


def headers_transform_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]

    h = MimeHeaders(headers)

    # transform tracks whether anything actually changed
    h.transform(lambda key,val: (key, val))
    assert not (h.have_changed())

    # ok, now something have changed, make sure we've preserved order and did not collapse anything
    h.transform(lambda key,val: ("X-{0}".format(key), "t({0})".format(val)))
    assert h.have_changed()

    assert [('X-Mime-Version', 't(1)'), ('X-Received', 't(2)'), ('X-Mime-Version', 't(3)'), ('X-Received', 't(4)')] == h.items()

def headers_transform_encodedword_test():
    # Create a header with non-ascii characters that will be stored in encoded-word format.
    headers = [('Subject', encoding.to_mime('Subject', u'Hello ✓'))]
    h = MimeHeaders(headers)

    # transform should decode it for us when we pass decode=True
    h.transform(lambda key,val: (key, val.replace(u'✓', u'☃')), decode=True)
    assert u'Hello ☃' == h.get('Subject')

def headers_parsing_empty_test():
    h = MimeHeaders.from_stream(StringIO(""))
    assert 0 == len(h)

def headers_parsing_ridiculously_long_line_test():
    val = "abcdefg"*100000
    header = "Hello: {0}\r\n".format(val)
    MimeHeaders.from_stream(StringIO(header))


def headers_parsing_binary_stuff_survives_test():
    value = zlib.compress(b"abcdefg")
    header = "Hello: {0}\r\n".format(value)
    assert MimeHeaders.from_stream(StringIO(header))


def broken_sequences_test():
    headers = StringIO("  hello this is a bad header\nGood: this one is ok")
    headers = MimeHeaders.from_stream(headers)
    assert 1 == len(headers)
    assert "this one is ok" == headers["Good"]


def bilingual_message_test():
    headers = MimeHeaders.from_stream(StringIO(BILINGUAL))
    assert 21 == len(headers)
    assert u"Simple text. How are you? Как ты поживаешь?" == headers['Subject']
    received_headers = headers.getall('Received')
    assert 5 == len(received_headers)
    assert 'c2cs24435ybk' in received_headers[0]


def headers_roundtrip_test():
    headers = MimeHeaders.from_stream(StringIO(BILINGUAL))
    out = StringIO()
    headers.to_stream(out)

    headers2 = MimeHeaders.from_stream(StringIO(out.getvalue()))
    assert 21 == len(headers2)
    assert u"Simple text. How are you? Как ты поживаешь?" == headers['Subject']
    received_headers = headers.getall('Received')
    assert 5 == len(received_headers)
    assert 'c2cs24435ybk' in received_headers[0]
    assert headers['Content-Transfer-Encoding'] == headers2['Content-Transfer-Encoding']
    assert headers['DKIM-Signature'] == headers2['DKIM-Signature']


def test_folding_combinations():
    message = """From mrc@example.com Mon Feb  8 02:53:47 PST 1993\nTo: sasha\r\n  continued\n      line\nFrom: single line  \r\nSubject: hello, how are you\r\n today?"""
    headers = MimeHeaders.from_stream(StringIO(message))
    assert 'sasha  continued      line' == headers['To']
    assert 'single line  ' == headers['From']
    assert "hello, how are you today?" == headers['Subject']
