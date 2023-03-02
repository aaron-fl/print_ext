import pytest
from print_ext.text import Text
from print_ext.line import Line, SMark as SM
from .testutil import debug_dump, styled, flat



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
    assert('--'.join(flat(t, w=5)) == 'the q--uick --brown')
    assert(flat(Text()) == [])
    assert(flat(Text('', '', '')) == [])



def test_text_styled():
    t = Text('\bx$ hi', '\vbye', '\v\by bob', 'coj', style='t', ascii='on')
    print('\n'.join(debug_dump(t)))
    assert(styled(t, w=3, h=4) == [
        ('hi ', [SM('t',0,3), SM('x',0,3)]),
        ('bye', [SM('t',0,3), SM('x',0,3)]),
        ('b~j', [SM('t',0,3), SM('x',0,1), SM('y',0,1), SM('dem',1,2), SM('x',2,3)]),
        ('   ', [SM('t',0,3)]),
    ])



def test_text_e():
    p = Text('parent')
    t= Text('ERROR', parent=p, style='err')
    #print('\n'.join(debug_dump(t)))
    assert(styled(t) == [('ERROR', [SM('err',0,5)])])



def test_empty_flattenable():
    s = Text()
    t = Text(s)
    assert(str(t) == '')


@pytest.mark.skip(reason='Not Implemented')
def test_text_lang():
    s = Text('\berr$', 'Danger\fzh 危险', '\b$ !', "Don't hold plutonium\vwith bare hands.\fzh 不要赤手拿钚。")
    assert(flat(s) == ["Danger!Don't hold plutonium", 'with bare hands.           '])
    s = Text('\berr$', 'Danger\fzh 危险', '\b$ !', "Don't hold plutonium\vwith bare hands.\fzh 不要赤\v手拿钚。", lang='zh')
    assert(flat(s) == ['危险!不要赤','手拿钚。   '])
