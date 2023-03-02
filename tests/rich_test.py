import pytest
from print_ext.rich import Rich
from print_ext.line import Line, SMark as SM
from print_ext.span import Span
from .testutil import ostr_ctx, debug_dump

class RichTest(Rich):
    context_defaults = dict(rt='a')

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.calls = []
        self(*args)
    
    def rich_append(self, el, ctx):
        if isinstance(el, str): el = Line(parent=self, **ctx).insert(0,Span(el))
        self.calls.append(el)

    def rich_tab(self, ctx):
        self.calls.append('\t')

    def rich_newline(self, ctx):
        self.calls.append('\n')

    def __str__(self):
        return ','.join(map(str, self.calls))



class SpecialChars():
    def __str__(self):
        return '\b \t \n \v \f \r'



def test_rich_pop_two():
    t = RichTest(style='6-7')
    t('\b1\b2 the', 'bad', style='8-9')('bob')
    print('\n'.join(debug_dump(t)))
    assert(t.calls[0].styled() == ('the', [SM('6',0,3), SM('7',0,3), SM('8',0,3), SM('9',0,3), SM('1',0,3), SM('2',0,3)]))
    assert(t.calls[1].styled() == ('bad', [SM('6',0,3), SM('7',0,3), SM('8',0,3), SM('9',0,3)]))
    assert(t.calls[2].styled() == ('bob', [SM('6',0,3), SM('7',0,3)]))
 


def test_rich_pop_mid():
    t = RichTest(style='7')
    t('\b2\b1$ cow', 'fox', '\b4\b$ cat', style='9-8')
    assert(t.calls[0].styled() == ('cow', [SM('7',0,3), SM('9',0,3), SM('8',0,3), SM('2',0,3), SM('1',0,3)]))
    assert(t.calls[1].styled() == ('fox', [SM('7',0,3), SM('9',0,3), SM('8',0,3), SM('1',0,3)]))
    assert(t.calls[2].styled() == ('cat', [SM('7',0,3), SM('9',0,3), SM('8',0,3), SM('4',0,3)]))



def test_rich():
    t = RichTest()#rt='b')
    #assert(t['rt'] == 'a')
    assert(str(t('bob')) == 'bob')
    assert(str(RichTest()('\t')('', '\v')) == '\t,\n')



@pytest.mark.skip(reason="Not implemented")
def test_l10n():
    t = 'xxx\fa_b_c abc\fa a\fa_b ab\fa_q aq'
    assert(str(RichTest(t)) == 'xxx')
    assert(str(RichTest(t,lang='a')) == 'a')
    assert(str(RichTest(t,lang='a_b')) == 'ab')
    assert(str(RichTest(t,lang='a_b_c')) == 'abc')
    assert(str(RichTest(t,lang='A_Q')) == 'aq')
    assert(str(RichTest(t,lang='a_q_d')) == 'aq')
    assert(str(RichTest(t,lang='a_b_q')) == 'ab')
    assert(str(RichTest(t,lang='a_f')) == 'a')
    assert(str(RichTest(t,lang='c')) == 'xxx')
    assert(str(RichTest(t,lang='c_b_c')) == 'xxx')



def test_append_tel():
    p = RichTest(z='cob')
    a = RichTest('hi', parent=p)
    assert(a['z'] == 'cob')
    b = RichTest(a, z='bob')
    assert(b.calls[0]['z'] == 'cob') # a  shouldn't get reparented to b



def test_rich_call_kwargs():
    r = RichTest('0','1', a=3, m=4)
    r('2', a=9, q=10)
    assert(r.calls[0]['a'] == 3)
    assert(r.calls[0]['q'] == None)
    assert(r.calls[2]['a'] == 9)
    assert(r.calls[2]['q'] == 10)
    r('3')
    assert(r.calls[3]['a'] == 3)
    assert(r.calls[0]['q'] == None)
    assert(r.calls[0]['m'] == 4)



def test_append_non_string():
    special_chars = SpecialChars()
    assert(str(RichTest(1,2,[3,4])) == f'1,2,{[3,4]}')
    assert(str(RichTest(special_chars).calls[0]) == '\\x08      \\x0a \\x0b \\x0c \\x0d')



def test_cleandoc():
    assert(str(RichTest('''   The quick
        brown
        fox
    
    ''')) == 'The quick,\n,brown,\n,fox')
    assert(str(RichTest('a\n  b\n  c\v\n\n\n')) == 'a,\n,b,\n,c')
    assert(str(RichTest('\n  a\n  b\n  c\v\n\n\n')) == 'a,\n,b,\n,c')
    


def test_tabs():
    assert(str(RichTest('a\tb\v\tc\t\v')) == 'a,\t,b,\n,\t,c,\t,\n')
    assert(str(RichTest('a\n\t\tb\tc\n\t\td\n\t\t\te\n\t\t')) == 'a,\n,b,\t,c,\n,d,\n,\t,e')
    assert(str(RichTest('\t\n\ta \n\tb\t\n\tc\t\t\n\t\n\t\t\t')) == 'a ,\n,b,\t,\n,c,\t,\t')



def test_rich_attr():
    a = RichTest('\bR\bB a')
    assert(str(a) == 'a')
    assert(a.calls[0]['style'] == ('R','B'))
    a = RichTest('\bR \br \bpi=3.4 a')
    assert(str(a) == 'a')
    assert(a.calls[0]['style'] == ('R','r'))
    assert(a.calls[0]['PI'] == 3.4)



def test_rich_pop():
    a = RichTest('\ba=1 \ba=2 bob \b the \b cob', a=10)
    assert(a.calls[0]['a'] == 2)
    assert(a.calls[1]['a'] == 1)
    assert(a.calls[2]['a'] == 10)



def test_autopop_call():
    a = RichTest('\ba=1$','b')
    a('2')
    assert(a.calls[0]['a'] == 1)
    assert(a.calls[1]['a'] == None)



def test_autopop_str():
    a = RichTest('\ba=1 a','b')
    assert(a.calls[0]['a'] == 1)
    assert(a.calls[1]['a'] == None)



def test_multi_style():
    r = RichTest('\bx$ hi', '\vbye', '\v\by bob', 'coj', style='z')
    r('jim')
    a = r.calls
    print(a)
    assert(a[0]['style'] == ('z','x'))
    assert(a[2]['style'] == ('z','x'))
    assert(a[4]['style'] == ('z','x','y'))
    assert(a[5]['style'] == ('z','x'))
    assert(a[6]['style'] == ('z',))


