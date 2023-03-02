import pytest
from print_ext.line import Line, Just, justify_v, SMark as SM, style_cvar
from print_ext.text import Text
from print_ext.span import Span
from print_ext.context import Context
from .testutil import debug_dump, styled


def Ln(*args, **kwargs):
    if isinstance(args[-1], int):
        kwargs['style'] = tuple(str(args[-1]))
        args=args[:-1]
    s = Line(**kwargs)
    for arg in reversed(args):
        s.insert(0, arg)
    return s


class EmptyStr():
    def __str__(self):
        return ''


class EmptyClass(Context):
    def __init__(self, val):
        self.val = [Line()] if val else []
        super().__init__()

    def flatten(self):
        return self.val


class StyleCtx(Context, style='x-y'):
    pass


def test_ctx_style():
    c1 = Context(style='a-b-c')
    c2 = StyleCtx(parent=c1)
    c3 = Context(parent=c2, style='b-c-d')
    print('\n'.join(debug_dump(c3)))
    assert(c3['style'] == style_cvar.canon('x-y-a-b-c-d'))



def test_StyleCVar():
    assert(style_cvar.canon('') == None)
    assert(style_cvar.canon('bob-') == ('',))
    assert(style_cvar.canon('-bob') == ('','bob'))
    assert(style_cvar.canon('-bob--') == ('',))
    assert(style_cvar.canon('--') == ('',))
    assert(style_cvar.canon('-') == ('',))
    assert(style_cvar.canon(('a','','b')) == ('','b'))
    assert(style_cvar.canon('bob--cob') == ('','cob'))
    with pytest.raises(ValueError):
        style_cvar.canon('bob cob')



def test_StyleCVar_merge():
    def _v(parent, val, result):
        assert(style_cvar.merge(style_cvar.canon(val), style_cvar.canon(parent)) == style_cvar.canon(result))
    _v('a-b', '-c-d', '-c-d')
    _v('a-b', 'b-c-d', 'a-b-c-d')
    _v('a-b', 'a-b', 'a-b')
    _v('a-b-a-b', 'a-b', 'a-b-a-b')
    _v('a-b-c', 'a-b', 'a-b-c-a-b')



def test_line_basic():
    s = Line('abc','カタカナ', 33)
    assert(str(s) == 'abcカタカナ33')
    


def test_empty_line():
    s = Line()
    assert(not s)
    assert(not s(''))
    assert(not s())
    assert(s('x'))



def testinsert_empty():
    s = Line()
    for v in ['\b3', '', EmptyClass(False), EmptyClass(True), EmptyStr()]:
        s.append(v)
        assert(repr(s) == 'Line()')



def test_line_clone():
    ''' When adding objects to a line they need to be reparented
    '''
    s1 = Ln('ab', 1)
    s1P = Ln(s1, 'cd', 2)
    assert(s1P.styled() == ('abcd', [SM('2',0,4), SM('1',0,2)]))
    s2 = Ln('ef', 3)
    s2P = Ln(s2, 'gh', 4)
    s = Ln(s1, s2, 5)
    s2P['style'] = '6'
    print('\n'.join(debug_dump(s)), '\n\n-----------\n')
    assert(s.styled() == ('abef', [SM('5',0,4), SM('2',0,2), SM('1',0,2), SM('4',2,4), SM('3',2,4)]))
    assert(s2P.styled() == ('efgh', [SM('6',0,4), SM('3',0,2)]))



def test_line_flatten_clone():
    ''' When a line is flattened it should still be parented correctly
    '''
    s = Line('abc', style='bob')
    rows = list(s.flatten())
    assert(rows[0].parent == s)



def test_line_append_multiline():
    s = Line(Text('bob'))
    assert(str(s) == 'bob')
    assert(str(Line(Text('bob\vcob'))) == 'bob\\ncob')
    assert(str(Line("the\vquick\vbrown")) == 'the\\nquick\\nbrown')



def test_line_append_tab():
    assert(str(Line('the\tquick')) == 'the    quick')



def test_justify_h():
    ''' Line.justify()
    '''
    s = Line('bob', justify=':')
    s.justify(4)
    assert(str(s) == ' bob')
    s.justify(4,justify_h='<')
    assert(str(s) == ' bob')
    s.justify(7,justify_h='|')
    assert(str(s) == '  bob  ')
    with pytest.raises(ValueError):
        s.justify(2)
    


def test_line_no_wrap():
    def _f(s, **kwargs):
        return styled(Line(s, justify='|', ascii='yes', text_wrap=False), **kwargs)[0]
    assert(_f('abcdefghij', w=13) == (' abcdefghij  ', []))
    assert(_f('abcdefghij', w=5) == ('ab~ij', [SM('dem',2,3)]))
    assert(_f('abcdefghij', w=4) == ('ab~j', [SM('dem',2,3)]))
    assert(_f('abcdefghij', w=3) == ('a~j',[SM('dem',1,2)]))
    assert(_f('abcdefghij', w=2) == ('a~',[SM('dem',1,2)]))
    assert(_f('abcdefghij', w=1) == ('~',[SM('dem',0,1)]))
    assert(_f('abcdefghij', w=0) == ('abcdefghij', []))
    assert(_f('aあa', w=4) == ('aあa', []))
    assert(_f('ああa', w=3) == ('~~a', [SM('dem',0,2)]))
    assert(_f('ああa', w=2) == ('~~', [SM('dem',0,2)]))
    assert(_f('test', w=3) == ('t~t', [SM('dem',1,2)]))



