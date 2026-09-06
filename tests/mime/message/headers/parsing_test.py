
from flanker.mime.message.headers import parsing

def test_content_type_star():
    _, ctype = parsing.parse_header('Content-Type: image/* ; name="Stuart *Wells.PNG"')
    assert ctype.value == 'image/*'
