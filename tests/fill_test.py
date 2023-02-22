from print_ext.fill import Fill
from print_ext.line import SMark as SM

def _f(*args, w=0, h=0, **kwargs):
    return ','.join(map(str, Fill(*args, **kwargs).flatten(w,h)))

def test_fill_unicode():
    assert(_f('あかさ', w=8,h=3) == 'あかさあ,あかさあ,あかさあ')
    assert(_f('か', w=1,h=3) == ' , , ')


def test_fill_different_line_width():
    assert(_f('あかa\vxy', w=3, h=3) == 'あ ,xyx,あ ')
    assert(_f('xy\v', w=3, h=3) == 'xyx,   ,xyx')
    assert(_f('abcd','\ve', w=0, h=4) == 'abcd,eeee,abcd,eeee')
    assert(_f('abcd\ve', w=0, h=0) == 'abcd,eeee')


def test_fills():
    assert(_f('', w=3, h=3) == '   ,   ,   ')
    assert(_f('abcde', w=3, h=2) == 'abc,abc')
    assert(_f(w=3, h=2) == '   ,   ')


def test_fill_style():
    f = Fill('\b2 xy', 'z', style='1')
    assert(list(f.flatten(w=7))[0].styled() == ('xyzxyzx', [SM('1',0,7), SM('2',0,2), SM('2',3,5), SM('2',6,7)]))


def test_fill_doctest():
    assert([str(l) for l in Fill().flatten(2,2)] == ['  ', '  '])
    assert([str(l) for l in Fill('abc').flatten(5,2)] == ['abcab','abcab'])
    assert([str(l) for l in Fill('a\v','b').flatten(3,3)] == ['aaa','bbb','aaa'])
