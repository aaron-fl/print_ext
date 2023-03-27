import pytest
from print_ext import Printer, StringIO


@pytest.mark.xfail()
def test_string_printer_tag():
    assert(0)



def test_string_printer_rewind():
    s = Printer.using(StringIO)()
    s('hello')
    with s.rewind() as rewind:
        s('world')
        rewind()
    s('y')
    s('z')
    assert(str(s) == 'hello\ny\nz\n')



def test_string_printer_rewind_nested():
    s = Printer.using(StringIO)()
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
