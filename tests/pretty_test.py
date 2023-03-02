import pytest
from print_ext.pretty import pretty
from .printer_test import _printer
from print_ext.table import Table
from .testutil import printer

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
    o,p = _printer(color=True)
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
