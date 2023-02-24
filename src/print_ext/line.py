import copy, sys
from functools import reduce
from collections import namedtuple
from .span import Span
from .context import Context, CVar, BoolCVar, IntCVar
from .rich import Rich
from tests.testutil import ostr, context_info, ostr_ctx, debug_dump

class Just():
    __slots__ = ('hv',)
    def __init__(self, hv):
        if isinstance(hv, str):
            if len(hv) == 1:
                self.hv = ('',hv) if hv in '_-~^' else (hv,'')
            else:
                self.hv = tuple(hv)
        else:
            self.hv = hv.hv if isinstance(hv, Just) else (hv or ('',''))
        if self.hv[0] not in '<|:>': raise ValueError(f"Invalid horizontal justification character '{self.hv[0]}'")
        if self.hv[1] not in '_-~^': raise ValueError(f"Invalid vertical justification character '{self.hv[1]}'")

    def h(self, default='<'):
        return self.hv[0] or default

    def v(self, default='^'):
        return self.hv[1] or default

    def __repr__(self):
        return f'Just({self.hv[0]+self.hv[1]!r})'



class JustCVar(CVar):
    def canon(self, sval):
        return Just(sval)

    def merge(self, val, pval):
        val = Just(val)
        pval = Just(pval)
        return Just((val.h(pval.hv[0]), val.v(pval.hv[1])))



class StyleCVar(CVar):
    def canon(self, sval):
        if isinstance(sval, str):
            if ' ' in sval: raise ValueError(f"No spaces allowed in style string '{sval}'")
            if not sval: return None
            sval = tuple(sval.split('-'))
        return sval[-1 - list(reversed(sval)).index(''):] if '' in sval else sval


    def merge(self, val, pval):
        if '' in val: return val[-1 - list(reversed(val)).index(''):]
        # find overlap
        for same in range(min(len(pval),len(val)), 0, -1):
            if pval[-same:] == val[:same]:
                return pval + val[same:]
        return pval + val
        

style_cvar = Context.define(StyleCVar('style',''))
Context.define(BoolCVar('ascii', 'ascii_only'))
Context.define(BoolCVar('text_wrap', 'wrap'))
Context.define(JustCVar('justify', 'just'))
Context.define(IntCVar('wrap_mark_from'))



class SMark():
    __props__ = ('style','s','e')

    def __init__(self,*args):
        self.style, self.s, self.e = args

    def __repr__(self):
        return f'{self.style}/{self.s}-{self.e}'

    def __eq__(self, other):
        return self.style == other.style and self.s == other.s and self.e == other.e



