import pytest
from print_ext import Printer, Memory


def test_memory_printer_overflow():
    m = Printer.using(Memory)(keep_lines=4)
    assert(m.calc_height() == 0)
    m('hello')
    m('the\nquick')
    assert(m.calc_height() == 3)
    m('fox')
    assert(m.calc_height() == 4)
    assert(not m.overflowed)
    m('ju\nover')
    assert(m.calc_height() == 3)
    assert(m.overflowed == 2)
    assert(m.calc_width() == 4)


def test_memory_printer_rewinder():
    m = Printer.using(Memory)(keep_lines=4)
    rw1 = m.rewind()
    m('x')('x')('x')('x')
    m('x')('x')
    assert(m.overflowed == 2)
    rw2 = m.rewind()
    m('x')('x')
    assert(m.overflowed == 4)
    rw2()
    m('x')
    assert(m.overflowed == 4)
    assert(m.calc_height() == 3)
    rw1()
    assert(m.overflowed == 0)
    assert(m.calc_height() == 0)
    assert(m.widgets == [])
    

def test_memory_printer_clone():
    m = Printer.using(Memory)(keep_lines=4)
    m('1')('2')('3')('4')('5')
    m2 = m.clone()
    assert(m2.overflowed == 1)
    assert(str(list(m.widgets[0][0].flatten())[0]) == '2')
