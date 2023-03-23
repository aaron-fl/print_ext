from print_ext.printer import WidgetPrinter
from .testutil import styled


def test_printer_widget_scalars():
    p = WidgetPrinter(width_max=10)
    p(33)
    assert(p.height == 1)
    assert(styled(p) == [('33', [])])


