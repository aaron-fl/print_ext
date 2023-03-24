import copy, sys
from math import ceil
from functools import reduce
from collections import namedtuple
from .span import Span
from .context import Context, CVar, BoolCVar, IntCVar
from .rich import Rich



class Just():
    __slots__ = ('hv','h','v')

    def __init__(self, hv=None, defaults=''):
        if not hv:
            hv = ('','')
        elif isinstance(hv, str):
            if len(hv) == 1:
                hv = ('',hv) if hv in '_-~^' else (hv,'')
            else:
                hv = tuple(hv)
        elif isinstance(hv, Just):
            hv = (hv.h, hv.v)
        if defaults:
            defaults = Just(defaults)
            hv = (hv[0] or defaults.h, hv[1] or defaults.v)
        self.h, self.v = hv
        if self.h not in '<|:>': raise ValueError(f"Invalid horizontal justification character '{self.h}'")
        if self.v not in '_-~^': raise ValueError(f"Invalid vertical justification character '{self.v}'")
        


    def pad_v(self, h):
        if self.v == '_': return h
        elif self.v == '-': return h//2
        elif self.v == '~': return ceil(h/2)
        return 0


    def pad_h(self, w):
        if self.h == '>': return w
        elif self.h == '|': return w//2
        elif self.h == ':': return ceil(w/2)
        return 0
        

    def __str__(self):
        return self.h+self.v


    def __repr__(self):
        return f'Just({self.h+self.v!r})'


    @staticmethod
    def lines(self, lines, num_lines, w, h, just):
        pad = h - num_lines
        if h==0 or pad==0: # Perfect fit
            yield from lines
            return
        elif pad < 0: # Too many lines
            vbar = '|' if self['ascii'] else '⋮'
            keep_top = ceil((h - 1)/2)
            hide = num_lines - h + 1
            e = Line(f"{vbar}{hide} lines{vbar}", style='dem', parent=self)
            if w and e.width > w: e = Line(style='dem', parent=self).insert(0, f"{vbar}{hide}")
            if w and e.width > w: e = Line(style='dem', parent=self).insert(0, f"{vbar}")
            line_iter = iter(lines)
            for _ in range(keep_top): yield next(line_iter)
            yield e.justify(w, '|')
            for _ in range(hide): next(line_iter)
            try:
                while True: yield next(line_iter)
            except StopIteration: pass
        else: # Too few lines
            padt = just.pad_v(pad)
            for _ in range(padt): yield Line(parent=self).insert(0, ' '*w)
            yield from lines
            for _ in range(pad-padt): yield Line(parent=self).insert(0, ' '*w)




class JustCVar(CVar):
    def canon(self, sval):
        return Just(sval)

    def merge(self, val, pval):
        return Just(val, pval)



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
Context.define(IntCVar('wrap_mark_from', 'wmf'))



class SMark():
    __props__ = ('style','s','e')

    def __init__(self,*args):
        self.style, self.s, self.e = args

    def __repr__(self):
        return f'{self.style}/{self.s}-{self.e}'

    def __eq__(self, other):
        return self.style == other.style and self.s == other.s and self.e == other.e



