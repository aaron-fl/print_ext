import pytest, io
from functools import reduce
from print_ext.table import Table, CellDfn, BorderDfn
from print_ext.fill import Fill
from print_ext.context import Context
from print_ext.printer import Printer
from print_ext.line import SMark as SM
from print_ext.borders import Borders
from .testutil import debug_dump
from .printer_test import _printer

def test_table_x():
    t = Table(3, -1, 5, tmpl='', ascii=True)
    t('test\tx\t')
    t(33,'\t',Fill('a\vb'),'\t',Fill('.'), '\t', 'tは quick brown fox jumped over the lazy dog')
    for line, expect in zip(t.flatten(w=10), ['t~tx33    ', 'aaa.tは~og', 'bbb.      ']):
        assert(line.styled()[0] == expect)
        


def test_table_x2():
    t = Table(3, -1, 5, ascii=True, tmpl='', wrap=True)
    t('test\tx\t')
    t(33,'\t',Fill('a\vb'),'\t',Fill('.'), '\t', 'The quick brown fox jumped over the lazy dog')
    for line, expect in zip(t.flatten(w=15), ['tesx33         ', 't              ', 'aaa.The quick b', 'bbb.\\ rown fox ','aaa.\\ jumped ov','bbb.\\ er the la','aaa.\\ zy dog   ']):
        assert(line.styled()[0] == expect)


def test_table_clone():
    t = Table(0.0, 1, tmpl='')
    t('a\tb\tc\td\t')
    b = t.clone(**t.ctx_local)
    assert([r.styled()[0] for r in b.flatten()] == ['ab','cd'])


def test_table_last_tab():
    t = Table(1,1)
    t('0\t1\t2\t3\t4\t')
    f = list(t.flatten())
    assert(len(f) == 3)
    t = Table(1,1)
    t('0\t1\t2\t3\t')
    f = list(t.flatten())
    assert(len(f) == 2)
    

def test_table_templates():
    t = Table(1,1)
    t('1\t2\ta\tb\t')
    flat = [f.styled() for f in t.flatten()]
    print('\n'.join(f'-{x}-' for x in flat))
    assert(flat[0] == ('1 2',[SM('em',0,3), SM('dem',1,2)]))
    assert(flat[1] == ('a b',[SM('dem',1,2)]))



def test_table_styles():    
    t = Table(-1, -2, -3, ascii=True, tmpl='', style='r')
    t.cell('R0', style='1')
    t.cell('C1', style='y')
    t.cell('R1%2C-1', style='_')
    t('A0\tA1\tA2\t')
    t('B0\tB1\tB2\t')
    t('C0\tC1\tC2\t')
    t('D0\tD1\tD2\t')
    rows = [r.styled() for r in t.flatten()]
    assert(rows[0] == ('~A1A2 ',[SM('r',0,6), SM('1',0,6), SM('dem',0,1), SM('y',1,3)]))
    assert(rows[1] == ('~B1B2 ', [SM('r',0,6), SM('dem',0,1), SM('y',1,3), SM('_',3,6)]))
    assert(rows[2] == ('~C1C2 ', [SM('r',0,6), SM('dem',0,1), SM('y',1,3)]))
    assert(rows[3] == ('~D1D2 ', [SM('r',0,6), SM('dem',0,1), SM('y',1,3), SM('_',3,6)]))
    assert(len(t) == 12)
    


def test_table_play():  
    o,p = _printer(color=True)  
    t = Table(-1, -2, -3, tmpl='pad', ascii=True)
    print(t['tmpl'])
    t('A0\tA1\tA2\tB0\t\b^r$ B1\tB2\t', 'C0\t\b$ C1\tC2\t')
    t('D0\tD1\tD2\t')
    assert([s.styled()[0] for s in t.flatten()] == ['~ ~ A2', '~ ~ B2', '~ ~ C2', '~ ~ D2'])
    assert([s.styled()[0] for s in t.flatten()] == ['~ ~ A2', '~ ~ B2', '~ ~ C2', '~ ~ D2'])
    p(t)
    print(o.getvalue())



