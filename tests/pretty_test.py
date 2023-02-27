import pytest
from print_ext.pretty import pretty
from .printer_test import _printer

@pytest.mark.skip()
def test_pretty_list():
    o,p = _printer(color=True)
    l = pretty(['the',33,(99,1),{'a':39,'tens':[10,20,30,40]}])
    p(l)
    print(o.getvalue())
    assert(o.getvalue() == '')