def test_line_loop():
    l = Line('hi',style='1')
    l(l,style='2')
    assert(l.styled() == ('hihi',[SM('1',0,4), SM('2',2,4), SM('1',2,4)]))


def test_line_loop_deep():
    b = Line('b', style='1')
    abc = Line('a', b, 'c', style='2')
    assert(abc.styled() == ('abc', [SM('2',0,3), SM('1',1,2)]))
    b(abc)
    print('\n'.join(debug_dump(b)))
    assert(b.styled() == ('babc', [SM('2',0,4), SM('1',0,4), SM('2',1,4), SM('1',2,3)]))


def test_just_defaults():
    j = Just()
    assert((j.h, j.v) == ('',''))
    j = Just(defaults='|-')
    assert((j.h, j.v) == ('|','-'))
    j = Just('_', defaults='|-')
    assert((j.h, j.v) == ('|','_'))
    j = Just('<', defaults='|-')
    assert((j.h, j.v) == ('<','-'))


def test_just_pad():
    j = Just('|-')
    assert(j.pad_v(10) == 5)
    assert(j.pad_h(10) == 5)
    assert(j.pad_v(9) == 4)
    assert(j.pad_h(9) == 4)



def test_line_wrap():
    def _f(s, w=0, h=0, just='|-', wmf=5, **kwargs):
        return [r.styled() for r in  Line(s, justify=just, ascii='y', text_wrap=True, wrap_mark_from=wmf, **kwargs).flatten(w, h)]
    assert(_f('abcdefghij', w=13) == [(' abcdefghij  ',[])])
    assert(_f('abcdefghij', w=3) == [('abc',[]), ('def',[]), ('ghi',[]), ('j  ',[])])
    assert(_f('abcdefghij', w=6) == [('abcdef',[]), ('\\ ghij',[SM('dem',0,2)])])
    assert(_f('abcdefghijabcdefgh', w=11, h=1) == [(' |2 lines| ',[SM('dem',0,11)])])
    assert(_f('abcdefghijabcdefghijkl', w=11, h=2) == [('abcdefghija',[]),(' |2 lines| ',[SM('dem',0,11)])])
    assert(_f('012345678012345601234560123456', w=9, h=3) == [('012345678',[]),('|2 lines|',[SM('dem',0,9)]),('\\ 0123456',[SM('dem',0,2)])])
    assert(_f('1111222233334444555566667777888899990000aaaa', w=4, h=1) == [('|11 ',[SM('dem',0,4)])])
    assert(_f('1111', w=1, h=1) == [('|',[SM('dem',0,1)])])
    #assert(_f('00000111112222233333', w=5, h=2, lang='ja', wmf=10) == [('00000',[]),('|3行|',[SM('dem',0,4)])])



def test_line_split():
    def s(*parts): return Line(*parts)
    def f(i, *parts): return str(s(*parts).trim(i))
    assert(f(-3, "abc", "あ",s('12型34')) == '34')
    assert(f(0, "abc", "あ",s('12型34')) == '')
    assert(f(3, "abc", "あ",s('12型34')) == 'abc')
    assert(f(5, "abc", "あ",s('12型34')) == 'abcあ')
    assert(f(-6, "abc", "あ",s('12型34')) == '12型34')
    assert(f(-7, "abc", "あ",s('12型34')) == '12型34')
    assert(f(6, "abc", "あ",s('12型34')) == 'abcあ1')



def test_line_trim_styles():
    ''' trimming keeps styles
    '''
    s = Ln('abc', Ln('def',1), 'ghi', 2)
    print('\n'.join(debug_dump(s)))
    assert(s.styled() == ('abcdefghi', [SM('2',0,9), SM('1',3,6)]))
    s.trim(4)
    assert(s.styled() == ('abcd', [SM('2',0,4), SM('1',3,4)]))
    s.trim(3)
    assert(s.styled() == ('abc', [SM('2',0,3)]))



def test_line_trim():
    def _f(x): return repr(Ln(Ln('abc'), 'def', Ln('ghi')).trim(x))
    assert(_f(1) == "Line(Line(Span('a')))")
    assert(_f(1000) == "Line(Line(Span('abc')), Span('def'), Line(Span('ghi')))")
    assert(_f(0) == "Line()")
    assert(_f(4) == "Line(Line(Span('abc')), Span('d'))")
    assert(_f(-4) == "Line(Span('f'), Line(Span('ghi')))")
    assert(_f(-1) == "Line(Line(Span('i')))")




