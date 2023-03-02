import pytest
from print_ext.borders import Borders,BorderDfn
from print_ext.line import SMark as SM
from print_ext.flex import Flex
from .printer_test import _printer


def test_borders_hi():
    b = Borders('hi', style='y')
    rows = [r.styled() for r in b.flatten()]
    assert(rows[0] == ('┌──┐',[SM('y',0,4), SM('dem',0,4)]))
    assert(rows[1] == ('│hi│',[SM('y',0,4), SM('dem',0,1),SM('dem',3,4)]))
    assert(rows[2] == ('└──┘',[SM('y',0,4), SM('dem',0,4)]))



def test_borders_blank():
    b = Borders(border=(1,'-'), ascii=True)
    assert([r.styled()[0] for r in b.flatten()] == ['++','++'])



def test_borderdfn_dfns():
    for v in ['aaa', 999, 'a'*7, 'a'*9, 'a'*11, 'a'*12]:
        with pytest.raises(ValueError):
            BorderDfn(t=v)
    for v in ['', 'a','aa','aaa','aaaaa']:
        with pytest.raises(ValueError):
            BorderDfn(m=v)
    for v in ['bad','also bad', 0, None]:
        print(f"BAD {v!r}")
        with pytest.raises(ValueError):
            BorderDfn(v)
    for v in [' ','-','=','{','(','[',False]:
        BorderDfn(v)



def test_borderdfn_fld_select():
    assert(BorderDfn('c::')['c'] == ':'*8)
    assert(BorderDfn(' .tc')['t'] == ' '*10)
    assert(BorderDfn(' .tc')['b'] == '\n'*10)
    with pytest.raises(ValueError):
        assert(BorderDfn('pad.t.c')['b'] == '\n'*10)



def test_border_pretty():
    o,p = _printer(color=False, ascii=True)
    f = Flex('hi\vthere\vbob')
    assert((f.width, f.height) == (5,3))
    p(Borders('hi\vthere\vbob', border=BorderDfn('-',m='01'), style='1'))
    print(o.getvalue())
    assert(repr(o.getvalue()) == "'|hi   |\\n|there|\\n|bob  |\\n'")
    
    

def test_border_size():
    b = BorderDfn(m='01')
    q = Borders('the\vquick', border=b)
    assert((b.width, b.height) == (2,0))
    assert((q.width, q.height) == (7,2))



def test_borderdfn_top_line():
    b = BorderDfn(t='abcde12345',m='1111')
    assert(b.top_line(3, True) == ' 5 ')
    assert(b.top_line(4, False) == ' ad ')
    assert(b.top_line(5, False) == ' abd ')
    assert(b.top_line(6, False) == ' abcd ')
    assert(b.top_line(7, False) == ' acbcd ')
    assert(b.top_line(8, False) == ' acbccd ')
    b = BorderDfn(t='abcde12345',b='qwert09876', c='XYZTxyzt', m='0111')
    assert(b.top_line(99, True) == None)
    assert(b.bottom_line(5, False) == 'ZqwrT')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='1')
    assert(b.top_line(5, False) == 'XabdY')
    assert(b.top_line(2, True) == 'xy')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='1101')
    assert(b.top_line(5, True) == '1234y')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='1110')
    assert(b.top_line(5, True) == 'x1234')
    b = BorderDfn(t='abcde12345',c='XYZTxyzt', m='1000')
    assert(b.top_line(5, True) == '13234')
    assert(b.bottom_line(5, True) == None)
    b = BorderDfn(m=1)
    assert(b.top_line(7, True) == '       ')
    


#def test_borderdfn_cascade():
    b = BorderDfn('=', 1)
    print(b)
    assert(b.top_line(5, True) == '#===#')



def test_borderdfn_override():
    b1 = BorderDfn('-', m='111\n',r=' ',c='┌─└─'*2)
    b2 = BorderDfn('-', m='11\n1',r='│|', l=' ',)
    assert(b1.update(b2).vals() == ('┌┐└┘++++', '          ', '│││││|||||', '─────-----', '─────-----', '1111'))
    assert(BorderDfn().update(BorderDfn(t='a')).vals() == ('\n'*8,'\n'*10,'\n'*10,'a'*10,'\n'*10,'\n'*4))
