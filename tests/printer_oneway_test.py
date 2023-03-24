import pytest, io
from print_ext.printer.stream import OnewayPrinter

@pytest.mark.xfail()
def test_oneway_printer_tag():
    assert(0)


def test_oneway_rewind():
    p = OnewayPrinter(stream=io.StringIO())
    with pytest.raises(AttributeError):
        with p.rewind():
            pass

