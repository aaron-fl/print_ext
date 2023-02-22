from print_ext.span import Span

class Empty():
    def __str__(self):
        return ''

def test_span():
    l = Span('theこん123')
    assert(len(l.spans) == 1)
    assert(l.width == 10)
    assert(len(l) == 8)


def test_bad():
    l = Span('A\x11_BCDE')
    assert(len(l.spans) == 3)
    assert(l.width == 10)
    assert(len(l) == 7)
    assert(l.spans[2].charsize == 1)
  
def test_empty():
    s = Span()
    assert(not Span())
    assert(not Span(''))
    assert(not Span('',Empty(), Empty()))
    assert(Span('x'))


def test_trim():
    def _f(s, i):
        return str(Span(s).trim(i))
    assert(_f('あかさ', 1) == '')
    assert(_f('あかさ', -1) == '')
    assert(_f('あかさ', -2) == 'さ')
    assert(_f('あかさ', 2) == 'あ')
    assert(_f('12345カタカ678', -3) == '678')
    assert(_f('12345カタカ678', -4) == '678')
    assert(_f('12345カタカ678', -5) == 'カ678')
    assert(_f('12345カタカ678', 5) == '12345')
    assert(_f('12345カタカ678', 6) == '12345')
    assert(_f('12345カタカ678', 7) == '12345カ')
    assert(_f('12345カタカ678', 8) == '12345カ')
    assert(_f('asdf', 8) == 'asdf')
    assert(_f('asdf', -8) == 'asdf')
    assert(str(Span().trim(8)) == '')
    assert(Span('    ').trim(3).width == 3)



def test_find_char_at():
    d0 = [(0,0), (0,1), (1,0), (1,0), (1,0), (1,0), (1,1), (1,1), (2,0), (3,0), (3,0)]
    for i in range(0, 10):
        l = Span('aaか') + 'か' + 'は9' 
        assert(l._find_char_at(i,0) == d0[i]), f"{i} {l!r}"

    d1 = [(0,0), (0,1), (1,0), (1,1), (1,0), (2,0), (1,1), (2,0), (2,0), (3,0), (3,0)]
    for i in range(0, 10):
        l = Span('aaか') + 'か' +'は9'
        assert(l._find_char_at(i,1) == d1[i]), f"{i} {l!r}"


    
if __name__ == '__main__':
    test_find_char_at()