def test_style_flatten():
    p = Line('test parent', style='p')
    s = Line('abc', parent=p)
    assert(s.styled() == ('abc', [SM('p',0,3)]))
    s.append('yz')
    assert(s.styled() == ('abcyz', [SM('p',0,5)]))
    s.insert(0, '  ')
    assert(s.styled() == ('  abcyz', [SM('p',0,7)]))
    s.insert(0, Line("o", style='1-2'))
    print('_'*80)
    print('\n'.join(debug_dump(s)), s.width)
    assert(s.styled() == ('o  abcyz', [SM('p',0,8), SM('1',0,1), SM('2',0,1)]))



def test_styled_double():
    s = Ln(Ln('a',1), Ln('b',1))
    assert(s.styled() == ('ab', [SM('1',0,2)]))



def test_extend_two():
    s = Ln(Ln(Ln('a',1),Ln('b',2),3), Ln('c',32), 6)
    #print('\n'.join(debug_dump(s)))
    assert(s.styled() == ('abc', [SM('6',0,3), SM('3',0,3), SM('1',0,1), SM('2',1,3)]))



def test_diffently_parented():
    p1 = Context(style='1')
    p2 = Context(style='2')
    s1 = Line(parent=p1, style='9').insert(0, 'a')
    s2 = Line(parent=p2).insert(0, 'b')
    s3 = Ln(s1,s2,3)
    assert(s3.styled() == ('ab', [SM('3',0,2), SM('1',0,1), SM('9',0,1), SM('2',1,2)]))



def test_pop_one_match_two():
    s = Ln(Ln('a',1), Ln('b',2), Ln('c',31), 3)
    assert(s.styled() == ('abc', [SM('3',0,3), SM('1',0,1), SM('2',1,2), SM('1',2,3)]))



def test_over_extend():
    s = Ln(Ln(Ln('a',1), Ln('b',2), 3), Ln('c',2))
    assert(s.styled() == ('abc', [SM('3',0,2), SM('1',0,1), SM('2',1,2), SM('2',2,3)]))



def test_pop_extend():
    ''' after popping  1  but we are appending 13 so just append 3'''
    s = Ln(Ln('a',2), Ln('b',13), 1)
    assert(s.styled() == ('ab', [SM('1',0,2), SM('2',0,1), SM('3',1,2)]))



def test_pop_extend_nested():
    ''' after popping  121  but we are appending 12123 so just append 23'''
    s = Ln(Ln('a',121), Ln('b',12123))
    assert(s.styled() == ('ab', [SM('1',0,2), SM('2',0,2), SM('1',0,2), SM('2',1,2),SM('3',1,2)]))



def test_pop_before_extend():
    ''' 23236 pop 236  new 236  -> 236? or 23236?'''
    s = Ln(Ln('a',2), Ln('b',523),5)
    assert(s.styled() == ('ab', [SM('5',0,2), SM('2',0,2), SM('3',1,2)]))



def test_pop_extend_new():
    ''' 123 pop 3 new 234   2 is parent 3 is extend 4 is new '''
    s = Ln(Ln('a',3), Ln('b',234),12)
    assert(s.styled() == ('ab', [SM('1',0,2), SM('2',0,2), SM('3',0,2), SM('4',1,2)]))



def test_extend_partial():
    ''' 123 pop 23 new 12.  only extend 2 '''
    s = Ln(Ln('a',23), Ln('b',12), 1)
    assert(s.styled() == ('ab', [SM('1',0,2), SM('2',0,2), SM('3',0,1)]))



def test_styled_nested():
    ''' bug: nested spans dont get styled
    '''
    s = Line('bob', style='p').insert(0, 'abc')
    assert(s.styled() == ('abcbob', [SM('p',0,6)]))
    s.insert(0, Line('xyz', style='1-2'))
    assert(s.styled() == ('xyzabcbob', [SM('p',0,9), SM('1',0,3), SM('2',0,3)]))



def test_styled_dedup_sibling():
    s = Line('\b0$ abc', 'def')
    assert(s.styled() == ('abcdef', [SM('0',0,6)]))



def test_style_justify():
    ''' justified space should not be included in the style '''
    s = Line('abc', style='s', justify='|')
    assert(styled(s, w=7) == [('  abc  ', [SM('s',0,7)])])



def test_subtyles():
    s1 = Line('abc', style='a')
    s2 = Line('def', style='b')
    s3 = Line(s1, s2, style='x-y')
    assert(s3.styled() == ('abcdef', [SM('x',0,6),SM('y',0,6),SM('a',0,3),SM('b',3,6)]))



def test_justify_v():
    rows = [Line('a'), Line('b'), Line('c'), Line('d')]
    r = list(justify_v(rows, 4, Just('-'), Line('xxxx')))
    assert('--'.join(map(str,r)) == 'a--b--c--d')
    r = list(justify_v(rows, 6, Just('-'), Line('xxx')))
    assert('--'.join(map(str,r)) == 'xxx--a--b--c--d--xxx')
    with pytest.raises(ValueError):
        list(justify_v(rows, 3, '-',Line()))
    assert(r[0].styled() == ('xxx', []))
    assert(r[1].styled() == ('a', []))
    assert(r[5].styled() == ('xxx', []))


if __name__=='__main__':
    test_extend_two()