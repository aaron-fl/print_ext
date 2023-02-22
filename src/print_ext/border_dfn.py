
class BorderDfn():
    ''' Define the border by single characters

    \n don't care
    corners      [c] : TL TR BL BR
    mask         [m] : T B L R
    top/bottom [t/b] : X | LXR | LMXR | LMXR1
    left/right [l/r] : X | TXB | LMXR | TMXB1

    '''

    @staticmethod
    def canon(**kwargs):
        kwargs['c'] = str(kwargs.get('c', '\n'*8))
        kwargs['m'] = str(kwargs.get('m', '\n'*4))
        for k in 'tblr':
            v = str(kwargs.get(k, '\n'*10))
            if len(v) == 1: v = v*10
            elif len(v) == 2: v = v[0]*5 + v[1]*5
            elif len(v) == 6: v = v[:2] + v[1:3] + v[1] + v[3:5] + v[4:6] + v[4]
            elif len(v) == 8: v = v[:4] + v[1] + v[4:] + v[5]
            elif len(v) == 10: pass
            else: raise ValueError(f"Invalid BorderDfn string: {k}={v!r}")
            kwargs[k] = v
        if len(kwargs['c']) != 8: raise ValueError(f"Invalid BorderDfn string: c={v!r}")
        if len(kwargs['m']) != 4: raise ValueError(f"Invalid BorderDfn string: m={v!r}")
        return kwargs


    def __init__(self, val=None, **kwargs):
        self._sides = None
        if val == None:
            vals = BorderDfn.canon()
        elif isinstance(val, BorderDfn):
            vals = {k:getattr(val,k) for k in 'cmtblr'}
        elif val == 'blank':
            vals = BorderDfn.canon(c=' '*8, t=' ', b=' ', l=' ', r=' ')
        elif val == 'box':
            vals = BorderDfn.canon(c='┌┐└┘++++', t='─-', b='─-', l='│|', r='│|')
        elif val == 'dbox':
            vals = BorderDfn.canon(c='╔╗╚╝####', t='═=', b='═=', l='║#', r='║#')
        elif val == 'bracket':
            vals = BorderDfn.canon(c=' '*8, t='┌──┐⎴-----', b='└──┘⎵-----', l='⎡⎢⎢⎣[[[[[[', r='⎤⎥⎥⎦]]]]]]')
        elif val == 'paren':
            vals = BorderDfn.canon(c=' '*8, t='╭──╮⏜/--\\-', b='╰──╯⏝\\--/-', l='⎛⎜⎜⎝(/||\\(', r='⎞⎟⎟⎠)\\||/)')
        elif val == 'brace':
            vals = BorderDfn.canon(c=' '*8, t='╭┴─╮⏞/`-\\*', b='╰┬─╯⏟\\,-/*', l='⎧⎨⎪⎩{/{|\\{', r='⎫⎬⎪⎭}\\}|/}')
        elif len(str(val)) == 1:
            val = str(val)
            vals = BorderDfn.canon(c=val*8, t=val*10, b=val*10, l=val*10, r=val*10)
        else:
            raise ValueError(f"Invalid border value {val!r}")
        vals.update({k:v for k,v in BorderDfn.canon(**kwargs).items() if k in kwargs})
        for k, v in vals.items(): setattr(self, k, v)


    def __repr__(self):
        _m = lambda v: f'{v[0]!r}*{len(v)}' if v[0]*len(v) == v else repr(v)
        args = [f'{k}={_m(getattr(self,k))}' for k in 'clrtbm']
        return f"BorderDfn({','.join(args)})"


    @property
    def sides(self):
        if not self._sides:
            self._sides = [c not in 'Xx ' for c in self.m.replace('\n','1')]
        return self._sides
    

    @property
    def width(self):
        _, _, l, r = self.sides
        return int(l) + int(r)


    @property
    def height(self):
        t, b, _, _ = self.sides
        return int(t) + int(b)


    def merge_from(self, older):
        out = BorderDfn()
        for k in 'clrbtm':
            pairs = zip(getattr(older,k), getattr(self, k))
            setattr(out, k, ''.join(o if n=='\n' else n for o,n in pairs))
        return out

    
    def _line(self, w, ascii, top):
        if not self.sides[0 if top else 1]: return None
        c = self.c[4:] if ascii else self.c
        cl, w = (c[0 if top else 2], w-1) if self.sides[2] else ('', w)
        cr, w = (c[1 if top else 3], w-1) if self.sides[3] else ('', w)
        chars = self.t if top else self.b
        return (cl + self.side_chars(w, chars[5:] if ascii else chars) + cr).replace('\n',' ')


    def top_line(self, w, ascii):
        return self._line(w, ascii, top=True)


    def bottom_line(self, w, ascii):
        return self._line(w, ascii, top=False)


    def side_chars(self, w, chars):
        if not w: return ''
        mid = w//2 + 1
        txt, w = (chars[4], w-1) if w == 1 else (chars[0], w-1)
        while w:
            if w == 1: txt += chars[3]
            elif w == mid: txt += chars[1]
            else: txt += chars[2]
            w -= 1
        return txt
