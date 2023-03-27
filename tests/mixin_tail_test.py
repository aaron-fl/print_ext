import pytest
from print_ext import Printer, StringIO, Tail
from tests.testutil import flat


def test_printer_tail_full():
    sp = Printer.using(Tail, StringIO)(keep_lines=3)
    sp('a')('b')('c')('ddd')('e')
    assert(str(sp) == 'a\nb\nc\nddd\ne\n')
    assert(flat(sp) == ['c','ddd','e'])
    assert(flat(sp,h=2) == ['ddd','e'])
    sp['just'] = '>'
    assert(flat(sp,w=3, h=2) == ['ddd','  e'])
