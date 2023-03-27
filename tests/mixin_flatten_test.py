from print_ext import Printer, Flatten
from .testutil import styled


def test_printer_widget_scalars():
    p = Printer.using(Flatten)(width_max=10)
    p(33)
    assert(p.height == 1)
    assert(styled(p) == [('33', [])])


def test_printer_widget_clone():
    p = Printer.using(Flatten)(width_max=10)
    p('hi')
    p(p)
    assert(styled(p) == [('hi',[]), ('hi',[])])

