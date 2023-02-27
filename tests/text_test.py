import pytest
from print_ext.text import Text
from print_ext.line import Line, SMark as SM
from .testutil import debug_dump



def test_text_nl_style():
    ''' when adding a blank newline the style should still be applied '''
    t=Text('\v\v\v', style='x')
    for row in t.flatten(w=4):
        assert(row.styled() == ('    ', [SM('x',0,4)]))
        


def test_text_clone():
    p = Text()
    t = Text('a\vb')
    y = t.clone(parent=p)
    assert(y != t)
    assert(y.parent == p)
    m = Text(t, t)
    assert(str(m) == 'a\\vba\\vb')



def test_text_nl():
    def _f(*args, w=0, h=0, **kwargs): return ','.join(map(str, Text(*args, **kwargs).flatten(w=w,h=h)))
    assert(_f('''  The
        quick
        brown
          fox
    ''', justify='>') == '  The,quick,brown,  fox')
    assert(_f('\na\nb\n') == 'a,b')
    assert(_f('   a\nb ') == 'a ,b ')



def test_width_height():
    t = Text('The\vquick brown\vfox\v')
    assert(t.width == 11)
    assert(t.height == 4)
    t = Text()
    assert(t.width == 0)
    assert(t.height == 0)
    t = Text('bob')
    assert(t.width == 3)
    assert(t.height == 1)
    t = Text('\v\v')
    assert(t.width == 0)
    assert(t.height == 3)



def test_text_flatten():
    t = Text('the', ' quick\v', 'brown', text_wrap=True, wrap_mark_from=10)
    assert('--'.join(map(str, t.flatten(5,0))) == 'the q--uick --brown')
    t = Text()
    assert(t.flatten() == [])
    t = Text('', '', '')
    assert(t.flatten() == [])



def test_text_styled():
    t = Text('\bx$ hi', '\vbye', '\v\by bob', 'coj', style='t', ascii='on')
    print('\n'.join(debug_dump(t)))
    f = t.flatten(3,4)
    assert('--'.join(map(str,f)) == 'hi --bye--b~j--   ')
    assert(f[0].styled() == ('hi ', [SM('t',0,3), SM('x',0,3)]))
    assert(f[1].styled() == ('bye', [SM('t',0,3), SM('x',0,3)]))
    assert(f[2].styled() == ('b~j', [SM('t',0,3), SM('x',0,1), SM('y',0,1), SM('dem',1,2), SM('x',2,3)]))
    print('\n\n\n\n\n\n')
    assert(f[3].styled() == ('   ', [SM('t',0,3)]))



def test_text_e():
    p = Text('parent')
    t= Text('ERROR', parent=p, style='err')
    #print('\n'.join(debug_dump(t)))
    f = t.flatten()[0]
    assert(f.styled() == ('ERROR', [SM('err',0,5)]))



def test_empty_flattenable():
    s = Text()
    t = Text(s)
    assert(str(t) == '')
