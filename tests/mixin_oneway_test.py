import pytest, io
from print_ext import Printer, Oneway

@pytest.mark.xfail()
def test_oneway_printer_tag():
    assert(0)


def test_oneway_rewind():
    p = Printer.using(Oneway)(stream=io.StringIO())
    with pytest.raises(ValueError):
        p.rewind()
        
