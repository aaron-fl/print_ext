import pytest, io
from print_ext.printer import Flattener, stack_enum
from print_ext.line import SMark as SM
from .testutil import printer


class PrinterTest(Flattener):
    def format_out(self, txt, styles):
        print(f'format_out "{txt}"  styles:{styles}')
        stripped = txt.rstrip()
        s = ''
        for t,stk in stack_enum(txt, styles):
            s += stripped[:len(t)] + ('_' if not stk else ''.join(stk))
            stripped = stripped[len(t):]
        return s



def _test_printer(**kwargs):
    o = io.StringIO()
    p = PrinterTest(stream=o, **kwargs)
    return o,p


def test_stack_enum():
    def _tst(*args):
        sout = ''
        for s,stk in stack_enum(*args):
            sout += f"{s}[{''.join(stk)}]"
        return sout
    # This is impossible from styled() assert(_tst('abcdef', [SM('0',0,3), SM('0',3,6)]) == 'abcdef[0]')
    assert(_tst('abcdef', [SM('0',0,6), SM('1',0,6),SM('',1,5),SM('',2,4)]) == 'a[01]b[0]cd[]e[0]f[01]')
    assert(_tst('abcdef', [SM('1',1,4)]) == 'a[]bcd[1]ef[]')
    assert(_tst('abcdef', [SM('0',0,1), SM('1',1,4),SM('2',1,3)]) == 'a[0]bc[12]d[1]ef[]')
    assert(_tst('abcdef', [SM('0',0,1), SM('1',1,4),SM('2',1,3)]) == 'a[0]bc[12]d[1]ef[]')
    assert(_tst('abcdef', [SM('0',0,6), SM('1',3,6)]) == 'abc[0]def[01]')
    assert(_tst('abcdef', [SM('0',0,6), SM('1',2,5)]) == 'ab[0]cde[01]f[0]')
    assert(_tst('abcdef', [SM('0',0,6), SM('1',0,6)]) == 'abcdef[01]')



def test_print_call():
    o,p = _test_printer()
    p('x','y','\b3 z     ')
    assert(o.getvalue() == 'xy_z3\n')


@pytest.mark.skip(reason="Not implemented")
def test_lang():
    o,p = _test_printer(lang='JA')
    p('hello\fja こんにちは')
    assert(repr(o.getvalue()) == r"'こんにちは_\n'")


def test_color():
    o,p = _test_printer(lang='JA')
    p('\berr ERROR',' j/k')
    assert(repr(o.getvalue()) == r"'ERRORerr j/k_\n'")
    

def test_printer_default_styles():
    o,p = printer(color=True)
    p('the ', '\bem-_ Quick\vbrown', ' fox')
    print(o.getvalue())
    assert(repr(o.getvalue()) == repr('the \x1b[1;4mQuick\x1b[0m\n\x1b[1;4mbrown\x1b[0m fox\n'))
    o,p = printer()
    p('the ', '\br_ Quick\vbrown', ' fox')
    print(o.getvalue())
    assert(repr(o.getvalue()) == repr('the Quick\nbrown fox\n'))


def test_printer_default_underscore():
    o,p = printer(color=True)
    p('the \br_$ quick ','\b!\b;$ brown', ' fox')
    print(o.getvalue())
    assert(repr(o.getvalue()) == repr('the \x1b[4;31mquick \x1b[1;2mbrown\x1b[0;2;4;31m fox\x1b[0m\n'))
    

def test_printer_default_bold():
    o,p = printer(color=True)
    p('the ', '\b! quick',' fox')
    print(o.getvalue())
    assert(repr(o.getvalue()) == repr('the \x1b[1mquick\x1b[0m fox\n'))
    

def test_printer_to_str():
    from print_ext import print
    assert(print.to_str('hello', ' \b1 world') == 'hello world\n')


def test_legacy_print(capfd):
    from print_ext import print
    print.print('hello', 'world', end='x')
    out, _ = capfd.readouterr()
    print(out)
    assert(out == 'hello worldx')

