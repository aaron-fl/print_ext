import pytest
from print_ext import pretty, PrettyException, Table, HR, StringPrinter
from .testutil import tostr, styled
from print_ext.line import SMark as SM



def test_pretty_str_bytes():
    p = pretty(['33', b'12', u'bob', r'\\'])
    print(p._widgets)
    v = tostr(p)
    assert(v == "[0] 33\n[1] b'12'\n[2] bob\n[3] \\\\\n")



def test_pretty_HasPretty():
    class HasPretty():
        def __init__(self, **kwargs):
            self.vals = kwargs
        
        def __pretty__(self, print, _depth=None, depth=None, **kwargs):
            print(f"{_depth}_{depth}")

    class SubPretty(HasPretty):
        pass

    v = tostr(pretty([HasPretty(), (SubPretty(),)]))
    print(str(v))
    assert(v == '[0] 1_-2\n[1] (0) 2_-3\n')



def test_pretty_FalsePretty():
    class FalsePretty():
        def __pretty__(self): pass
        def __repr__(self): return 'FalsePretty'
    v = tostr(pretty(FalsePretty()))
    assert(v == 'FalsePretty\n')



def test_pretty_RaisesPretty():
    class SomeException(Exception): pass
    class RaisesPretty():
        def __pretty__(self, print, **kwargs): raise SomeException()
    with pytest.raises(SomeException):
        pretty(RaisesPretty())



def test_pretty_tuple():
    def f(*args):
        return pretty(args)
    v = tostr(f('asdf', tuple(), (b'', None)))
    assert(v == "(0) asdf\n(1) ()\n(2) (0) b''\n    (1) None\n")



def test_pretty_list():
    class MyList(list):
        pass
    v = tostr(pretty(['x', MyList([10,""])]))
    assert(v == "[0] x\n[1] [0] 10\n    [1] ''\n")



def test_pretty_dict():
    class BadDict():
        def items(self): return [1,2,3]
        def __repr__(self): return 'BadDict'
    class GoodDict():
        def items(self): return [(2,' '), (3,'\t')]
    assert(tostr(pretty({('tuple',3):BadDict()})) == "('tuple', 3) BadDict\n")
    assert(tostr(pretty({'':'multi\n\nline', 'xy':GoodDict()})) == "'' multi\n\n   line\nxy 2 ' '\n   3 '\\t'\n")



def test_pretty_multiple():
    p = StringPrinter()
    p.pretty(None, 'b', 33)
    assert(str(p) == "None\nb\n33\n")



def test_pretty_quote():
    assert(tostr(pretty({'':''})) == "'' ''\n")
    assert(tostr(pretty({'\t':'\t'})) == "'\\t' '\\t'\n")
    assert(tostr(pretty({' ':'  '})) == "' ' '  '\n")
    assert(tostr(pretty({' asdf':'  asdf  '})) == "' asdf' '  asdf  '\n")
    assert(tostr(pretty({'\t':'\t '})) == "'\\t' '\\t '\n")
    assert(tostr(pretty({'\n\n':'\n\t\n'})) == "'\\n\\n' '\\n\\t\\n'\n")
    assert(tostr(pretty({'bob':'33'}, quote=True)) == "'bob' '33'\n")
    assert(tostr(pretty({'bob':'33'})) == "bob 33\n")



def test_pretty_iter():
    class Getitem():
        def __getitem__(self): return 'hi'
        def __repr__(self): return 'Getitem'
    assert(tostr(pretty(Getitem())) == 'Getitem\n')

    class Iter():
        def __iter__(self): return iter([' f ','22'])
    assert(tostr(pretty(Iter())) == "<0> ' f '\n<1> 22\n")
 


def test_pretty_exception():
    class MyIter():
        def __iter__(self):
            self.i = 0
            return self

        def __next__(self):
            if self.i == 4: raise StopIteration()
            self.i += 1
            return ['zero','one','two','three','four'][self.i-1]

        def __repr__(self):
            return 'MyIter'


    p = StringPrinter()
    try:
        raise PrettyException(a=MyIter(), b={'x':'hi','Hello': 'World'}, msg='Something wicked')
    except PrettyException as e:
        p.pretty(e)
        assert(str(e) == 'Something wicked')
        assert(repr(e) == "PrettyException(a=MyIter, b={'x': 'hi', 'Hello': 'World'}, msg='Something wicked')")
        assert(str(p) == 'Something wicked\na <0> zero\n  <1> one\n  <2> two\n  <3> three\nb     x hi\n  Hello World\n')



def test_pretty_exception_no_pretty():
    class MyException(PrettyException):
        def __pretty__(self, print, **kwargs):
            pass
    p = StringPrinter()
    try:
        raise MyException(msg='hello', a=[1,2,3], b={'x':'hi','Hello': 'World'})
    except MyException as e:
        p.pretty(e)#(pretty(e))
        assert(str(e) == "hello")
        assert(repr(e) == "MyException(msg='hello', a=[1, 2, 3], b={'x': 'hi', 'Hello': 'World'})")
        assert(str(p) == '')



def test_pretty_exception_no_style():
    class MyException(PrettyException):
        def __pretty__(self, print, **kwargs):
            print.hr('\b1 hello')
    p = StringPrinter(ascii=False, color=True)
    try:
        raise MyException()
    except MyException as e:
        p.pretty(e)
        assert(str(e) == "MyException()")        
        assert(repr(e) == "MyException()")
        assert(str(p) == '─┤ \x1b[33mhello\x1b[0m ├─\n')



def test_pretty_styles():
    s = styled(pretty({'a':[(['b'],)]}))
    assert(s == [('a [0] (0) [0] b', [
        SM('1',0,2),
        SM('2',2,6), SM('dem',2,3), SM('dem',4,6),
        SM('3',6,10), SM('dem',6,7), SM('dem',8,10),
        SM('1',10,14), SM('dem',10,11), SM('dem',12,14)
    ])])
    


def test_pretty_depthstop():
    assert(tostr(pretty({'a':3}, depth=0)) == "{'a': 3}\n")
    assert(tostr(pretty({'a':[1,2,3]}, depth=1)) == "a [1, 2, 3]\n")
