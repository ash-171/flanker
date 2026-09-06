# coding=utf-8
from flanker.addresslib.quote import smart_quote, smart_unquote


def test_quote():
    assert '"foo, bar"' == smart_quote('foo, bar')
    assert '"foo; bar"' == smart_quote('foo; bar')
    assert '"foo< bar"' == smart_quote('foo< bar')
    assert '"foo> bar"' == smart_quote('foo> bar')
    assert '"foo\\" bar"' == smart_quote('foo" bar')
    assert '"foo: bar"' == smart_quote('foo: bar')


def test_quote__periods():
    assert 'foo. bar' == smart_quote('foo. bar')


def test_quote__spaces():
    assert 'foo bar' == smart_quote('foo bar')
    assert '" foo bar"' == smart_quote(' foo bar')
    assert '"foo bar "' == smart_quote('foo bar ')
    assert '" foo bar "' == smart_quote(' foo bar ')
    assert 'foo\tbar' == smart_quote('foo\tbar')
    assert '"\tfoo\tbar"' == smart_quote('\tfoo\tbar')
    assert '"foo\tbar\t"' == smart_quote('foo\tbar\t')
    assert '"\tfoo\tbar\t"' == smart_quote('\tfoo\tbar\t')


def test_quote__escaping():
    assert '"f\\\\o\\"o \\"bar\\""' == smart_quote('f\\o"o "bar"')
    assert '"\\"foo\\""' == smart_quote('"foo"')
    assert '"\\"foo\\"bar\\""' == smart_quote('"foo"bar"')


def test_quote__nothing_to_quote():
    assert '' == smart_quote('')
    assert 'foo bar' == smart_quote('foo bar')
    assert "!#$%&'*+-/=?^_`{|}~" == smart_quote("!#$%&'*+-/=?^_`{|}~")


def test_unquote():
    assert 'foo bar "(bazz)" blah oops' == smart_unquote('foo "bar \\"(bazz)\\" blah" oops')
    assert 'foo;  bar. \\bazz\\' == smart_unquote('"foo;"  "bar." "\\\\bazz\\\\"')
    assert '"foo"bar"' == smart_unquote('"\\"foo\\"bar\\"')


def test_unquote__nothing_to_unquote():
    assert 'foo\\.;\tbar' == smart_unquote('foo\\.;\tbar')


def test_unquote__unicode():
    assert u'Превед Медвед' == smart_unquote(u'Превед Медвед')