def test_table_CellDfn_ctx_extend():
    cells = [ CellDfn('R0', cls=Fill, style='1-2'), CellDfn('C1', cls=Table, style='3'), CellDfn('R0C2', style='4')]
    ctx = Context()
    assert(reduce(lambda a, c: c.ctx_merge(a, 4, 4, 10, 10), cells, ctx) == ctx)
    assert(reduce(lambda a, c: c.ctx_merge(a, 0, 4, 10, 10), cells, ctx)['cls'] == Fill)
    assert(reduce(lambda a, c: c.ctx_merge(a, 0, 1, 10, 10), cells, ctx)['cls'] == Table)
    assert(reduce(lambda a, c: c.ctx_merge(a, 0, 2, 10, 10), cells, ctx)['style'] == ('1','2','4'))



def test_table_CellDfn():
    for s in ['r0', 'R-1', 'R%3', 'R3%4', 'C3', 'R0C0', 'all']:
        print(CellDfn(s))
    for s in ['0', 'C0R0']:
        with pytest.raises(ValueError):
            CellDfn(s)

    c = CellDfn('R0')
    for rc in [(0,0), (0,1), (0, 99)]:
        assert(c.matches(*rc, 10,10))
    for rc in [(1,0), (3,1), (5, 99)]:
        assert(not c.matches(*rc, 10,10))
    
    c = CellDfn('R-4%2C3%3')
    for rc in [(6,3), (8,6), (6, 9)]:
        assert(c.matches(*rc, 10,10))
    for rc in [(0,0), (8,0)]:
        assert(not c.matches(*rc, 10,10))


@pytest.mark.xfail(reason="can't reproduce")
def test_border_hilite_bug():
    o, p = _printer(ascii=True, color=True)
    t= Table(0,0,tmpl='grid')
    t('\by a\tb', '\tc\td\t')
    p(t)
    print(o.getvalue())
    assert(o.getvalue() == '')
    raise(False)



def test_sudoku():
    o,p = _printer()
    b = Table(1,1,1,1,1,1,1,1,1, tmpl='grid,dbl')
    b.cell('C3%3', border=('l:║#','c:╫\n\n\n#\n\n\n'))
    b.cell('R3%3', border=('t:═#','c:╪\n\n\n#\n\n\n'))
    b.cell('R3%3C3%3', border=('c:╬\n\n\n#\n\n\n'))
    b.cell('R0C3%3', border=('c:╦\n\n\n#\n\n\n'))
    b.cell('R3%3C0', border=('c:╠\n\n\n#\n\n\n'))
    b.cell('R-1C3%3', border=('c:\n\n╩\n\n\n#\n'))
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    b('１\t２\t３\t４\t５\t６\t７\t８\t９\t')
    p(b)
    print(o.getvalue())
    assert(o.getvalue() == '╔══╤══╤══╦══╤══╤══╦══╤══╤══╗\n║１│２│３║４│５│６║７│８│９║\n╟──┼──┼──╫──┼──┼──╫──┼──┼──╢\n║１│２│３║４│５│６║７│８│９║\n╟──┼──┼──╫──┼──┼──╫──┼──┼──╢\n║１│２│３║４│５│６║７│８│９║\n╠══╪══╪══╬══╪══╪══╬══╪══╪══╢\n║１│２│３║４│５│６║７│８│９║\n╟──┼──┼──╫──┼──┼──╫──┼──┼──╢\n║１│２│３║４│５│６║７│８│９║\n╟──┼──┼──╫──┼──┼──╫──┼──┼──╢\n║１│２│３║４│５│６║７│８│９║\n╠══╪══╪══╬══╪══╪══╬══╪══╪══╢\n║１│２│３║４│５│６║７│８│９║\n╟──┼──┼──╫──┼──┼──╫──┼──┼──╢\n║１│２│３║４│５│６║７│８│９║\n╟──┼──┼──╫──┼──┼──╫──┼──┼──╢\n║１│２│３║４│５│６║７│８│９║\n╚══╧══╧══╩══╧══╧══╩══╧══╧══╝\n')


@pytest.mark.skip(reason="not implemented")
def test_table_partial_show():
    ''' Show a portion of the table while building.  The col widths may change, so use fixed col widths
    '''
    pass


def test_table_coldfns():
    t = Table(-3,-4,tmpl='',ascii=True)
    t('12345\t12345\t')
    f = [s.styled()[0] for s in t.flatten()][0]
    assert(f == '1~512~5')
