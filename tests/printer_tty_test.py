import pytest,io
from print_ext.printer.stream import TTYPrinter

@pytest.mark.xfail()
def test_tty_printer_tag():
    assert(0)



def test_tty_printer_rewind():
    s = TTYPrinter(stream=io.StringIO())
    s('hello')
    try:
        with s.rewind() as rewind:
            s('jim')
            s('bob')
            rewind()
            s('j')
            raise RuntimeError()
    except RuntimeError:
        assert(s.stream.getvalue() == 'hello\n\x1b[?25ljim\nbob\n\x1b[0J\x1b[2Fj\x1b[0K\n\x1b[0J\x1b[?25h')

