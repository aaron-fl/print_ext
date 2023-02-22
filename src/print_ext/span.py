from wcwidth import wcswidth
from collections import namedtuple
from functools import reduce

SingleSpan = namedtuple('SingleSpan', ['text', 'width', 'charsize'])


class Span():
    ''' A Span represents a line of characters as a list of SingleSpan objects.

    It is immutable, as are SingleSpans.
    
    A singleSpan object helps by separating homogenious chunks of characters.
    A Span does not contain line breaks.  If a newline character is added
    to a Span then it will be renderd in escaped form '\'+'n'
    '''
    __slots__ = ('length', 'width', 'spans')

    def __init__(self, *args):
        self.spans = []
        self.length = 0
        self.width = 0
        for arg in args:
            if isinstance(arg, Span):
                self.spans += arg.spans
                self.width += arg.width
                self.length += arg.length
                self._merge_two(len(self.spans) - len(arg.spans) - 1)
                continue
            for span in [arg] if isinstance(arg, SingleSpan) else _SingleSpan_from_str(str(arg)):
                self.width += span.width
                self.length += len(span.text)
                self.spans.append(span)
                self._merge_two(len(self.spans) - 2)
        

    def trim(self, width):
        ''' Return a Span that fits into `width`.

        If `width` >=0 then keep the left.
        If `width` < 0 then keep the right.
        '''
        if not self: return Span()
        i, idx = self._find_char_at(*((self.width+width, 1) if width < 0 else (width,0)))
        if idx != 0:
            span = self.spans[i]
            i += 1 if idx>=len(span.text) else 1 if self._split_at(span, i, idx) == None else 0
        return Span(*(self.spans[i:] if width < 0 else self.spans[:i]))


    def ctx_parent(self, p):
        return self


    def _merge_two(self, idx):
        if idx < 0 or idx + 1 >= len(self.spans): return
        pA = self.spans[idx]
        pB = self.spans[idx+1]
        if pA.charsize == pB.charsize:
            self.spans[idx:idx+2] = [SingleSpan(text=pA.text+pB.text, width=pA.width + pB.width, charsize=pA.charsize)]
            return True
        

    def _find_in_span(self, span, i, w, dir):
        if span.charsize != 0: return span, i, w//span.charsize + (w%span.charsize and dir)
        if (aW:=self._split_at(span, i, len(span.text) // 2)) != None:
            i -= 1
            w += self.spans[i].width - aW
        spanA = self.spans[i]
        return self._find_in_span(spanA, i, w, dir) if w < spanA.width else self._find_in_span(self.spans[i+1], i+1, w-spanA.width, dir)
    

    def _find_char_at(self, width, dir=0):
        assert(self.spans)
        if width < 0: return 0,0
        for i, span in enumerate(self.spans):
            if span.width > width: break
            width -= span.width
        else:
            return i+1, 0
        span, i, idx = self._find_in_span(span, i, width, dir)
        return (i+1, 0) if idx >= len(span.text) else (i, idx)
        

    def _split_at(self, span, i, idx):
        spanA = _new_span(text=span.text[:idx])
        assert(spanA.text)
        spanB = _new_span(text=span.text[idx:])
        assert(spanB.text)
        self.spans[i:i+1] = [spanA, spanB]
        self._merge_two(i+1)
        return spanA.width if self._merge_two(i-1) else None
         

    def __bool__(self):
        return bool(self.spans)


    def __len__(self):
        return self.length


    def __str__(self):
        return reduce(lambda a,s: a + _str_span(s), self.spans, '')


    def __add__(self, other):
        return Span(self, other)


    def __radd__(self, other):
        return Span(other, self)


    def __repr__(self):
        spans = [repr(s.text) for s in self.spans]
        return f"Span({', '.join(spans)})"




def _SingleSpan_from_str(t):
    w = wcswidth(t)
    if w < 0:
        if len(t) == 1:
            w = len(_chr(t[0]))
            yield SingleSpan(text=t, width=w, charsize=w)
        else:
            m = len(t)//2
            yield from _SingleSpan_from_str(t[:m])
            yield from _SingleSpan_from_str(t[m:])
    else:
        if t: yield _new_span(text=t, width=w)



def _new_span(text, width=None):
    lt = len(text)
    w = wcswidth(text) if width==None else width
    assert(w >= 0)
    assert(text)
    return SingleSpan(text=text, width=w, charsize=(1 if w==lt else 2 if w==2*lt else 0))



def _str_span(span):
    return span.text if span.charsize <= 2 else ''.join(map(_chr, span.text))



def _chr(c):
    o = ord(c)
    if o == 9: return '    '
    if o < 256: return f'\\x{o:02x}'
    if o < 65536: return f'\\u{o:04x}'
    return repr(chr(o))[1:-1]

