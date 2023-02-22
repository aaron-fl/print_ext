import pytest
from print_ext.borders import Borders,BorderDfn
from print_ext.line import SMark as SM
from print_ext.flex import Flex
from .printer_test import _printer


def test_borders_hi():
    b = Borders('hi', style='y')
    rows = [r.styled() for r in b.flatten()]
    assert(rows[0] == ('    ',[SM('y',0,4), SM('dem',0,4)]))
    assert(rows[1] == (' hi ',[SM('y',0,4), SM('dem',0,1),SM('dem',3,4)]))
    assert(rows[2] == ('    ',[SM('y',0,4), SM('dem',0,4)]))


def test_boorders_blank():
    b = Borders(border='box', ascii=True)
    assert([r.styled()[0] for r in b.flatten()] == ['++','++'])


def test_borderdfn_dfns():
    for v in ['aaa',999, 'a'*5, 'a'*7, 'a'*9, 'a'*11, 'a'*12]:
        with pytest.raises(ValueError):
            BorderDfn(t=v)
    for v in ['', 'a','aa','aaa','aaaaa']:
        with pytest.raises(ValueError):
            BorderDfn(m=v)
    for v in ['bad','also bad']:
        with pytest.raises(ValueError):
            BorderDfn(v)
    for v in ['blank','box','dbox','paren','bracket','brace',0]:
        BorderDfn(v)


def test_border_pretty():
    o,p = _printer(color=False)
    f = Flex('hi\vthere\vbob')
    assert((f.width, f.height) == (5,3))
    p(Borders('hi\vthere\vbob', border=BorderDfn('|',m='  **'), style='1'))
    print(o.getvalue())
    assert(repr(o.getvalue()) == "'|hi   |\\n|there|\\n|bob  |\\n'")
    
    

def test_border_size():
    b = BorderDfn(m='xx11')
    q = Borders('the\vquick', border=b)
    assert((b.width, b.height) == (2,0))
    assert((q.width, q.height) == (7,2))



def test_borderdfn_top_line():
    b = BorderDfn(t='abcde12345')
    assert(b.top_line(3, True) == ' 5 ')
    assert(b.top_line(4, False) == ' ad ')
    assert(b.top_line(5, False) == ' abd ')
    assert(b.top_line(6, False) == ' abcd ')
    assert(b.top_line(7, False) == ' acbcd ')
    assert(b.top_line(8, False) == ' acbccd ')
    b = BorderDfn(t='abcde12345',b='qwert09876', c='XYZTxyzt', m='x---')
    assert(b.top_line(99, True) == None)
    assert(b.bottom_line(5, False) == 'ZqwrT')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='----')
    assert(b.top_line(5, False) == 'XabdY')
    assert(b.top_line(2, True) == 'xy')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='--x-')
    assert(b.top_line(5, True) == '1234y')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='---x')
    assert(b.top_line(5, True) == 'x1234')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='-xxx')
    assert(b.top_line(5, True) == '13234')
    assert(b.bottom_line(5, True) == None)
    b = BorderDfn()
    assert(b.top_line(7, True) == '       ')
    b = BorderDfn('dbox')
    assert(b.top_line(5, True) == '#===#')


def test_borderdfn_merge_from():
    b = BorderDfn('blank')
    assert(repr(BorderDfn(t='a').merge_from(b)) == "BorderDfn(c=' '*8,l=' '*10,r=' '*10,t='a'*10,b=' '*10,m='\\n'*4)")
    assert(repr(BorderDfn().merge_from(b)) == "BorderDfn(c=' '*8,l=' '*10,r=' '*10,t=' '*10,b=' '*10,m='\\n'*4)")
    assert(repr(BorderDfn(m='xxxx').merge_from(b)) == "BorderDfn(c=' '*8,l=' '*10,r=' '*10,t=' '*10,b=' '*10,m='x'*4)")
