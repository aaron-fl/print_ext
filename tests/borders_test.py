import pytest
from print_ext.line import SMark as SM
from print_ext import Flex, StringPrinter, Bdr
from .testutil import styled


def test_Bdr_hi():
    b = Bdr('hi', style='y')
    rows = [r.styled() for r in b.flatten()]
    assert(rows[0] == ('┌──┐',[SM('y',0,4), SM('dem',0,4)]))
    assert(rows[1] == ('│hi│',[SM('y',0,4), SM('dem',0,1),SM('dem',3,4)]))
    assert(rows[2] == ('└──┘',[SM('y',0,4), SM('dem',0,4)]))


def test_bdr_topl_multi():
    b = Bdr('aa\nbbb', ascii=True, border=('-','m:1010'))
    assert(styled(b, h=4) == [
        ('+---', [SM('dem',0,4)]),
        ('|aa ', [SM('dem',0,1)]),
        ('|bbb', [SM('dem',0,1)]),
        ('|   ', [SM('dem',0,1)]),
    ])


def test_Bdr_blank():
    b = Bdr(border=(1,'-'), ascii=True)
    assert([r.styled()[0] for r in b.flatten()] == ['++','++'])



def test_borderdfn_dfns():
    for v in ['aaa', 999, 'a'*7, 'a'*9, 'a'*11, 'a'*12]:
        with pytest.raises(ValueError):
            Bdr.dfn(t=v)
    for v in ['', 'a','aa','aaa','aaaaa']:
        with pytest.raises(ValueError):
            Bdr.dfn(m=v)
    for v in ['bad','also bad', 0, None]:
        print(f"BAD {v!r}")
        with pytest.raises(ValueError):
            Bdr.dfn(v)
    for v in [' ','-','=','{','(','[',False]:
        Bdr.dfn(v)



def test_borderdfn_fld_select():
    assert(Bdr.dfn('c::')['c'] == ':'*8)
    assert(Bdr.dfn(' .tc')['t'] == ' '*10)
    assert(Bdr.dfn(' .tc')['b'] == '\n'*10)
    with pytest.raises(ValueError):
        assert(Bdr.dfn('pad.t.c')['b'] == '\n'*10)



def test_border_pretty():
    p = StringPrinter(ascii=True)
    f = Flex('hi\vthere\vbob')
    assert((f.width, f.height) == (5,3))
    b = Bdr('hi\vthere\vbob', border=Bdr.dfn('-',m='01'), style='1')
    print(b.height, b.calc_height())
    assert(b)
    p(b)
    assert(str(p) == "|hi   |\n|there|\n|bob  |\n")
    
    

def test_border_size():
    b = Bdr.dfn(m='01')
    q = Bdr('the\vquick', border=b)
    assert((b.width, b.height) == (2,0))
    assert((q.width, q.height) == (7,2))



def test_borderdfn_top_line():
    b = Bdr.dfn(t='abcde12345',m='1111')
    assert(b.top_line(3, True) == ' 5 ')
    assert(b.top_line(4, False) == ' ad ')
    assert(b.top_line(5, False) == ' abd ')
    assert(b.top_line(6, False) == ' abcd ')
    assert(b.top_line(7, False) == ' acbcd ')
    assert(b.top_line(8, False) == ' acbccd ')
    b = Bdr.dfn(t='abcde12345',b='qwert09876', c='XYZTxyzt', m='0111')
    assert(b.top_line(99, True) == None)
    assert(b.bottom_line(5, False) == 'ZqwrT')
    b = Bdr.dfn(t='abcde12345',c='XYZTxyzt', m='1')
    assert(b.top_line(5, False) == 'XabdY')
    assert(b.top_line(2, True) == 'xy')
    b = Bdr.dfn(t='abcde12345',c='XYZTxyzt', m='1101')
    assert(b.top_line(5, True) == '1234y')
    b = Bdr.dfn(t='abcde12345',c='XYZTxyzt', m='1110')
    assert(b.top_line(5, True) == 'x1234')
    b = Bdr.dfn(t='abcde12345',c='XYZTxyzt', m='1000')
    assert(b.top_line(5, True) == '13234')
    assert(b.bottom_line(5, True) == None)
    b = Bdr.dfn(m=1)
    assert(b.top_line(7, True) == '       ')
    


#def test_borderdfn_cascade():
    b = Bdr.dfn('=', 1)
    print(b)
    assert(b.top_line(5, True) == '#===#')



def test_borderdfn_override():
    b1 = Bdr.dfn('-', m='111\n',r=' ',c='┌─└─'*2)
    b2 = Bdr.dfn('-', m='11\n1',r='│|', l=' ',)
    assert(b1.update(b2).vals() == ('┌┐└┘++++', '          ', '│││││|||||', '─────-----', '─────-----', '1111'))
    assert(Bdr.dfn().update(Bdr.dfn(t='a')).vals() == ('\n'*8,'\n'*10,'\n'*10,'a'*10,'\n'*10,'\n'*4))
