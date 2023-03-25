import pytest, io, contextvars
from print_ext import Printer
from print_ext.printer.stream import StreamPrinter, StringPrinter, stack_enum
from print_ext.line import SMark as SM


class StylePrinter(StringPrinter):
    def format_out(self, txt, styles):
        print(f'format_out "{txt}"  styles:{styles}')
        stripped = txt.rstrip()
        s = ''
        for t,stk in stack_enum(txt, styles):
            s += stripped[:len(t)] + ('_' if not stk else ''.join(stk))
            stripped = stripped[len(t):]
        return s



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
    p = StylePrinter()
    p('x','y','\b3 z     ')
    assert(str(p) == 'xy_z3\n')



@pytest.mark.skip(reason="Not implemented")
def test_lang():
    p = StylePrinter(lang='JA')
    p('hello\fja こんにちは')
    assert(repr(str(p)) == r"'こんにちは_\n'")



def test_color():
    p = StylePrinter()
    p('\berr ERROR',' j/k')
    assert(repr(str(p)) == r"'ERRORerr j/k_\n'")
    


def test_printer_default_styles():
    p = StringPrinter(color=True)
    p('the ', '\bem-_ Quick\vbrown', ' fox')
    assert(repr(str(p)) == repr('the \x1b[1;4mQuick\x1b[0m\n\x1b[1;4mbrown\x1b[0m fox\n'))
    p = StringPrinter()
    p('the ', '\br_ Quick\vbrown', ' fox')
    assert(repr(str(p)) == repr('the Quick\nbrown fox\n'))



def test_printer_default_underscore():
    p = StringPrinter(color=True)
    p('the \br_$ quick ','\b!\b;$ brown', ' fox')
    assert(repr(str(p)) == repr('the \x1b[4;31mquick \x1b[1;2mbrown\x1b[0;2;4;31m fox\x1b[0m\n'))
    


def test_printer_default_bold():
    p = StringPrinter(color=True)
    p('the ', '\b! quick',' fox')
    assert(repr(str(p)) == repr('the \x1b[1mquick\x1b[0m fox\n'))



def test_printer_to_str():
    p = StringPrinter()
    p('hello', ' \b1 world')
    assert(p.stream.getvalue() == 'hello world\n')



@pytest.mark.xfail()
def test_printer_widgets():
    raise(False)



@pytest.mark.xfail()
def test_printer_blank():
    ''' Don't merge blank lines within a widget '''
    raise(False)



@pytest.mark.xfail()
def test_abc_printer_tag():
    assert(0)



def test_printer_replace():
    p = StringPrinter()
    def in_ctx():
        Printer.replace(p)
        Printer('hi')
        assert(str(p) == 'hi\n')
        ctx = contextvars.copy_context()
        Printer.replace(StringPrinter(filter=lambda t: t.get('show', False)), context=ctx)
        Printer('bye')
        assert(str(p) == 'hi\nbye\n')
        def sub_ctx():
            Printer('xyz')
            assert(str(Printer()) == '')
            Printer('qwerty', tag='show')
            assert(str(Printer()) == 'qwerty\n')
        ctx.run(sub_ctx)
        Printer('done')
        assert(str(Printer()) == 'hi\nbye\ndone\n')

    contextvars.copy_context().run(in_ctx)
