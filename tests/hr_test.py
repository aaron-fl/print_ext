
from print_ext.hr import HR
from print_ext.line import SMark as SM
from print_ext.flex import Flex
from print_ext.text import Text
from .printer_test import _printer
from .testutil import flat

def test_hr_hello_pretty():
    o, p = _printer(width=10, ascii=True)
    p.hr('hi')
    assert(o.getvalue() == '--[ hi ]--\n')


def test_hr_blank():
    assert(flat(HR(width_max=10, ascii=True)) == ['----------'])
    assert(flat(HR(border=('t:abcde'))) == ['acd'])
    assert(HR().width == 3)
    assert(HR(width_max=5).width == 5)
    assert(flat(HR('','',width_max=4,ascii=True)) == ['----'])


def test_hr_just_h():
    o,p = _printer(width=10, ascii=True)
    p.hr('hi', just='<')
    print(o.getvalue())
    assert(o.getvalue() == '-[ hi ]---\n')
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
    assert([f.styled()[0] for f in h.flatten()] == ['  [ a   ]  ', '  [ bbb ]  ','--[ c   ]--','  [     ]  '])
    h['just'] = '_'
    assert([f.styled()[0] for f in h.flatten()] == ['  [ a   ]  ', '  [ bbb ]  ','  [ c   ]  ','--[     ]--'])
    h['just'] = '^'
    assert([f.styled()[0] for f in h.flatten()] == ['--[ a   ]--', '  [ bbb ]  ','  [ c   ]  ','  [     ]  '])
    h['just'] = '-'
    h['ascii'] = False
    assert([f.styled()[0] for f in h.flatten()] == ['  │ a   │  ', '──┤ bbb ├──','  │ c   │  ','  │     │  '])
    h['just'] = '<'
    assert([f.styled()[0] for f in h.flatten()] == [' │ a   │   ', ' │ bbb │   ','─┤ c   ├───',' │     │   '])



def test_hr_small():
    h = HR('hello world', ascii=True)
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