class Line(Rich, wrap=True):
    ''' A Line is a list of Lines and Spans.
    
    It is a Context so it can style the text.
    Only Lines and Spans can be appended (or inserted).
    Anything else will be converted with Span() first and then added.
    Any Lines appended or inserted into this string will become Context children.
    '''
    
    def __init__(self, *args, **kwargs):
        self.__spans = []
        super().__init__(*args, **kwargs)


    @property
    def spans(self):
        while self.rich_stream:
            el, ctx = self.rich_stream.pop(0)
            if el == '\n': el = '\\n'
            self.insert(-1, el, **ctx)
        return self.__spans


    def is_blank(self):
        for span in self.spans:
            if not span.is_blank(): return False
        return True
        

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
        return self


    def calc_width(self):
        return reduce(lambda a,x: x.width + a, self.spans, 0)
    

    def calc_height(self):
        return 1 if self.spans else 0


    def each_child(self):
        yield from self.spans


    def justify(self, w, justify='<'):
        ''' Add padding so that we are correctly justified for the given `width`
        '''
        if w == 0: return self
        if w < 0: raise ValueError(f"Can't justify to negative width: {w}")
        pad = w - self.width
        if pad == 0: return self
        if pad < 0:
            best = (-1,)
            for off in [0, 1, -1]:
                lhs = self.clone().trim(ceil((w-1)/2) + off)
                lhs_w = lhs.width
                rhs = self.clone().trim(-(w-lhs_w-1))
                rhs_w = rhs.width
                lr_w = lhs_w + rhs_w
                if lr_w >= w: continue
                hur = int(len(lhs) >= len(rhs)) + int(lr_w == w-1)*5
                if hur > best[0]: best = (hur, lr_w, lhs, rhs, lhs_w, rhs_w)
            else:
                _, lr_w, lhs, rhs, lhs_w, rhs_w = best
            inter = Line(parent=self, style='dem').insert(0, ('~' if self['ascii'] else '⋯')*(w-lr_w))
            self.__spans = lhs.spans + [inter] + rhs.spans
            self.changed_size()
            return self
        else: # Extra space
            padl = Just(justify, '<').pad_h(pad)
            return self.insert(0, ' '*padl).insert(-1, ' '*(pad-padl))



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
        self.changed_size()
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
        
        def _stack_append(style, s, e):         
            if not style: return   
            popped = []
            while tstk and tstk[-1].e <= s: popped.insert(0,tstk.pop()) # Pop old ones
            # Match as many parents as we can
            for same in range(len(style), -1, -1):
                if style[:same] == tuple(y.style for y in tstk[-same:]): break
            style = style[same:]
            # Extend popped styles
            i = 0
            for p, y in zip(popped, style[:]):
                if p.style != y: break
                if p.e != s: break
                i += 1
                p.e = e
                tstk.append(p)
                style = style[1:]
            for y in style:
                tstk.append(SMark(y, s, e))
                stack.append(tstk[-1])


        def _styled(part, s, parent, styles):
            if isinstance(part, Line) and (y:=part.ctx_local.get('style',None)):
                styles = style_cvar.merge(y, styles) if styles else y
            if isinstance(part, Span):
                _stack_append(styles, len(s), len(s)+len(part))
                s += str(part)
            else:
                for sub in part.spans: s = _styled(sub, s, part, styles)
            return s

        return _styled(self, '', self, self['style']), stack


    def changed_size(self):
        self.__len = None
        super().changed_size()



    def flatten(self, w=0, h=0, **kwargs):
        justify = self['justify']
        text_wrap = self['text_wrap']
        my_w = w if (w!=0 or Just(justify,'<').h == '<') else Line.calc_width(self)
        if h:
            if w==0 or not text_wrap: # known height
                lines = [self.clone(parent=self).justify(my_w, justify)]
                my_h = 1
            else: # We have an unknown height
                lines = list(self._flatten_wrap(my_w, justify))
                my_h = len(lines)
            yield from Just.lines(self, lines, my_h, my_w, h, Just(justify,'^'))
        else: # h == 0
            if text_wrap:
                yield from self._flatten_wrap(my_w, justify)
            else:
                yield self.clone(parent=self).justify(my_w, justify)


    def _flatten_wrap(self, w, justify):
        cur = self.clone(parent=self)
        if w==0 or w >= cur.width:
            yield cur.justify(w, justify)
            return
        wmf = max(self['wrap_mark_from'] or 4, 4)
        prefix = '' if w < wmf else '\\ ' if self['ascii'] else '⤷ '
        while True:
            lhs = cur.clone(parent=self).trim(w)
            cur.trim(-(cur.width - lhs.width))  
            yield lhs.insert(-1, ' '*(w-lhs.width))
            if not cur: break
            if prefix: cur.insert(0, Line(style='dem').insert(0,prefix))


    def __str__(self):
        return ''.join(map(str, self.spans))


    def __repr__(self):
        return f"Line({', '.join([repr(x) for x in self.spans])})"
        

    def __len__(self):
        if self.__len == None:
            self.__len = reduce(lambda a,x: len(x) + a, self.spans, 0)
        return self.__len
        
