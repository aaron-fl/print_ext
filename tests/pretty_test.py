import pytest
from print_ext import pretty, PrettyException, Table, HR
from .testutil import printer, debug_dump


class Beautiful():
    def __init__(self, **kwargs):
        self.vals = kwargs
    
    def pretty(self, **kwargs):
        t = Table(0,0)
        self.vals.update(kwargs)
        for k,v in self.vals.items():
            t(k,'\t',pretty(v),'\t')
        return t 


@pytest.mark.skip()
def test_pretty_list():
    o,p = printer(color=True)
    l = pretty(['the',33,(99,1),{'a':39,'tens':[10,20,30,40]}])
    p(l)
    print(o.getvalue())
    assert(o.getvalue() == '')


def test_pretty_beautiful():
    o, p = printer()
    b = Beautiful(a=3, b=4)
    p.pretty(b, b=5, c=6)
    print(o.getvalue())
    assert(o.getvalue() == 'a 3\nb 5\nc 6\n')


def test_pretty_exception():
    o,p = printer()
    try:
        raise PrettyException(a=[1,2,3], b={'x':'hi','Hello': 'World'})
    except PrettyException as e:
        p(pretty(e))
        print(o.getvalue())
        assert(str(e) == 'PrettyException')
        assert(repr(e) == "PrettyException(a=[1, 2, 3], b={'x': 'hi', 'Hello': 'World'})")
        assert(o.getvalue() == 'PrettyException\na [0] 1\n  [1] 2\n  [2] 3\nb     x hi\n  Hello World\n')
    

def test_pretty_exception_no_pretty():
    class MyException(PrettyException):
        def pretty(self):
            return ''
    o,p = printer()
    try:
        raise MyException(a=[1,2,3], b={'x':'hi','Hello': 'World'})
    except MyException as e:
        p(pretty(e))
        print(o.getvalue())
        assert(str(e) == "MyException(a=[1, 2, 3], b={'x': 'hi', 'Hello': 'World'})")
        assert(repr(e) == "MyException(a=[1, 2, 3], b={'x': 'hi', 'Hello': 'World'})")
        assert(o.getvalue() == '')


def test_pretty_exception_no_style():
    class MyException(PrettyException):
        def pretty(self):
            return HR('\b1 hello')
    o,p = printer(ascii=False, color=True)
    try:
        raise MyException()
    except MyException as e:
        p(pretty(e))
        assert(str(e) == "-[ hello ]-")        
        assert(repr(e) == "MyException()")
        assert(o.getvalue() == '─┤ \x1b[33mhello\x1b[0m ├─\n')
