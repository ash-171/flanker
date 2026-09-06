
from flanker.mime.message.headers.wrappers import ContentType

def charset_test():
    c = ContentType('text', 'plain')
    assert 'ascii' == c.get_charset()

    c = ContentType('application', 'pdf')
    assert None == c.get_charset()
