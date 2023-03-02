import pytest
from print_ext.flex import Flex
from print_ext.fill import Fill
from print_ext.text import Text
from print_ext.line import Line, SMark as SM
from .testutil import debug_dump, styled

def f(o, w,h):
    return ','.join(map(str, o.flatten(w=w, h=h)))


def test_flex_clone():
    f = Flex('a\tb\vc\td')
    print('\n'.join(debug_dump(f)))
    print('-----\n', *[f'-{s.styled()[0]}-\n' for s in f.flatten()])
    print('-------\n', f.width, f.height, f.ctx('height_nom', 'width_nom'))
    f2 = Flex(f, '\t', f)
    print('\n\n\n\n')
    print('\n'.join(debug_dump(f2)))
    lines = [str(x) for x in f2.flatten()]
    assert(lines == ['abdabd', ' c  c '])



def test_flex_in_flex():
    p = Flex('bob\vcob\tfoo\vbar')
    f = Flex('ab\tcd\t',p)
    lines = [str(x) for x in f.flatten()]
    assert(lines == ['abcdbobfoo', '    cobbar'])


def test_flex_loops():
    g = Flex('hi')
    i = Flex(g,g)
    lines = [str(x) for x in i.flatten()]
    assert(lines == ['hihi'])



def test_flex_fox():
    fox = Flex(style='1', text_wrap=True, wrap_mark_from=10, justify='>_').tab(wx=5, style='2')('\b3 the',' quick\vbrown\t', 'fox','\t',Fill('y'))
    els = list(fox.each_child())
    print(f"{len(els)} Flex cells")
    for e in els:
        print(f'   {type(e)} {e}')
    el0 = list(els[0].each_child())
    print('\n'.join(debug_dump(els[0])))
    assert(el0[0]['width_max'] == 5)
    assert(el0[0]['width_nom'] == 9)
    assert(els[2]['width_nom'] == 0)
    assert(f(fox, 20, 0) == 'the q         yyyyyy,uick          yyyyyy,brown      foxyyyyyy')
    


def test_flex_small():
    ''' The flex itsself is justified
    '''
    fox = Flex(Fill('x',width_max=3), '\t', Text('y\vz',width_max=4, justify='>'), justify='|')
    assert(f(fox, 10, 0) == ' xxx   y  , xxx   z  ')



@pytest.mark.xfail(reason='not implemented')
def test_flex_large():
    ''' The flex is too large
    '''
    fox = Flex(Fill('x', width_min=3), '\t', Fill('a\nb', width_min=3))
    assert(f(fox, 2, 0) == 'xxxxxaaaaa,xxxxxbbbbb')
   


def test_flex_wrap():
    def fox(**kwargs): return Flex(Fill('123456789'), '\t', Fill('a\vb', width_min=3), '\t', Fill('z', width_min=3), **kwargs)
    assert(f(fox(), 10, 0) == '1234aaazzz,1234bbbzzz')
    assert(f(fox(), 10, 2) == '1234aaazzz,1234bbbzzz')
    assert(f(fox(flex_wrap=True), 10, 3) == '1234aaazzz,1234bbbzzz,1234aaazzz')



def test_flex_height():
    def fox(**kwargs): return Flex(Fill('123456789', width_min=9), '\t', Fill('a\vb', width_min=3), '\t', Fill('z', width_min=3), **kwargs)
    assert(f(fox(flex_wrap=True, ascii='y'), 10, 2) == '1234567891,   |1|    ')
    assert(f(fox(flex_wrap=True), 10, 5) == '1234567891,1234567891,aaaaazzzzz,bbbbbzzzzz,aaaaazzzzz')
    assert(f(Flex('aaaaa\tbbbbb\tccccc\tddddd\teeeee', ascii=1, flex_wrap=True), 5, 3) == 'aaaaa, |3| ,eeeee')


def test_flex_elide():
    assert(f(Flex('a\tb\tc\td\te\tf', ascii='y'), 3, 0) == 'a~f')


def test_flex_str():
    f = Flex('\berr ERROR',' j/k')
    print('\n'.join(debug_dump(f)))
    print('!'*80)
    fl = f.flatten()[0]
    print('\n'.join(debug_dump(fl)))
    print('-'*80)
    assert(fl.styled() == ('ERROR j/k', [SM('err',0,5)]))
    

def test_flex_empty():
    f = Flex()
    assert((f.width, f.height) == (0,0))
    f.flatten()


def test_flex_passthrough():
    l = Line('hi')
    f = Flex(l)
    assert(styled(l,w=10) == styled(f,w=10))