class Line(Rich):
    ''' A Line is a list of Lines and Spans.
    
    It is a Context so it can style the text.
    Only Lines and Spans can be appended (or inserted).
    Anything else will be converted with Span() first and then added.
    Any Lines appended or inserted into this string will become Context children.
    '''
    
    def __init__(self, *args, **kwargs):
        self.__spans = []
        self.__up_to_date = False
        self._changed_size()
        super().__init__(*args, **kwargs)


    @property
    def spans(self):
        while self.rich_stream:
            el, ctx = self.rich_stream.pop(0)
            if el == '\v': el = '\\n'
            self.insert(-1, el, **ctx)
        return self.__spans


    def trim(self, width):
        ''' Trim this string to fit into width

        If width >= 0 then keep the left
        If width < 0 then keep the right
        '''
        w = self.width+width if width < 0 else width
        for i, span in enumerate(self.spans):
            if span.width > w: break
            w -= span.width
        else:
            return self
        span = span.trim(-span.width+w) if width < 0 else span.trim(w)
        self.__spans[slice(0,i+1) if width < 0 else slice(i,len(self.__spans))] = [span] if span else []
        self._changed_size()
        return self


    @property
    def width(self):
        if self.__width == None:
            self.__width = reduce(lambda a,x: x.width + a, self.spans, 0)
        return self.__width


    @property
    def height(self):
        return int(self)


    def each_child(self):
        yield from self.spans


    def justify(self, width, justify_h=''):
        ''' Add padding so that we are correctly justified for the given `width`
        '''
        if width == 0: return self
        j = justify_h or Just(self['justify']).h()
        pad = width - self.width
        if pad < 0: raise ValueError(f"This string width ({self.width}) is greater than the given justification width ({width})")
        padl = 0 if j == '<' else pad if j == '>' else pad//2
        padr,padl = (padl, pad-padl) if j == ':' else (pad-padl, padl)
        return self.insert(0, ' '*padl).insert(-1, ' '*padr)



    def insert(self, at, el, **kwargs):
        if isinstance(el, Line):
            pass
        elif hasattr(el, 'flatten'):
            flat = list(el.flatten())
            if not flat: return self
            if at == 0: flat.reverse()
            self.insert(at, flat[0], **kwargs)
            for el in flat[1:]:
                self.insert(at, '\\n', **kwargs)
                self.insert(at, el, **kwargs)
            return self
        else:
            el = Span(el)
        if not el: return self
        if kwargs: el = Line(**kwargs).insert(0, el)
        el = el.ctx_parent(self)
        if self.__spans and isinstance(el, Span) and isinstance(self.__spans[at], Span):
            self.__spans[at] = Span(self.__spans[-1], el) if at else Span(el, self.__spans[0])
        elif at:
            self.__spans.append(el)
        else:
            self.__spans.insert(0, el)
        self._changed_size()
        return self


    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s.__spans = [x if isinstance(x,Span) else x.clone(parent=s, **x.ctx_local) for x in self.spans]
        return s


    def styled(self):
        ''' Returns a str and a list of style commands (push/pop)
        '''
        tstk = [] # temporary stack
        stack = [] # progressive stack
        #print("\n________________STYLED_______________", f"'{self}' style:{self['style']}\n", '\n'.join(debug_dump(self)))
        
        def _stack_append(style, s, e):         
            if not style: return   
            popped = []
            while tstk and tstk[-1].e <= s: popped.insert(0,tstk.pop()) # Pop old ones
            #print(f"## {''.join(style)}:{s}-{e} {tstk} :: {popped}")
            # Match as many parents as we can
            for same in range(len(style), -1, -1):
                if style[:same] == tuple(y.style for y in tstk[-same:]): break
            style = style[same:]
            #print(f"    {same} matched parents")
            # Extend popped styles
            i = 0
            for p, y in zip(popped, style[:]):
                if p.style != y: break
                if p.e != s: break
                i += 1
                p.e = e
                tstk.append(p)
                style = style[1:]
            #print(f"    {i} extended")
            #print(f"    {style}  new")
            for y in style:
                tstk.append(SMark(y, s, e))
                stack.append(tstk[-1])


        def _styled(part, s, parent, styles):
            if isinstance(part, Line) and (y:=part.ctx_local.get('style',None)):
                styles = style_cvar.merge(y, styles) if styles else y
            if isinstance(part, Span):
                #print(f"_styled {ostr(part)} {s!r} {styles}")
                _stack_append(styles, len(s), len(s)+len(part))
                s += str(part)
            else:
                for sub in part.spans: s = _styled(sub, s, part, styles)
            return s

        return _styled(self, '', self, self['style']), stack


    def _changed_size(self):
        self.__width = None
        self.__len = None


    def flatten(self, w=0, h=0, **kwargs):
        if self.width - (w or 1e99) <= 0:
            rows = [self.clone(parent=self).justify(w)]
        else:
            rows = self._flatten_wrap(w) if w and self['text_wrap'] else self._flatten_no_wrap(w)
        dh = len(rows) - (h or 1e99)
        if dh > 0: # We are overflowing vertically by dh
            vbar = '|' if self['ascii'] else '⋮'
            keep = len(rows) - dh - 1
            n = str(dh+1)
            e = Line(f"{vbar}{n} lines{vbar}\fja {vbar}{n}行{vbar}", style='dem', parent=self)
            if e.width > w: e = Line(style='dem', parent=self).insert(0, f"{vbar}{n}")
            if e.width > w: e = Line(style='dem', parent=self).insert(0, f"{vbar}")
            rows = rows[:keep-keep//2] + [e.justify(w, '|')] + rows[len(rows)-keep//2:]
        return rows if not h else justify_v(rows, h, Just(self['justify']).v(), Line(parent=self).insert(0,' '*w))


    def _flatten_no_wrap(self, w):
        lhs = self.clone().trim(w//2)
        rhs = self.clone().trim(-((w-1)//2))
        inter = Line(('~' if self['ascii'] else '…')*(w-lhs.width-rhs.width), style='dem')
        return [Line(lhs, inter, rhs, parent=self)]
        

    def _flatten_wrap(self, w):
        cur, rows, wmf = self.clone(parent=self), [], max(self['wrap_mark_from'] or 4, 4)
        prefix = '' if w < wmf else '\\ ' if self['ascii'] else '⤷ '
        while True:
            lhs = cur.clone(parent=self).trim(w)
            cur.trim(-(cur.width - lhs.width))  
            rows.append(lhs.insert(-1, ' '*(w-lhs.width)))
            if not cur: break
            l = Line(style='dem').insert(0,prefix)
            if prefix: cur.insert(0, l)
            
        return rows


    def __str__(self):
        return ''.join(map(str, self.spans))


    def __repr__(self):
        return f"Line({', '.join([repr(x) for x in self.spans])})"
        

    def __bool__(self):
        return bool(self.spans)


    def __len__(self):
        if self.__len == None:
            self.__len = reduce(lambda a,x: len(x) + a, self.spans, 0)
        return self.__len
        


def justify_v(rows, h, j, line):
    pad = h - len(rows)
    if pad < 0: raise ValueError(f"{len(rows)} is greater than the given justification height ({h})")
    padt = 0 if j == '^' else pad if j == '_' else pad//2
    padb, padt = (padt, pad-padt) if j == '~' else (pad-padt, padt)
    return [line.clone(parent=line.parent, **line.ctx_local) for _ in range(padt)] + rows + [line.clone(parent=line.parent, **line.ctx_local) for _ in range(padb)]
