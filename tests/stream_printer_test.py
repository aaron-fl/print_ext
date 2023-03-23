import pytest, io
from print_ext.printer.stream import StringPrinter, TTYPrinter

def test_string_printer_rewind():
    s = StringPrinter()
    s('hello')
    with s.rewind() as rewind:
        s('world')
        rewind()
    s('y')
    s('z')
    assert(str(s) == 'hello\ny\nz\n')



def test_string_printer_rewind_nested():
    s = StringPrinter()
    s('a')
    with s.rewind() as rewind:
        s('b')
        with s.rewind() as rewind2:
            s('c')('d')
            assert(str(s) == 'a\nb\nc\nd\n')
            rewind2()
            s('e')
        s('f')
        assert(str(s) == 'a\nb\ne\nf\n')
        rewind()
    s('x')
    assert(str(s) == 'a\nx\n')



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


@pytest.mark.xfail()
def test_file_printer():
    assert(0)



@pytest.mark.xfail()
def test_stream_printer_rewind_exception():
    ''' Clean up if something bad happens in a rewind '''
    assert(0)
