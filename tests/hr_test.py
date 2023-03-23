
from print_ext.hr import HR
from print_ext.line import SMark as SM
from print_ext import Flex, Text, StringPrinter
from .testutil import flat, styled

def test_hr_hello_pretty():
    #o, p = printer(width=10, ascii=True)
    hr = HR('\b2 hi', border_style='1', ascii=True)
    assert(styled(hr, w=10)[0] == ('-[ hi ]---', [SM('1',0,3), SM('2',3,5), SM('1',5,10)]))



def test_hr_blank():
    assert(flat(HR(width_max=10, ascii=True)) == ['----------'])
    assert(flat(HR(border=('t:abcde'))) == ['acd'])
    assert(HR().width == 3)
    assert(HR(width_max=5).width == 5)
    assert(flat(HR('','',width_max=4,ascii=True)) == ['----'])



def test_hr_just_h():
    p = StringPrinter(width_max=10, ascii=True)
    p.hr('hi', just='<')
    assert(str(p) == '-[ hi ]---\n')
    h = HR('hi', just='|', ascii=True, width_max=10, style='y')
    assert([f.styled() for f in h.flatten()][0] == ('--[ hi ]--', [SM('y',0,10)]))
    assert([f.styled() for f in h.flatten(w=9)][0] == ('-[ hi ]--', [SM('y',0,9)]))
    h['just'] = ':'
    assert([f.styled() for f in h.flatten(w=9)][0] == ('--[ hi ]-', [SM('y',0,9)]))
    print('\n\n\n\n')
    h['just'] = '>'
    assert([f.styled() for f in h.flatten()][0] == ('---[ hi ]-', [SM('y',0,10)]))



def test_hr_just_v():
    h = HR('a\vbbb\vc\v', ascii=True, width_max=11)
    assert([f.styled()[0] for f in h.flatten()] == [' [ a   ]   ', ' [ bbb ]   ','-[ c   ]---',' [     ]   '])
    h['just'] = '_'
    assert([f.styled()[0] for f in h.flatten()] == [' [ a   ]   ', ' [ bbb ]   ',' [ c   ]   ','-[     ]---'])
    h['just'] = '|^'
    assert([f.styled()[0] for f in h.flatten()] == ['--[  a  ]--', '  [ bbb ]  ','  [  c  ]  ','  [     ]  '])
    h['just'] = '|-'
    h['ascii'] = False
    assert([f.styled()[0] for f in h.flatten()] == ['  │  a  │  ', '──┤ bbb ├──','  │  c  │  ','  │     │  '])
    h['just'] = '>'
    assert([f.styled()[0] for f in h.flatten()] == ['   │   a │ ', '   │ bbb │ ','───┤   c ├─','   │     │ '])



def test_hr_small():
    h = HR('hello world', ascii=True, wrap=False)
    assert([f.styled()[0] for f in h.flatten()] == ['-[ hello world ]-'])
    assert([f.styled()[0] for f in h.flatten(w=11)] == ['-[ he~ld ]-'])
    assert([f.styled()[0] for f in h.flatten(w=7)] == ['-[ ~ ]-'])
    assert([f.styled()[0] for f in h.flatten(w=6)] == ['hel~ld'])
    h['wrap']=True
    assert([f.styled()[0] for f in h.flatten(w=11)] == [' [ hello ] ', '-[ \\  wo ]-', ' [ \\ rld ] '])



def test_hr_clone():
    h = HR('bob', ascii=False)
    print(h['width_max'])
    assert([str(x) for x in h.flatten()] == ['─┤ bob ├─'])
    assert([str(x) for x in Text(h,h).flatten()] == ['─┤ bob ├──┤ bob ├─'])



def test_hr_infinity():
    p = StringPrinter(ascii=True)
    p(HR('\b1 hi'))
    assert(str(p) == '-[ hi ]-\n')



def test_hr_infinity_no_title():
    p = StringPrinter(ascii=True)
    p.hr()
    assert(str(p) == '---\n')



def test_hr_joins():
    p = StringPrinter()
    p.hr('hi', border='=')
    assert(str(p) == '═╣ hi ╠═\n')



def test_hr_joins_ascii():
    p = StringPrinter(ascii=True)
    p.hr('hi', border='=')
    assert(str(p) == '=# hi #=\n')



def test_hr_joins_bold():
    p = StringPrinter()
    p.hr('hi', border=('#', '-.rl'))
    assert(str(p) == '━┥ hi ┝━\n')



def test_hr_joins_double_space():
    p = StringPrinter()
    p.hr('hi', border=('=', ' .rl'))
    assert(str(p) == '═  hi  ═\n')
