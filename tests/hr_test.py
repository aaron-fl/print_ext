
from print_ext.hr import HR
from print_ext.line import SMark as SM
from print_ext.flex import Flex
from print_ext.text import Text
from .printer_test import _printer

def test_hr_hello():
    h = HR('hello', ascii=True, style='y')
    assert([l.styled() for l in h.flatten(w=10)] == [('--[hello]-',[SM('y',0,10), SM('dem',0,3), SM('dem',8,10)])])

    h = HR('hello\vto the\vworld', ascii=True, style='y')
    s = [l.styled() for l in h.flatten(w=11)]
    print('\n'.join(x[0] for x in s))
    assert(s[0] == ('  [hello ] ',[SM('y',0,11), SM('dem',0,3), SM('dem',9,11)]))
    assert(s[1] == ('  [to the] ',[SM('y',0,11), SM('dem',0,3), SM('dem',9,11)]))
    assert(s[2] == ('--[world ]-',[SM('y',0,11), SM('dem',0,3), SM('dem',9,11)]))


def test_hello_pretty():
    o, p = _printer(width=10, ascii=True)
    p.hr('hi')
    assert(o.getvalue() == '---[hi]---\n')


def test_hr_clone():
    h = HR('bob')
    assert([str(x) for x in h.flatten()] == ['──┤bob├──'])
    assert([str(x) for x in Text(h,h).flatten()] == ['──┤bob├────┤bob├──'])
