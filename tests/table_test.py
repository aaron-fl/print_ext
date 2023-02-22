import pytest, io
from functools import reduce
from print_ext.table import Table, CellRange
from print_ext.fill import Fill
from print_ext.context import Context
from print_ext.printer import Printer
from print_ext.line import SMark as SM
from .testutil import debug_dump


def test_table_x():
    t = Table(3, -1, 5, ascii=True)
    t('test\tx\t')
    t(33,'\t',Fill('a\vb'),'\t',Fill('.'), '\t', 'The quick brown fox jumped over the lazy dog')
    for line, expect in zip(t.flatten(w=10), ['t~tx33    ', 'aaa.The~og', 'bbb.      ']):
        assert(line.styled()[0] == expect)
        


def test_table_x2():
    t = Table(3, -1, 5, ascii=True, wrap=True)
    t('test\tx\t')
    t(33,'\t',Fill('a\vb'),'\t',Fill('.'), '\t', 'The quick brown fox jumped over the lazy dog')
    for line, expect in zip(t.flatten(w=15), ['tesx33         ', 't              ', 'aaa.The quick b', 'bbb.\\ rown fox ','aaa.\\ jumped ov','bbb.\\ er the la','aaa.\\ zy dog   ']):
        assert(line.styled()[0] == expect)


def test_table_last_tab():
    t = Table(1,1)
    t('0\t1\t2\t3\t4\t')
    f = list(t.flatten())
    assert(len(f) == 3)
    t = Table(1,1)
    t('0\t1\t2\t3\t')
    f = list(t.flatten())
    assert(len(f) == 2)
    



def test_table_styles():
    
    t = Table(-1, -2, -3, ascii=True, style='r')
    t.cell('R0', style='!')
    t.cell('C1', style='y')
    t.cell('R1%2C-1', style='_')

    t('A0\tA1\tA2\t')
    t('B0\tB1\tB2\t')
    t('C0\tC1\tC2\t')
    t('D0\tD1\tD2\t')
    rows = [r.styled() for r in t.flatten()]
    assert(rows[0] == ('A0A1A2',[SM('r',0,6), SM('!',0,6), SM('y',2,4)]))
    assert(rows[1] == ('B0B1B2', [SM('r',0,6), SM('y',2,4), SM('_',4,6)]))
    assert(rows[2] == ('C0C1C2', [SM('r',0,6), SM('y',2,4)]))
    assert(rows[3] == ('D0D1D2', [SM('r',0,6), SM('y',2,4), SM('_',4,6)]))
    assert(len(t) == 12)
    

def test_table_CellRange_ctx_extend():
    cells = [ CellRange('R0', cls=Fill, style='1-2'), CellRange('C1', cls=Table, style='3'), CellRange('R0C2', style='4')]
    ctx = Context()
    assert(reduce(lambda a, c: c.ctx_merge(a, 4, 4, 10, 10), cells, ctx) == ctx)
    assert(reduce(lambda a, c: c.ctx_merge(a, 0, 4, 10, 10), cells, ctx)['cls'] == Fill)
    assert(reduce(lambda a, c: c.ctx_merge(a, 0, 1, 10, 10), cells, ctx)['cls'] == Table)
    assert(reduce(lambda a, c: c.ctx_merge(a, 0, 2, 10, 10), cells, ctx)['style'] == ('1','2','4'))



def test_table_CellRange():
    for s in ['R0', 'R-1', 'R%3', 'R3%4', 'C3', 'R0C0']:
        print(CellRange(s))
    for s in ['r0', 'C0R0']:
        with pytest.raises(ValueError):
            CellRange(s)

    c = CellRange('R0')
    for rc in [(0,0), (0,1), (0, 99)]:
        assert(c.matches(*rc, 10,10))
    for rc in [(1,0), (3,1), (5, 99)]:
        assert(not c.matches(*rc, 10,10))
    
    c = CellRange('R-4%2C3%3')
    for rc in [(6,3), (8,6), (6, 9)]:
        assert(c.matches(*rc, 10,10))
    for rc in [(0,0), (8,0)]:
        assert(not c.matches(*rc, 10,10))
