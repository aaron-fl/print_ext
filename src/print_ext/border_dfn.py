from functools import reduce



class BorderDfn():
    ''' Define the border by single characters

    \n don't care
    corners      [c] : TL TR BL BR
    mask         [m] : T B L R
    top/bottom [t/b] : X | LXR | LMXR | LMXR1
    left/right [l/r] : X | TXB | LMXR | TMXB1

    '''
    special = {
        '\\':'╲', '/':'╱', 'X':'╳',
        '|2':'╎', '-2':'╌', '#|2':'╏', '#-2':'╍',
        '|3':'┆', '-3':'┄', '#|3':'┇', '#-3':'┅',
        '|4':'┊', '-4':'┈', '#|4':'┋', '#-4':'┉',
    }

    codes = {
        '   #':'╸', '   -':'╴', '  # ':'╻', '  ##':'┓', '  #-':'┒', '  - ':'╷', '  --':'┐', '  -=':'╕', '  =-':'╖',
        '  ==':'╗', '  ~~':'╮', ' #  ':'╺', ' # #':'━', ' # -':'╾', ' ## ':'┏', ' ###':'┳', ' ##-':'┲', ' #- ':'┍',
        ' #-#':'┯', ' #--':'┮', ' -  ':'╶', ' - -':'─', ' -# ':'┎', ' -##':'┱', ' -- ':'┌', ' --#':'┭', ' ---':'┬',
        ' -= ':'╓', ' -=-':'╥', ' = =':'═', ' =- ':'╒', ' =-=':'╤', ' == ':'╔', ' ===':'╦', ' ~~ ':'╭', '#   ':'╹',
        '#  #':'┛', '#  -':'┚', '# # ':'┃', '# ##':'┫', '# #-':'┨', '# - ':'╿', '# -#':'┩', '# --':'┦', '##  ':'┗',
        '## #':'┻', '## -':'┺', '### ':'┣', '####':'╋', '###-':'╊', '##- ':'┡', '##-#':'╇', '##--':'╄', '#-  ':'┖',
        '#- #':'┹', '#- -':'┸', '#-##':'╉', '#-#-':'╂', '#-- ':'┞', '#--#':'╃', '#---':'╀', '-   ':'╵', '-  #':'┙',
        '-  -':'┘', '-  =':'╛', '- # ':'╽', '- ##':'┪', '- #-':'┧', '- - ':'│', '- -#':'┥', '- --':'┤', '- -=':'╡',
        '-#  ':'┕', '-# #':'┷', '-# -':'┶', '-###':'╈', '-##-':'╆', '-#- ':'┝', '-#-#':'┿', '-#--':'┾', '--  ':'└',
        '-- #':'┵', '-- -':'┴', '--# ':'┟', '--##':'╅', '--#-':'╁', '--- ':'├', '---#':'┽', '----':'┼', '-=  ':'╘',
        '-= =':'╧', '-=- ':'╞', '-=-=':'╪', '=  -':'╜', '=  =':'╝', '= = ':'║', '= =-':'╢', '= ==':'╣', '=-  ':'╙',
        '=- -':'╨', '=-= ':'╟', '=-=-':'╫', '==  ':'╚', '== =':'╩', '=== ':'╠', '====':'╬', '~  ~':'╯', '~~  ':'╰',
    }

    codes_inv = dict(zip(codes.values(), codes.keys()))    
    fields = 'clrtbm'
    fld_size = dict(c=8,l=10,r=10,t=10,b=10,m=4)
    dfns = {}


    @staticmethod
    def ext(trbl):
        return ''.join(BorderDfn.codes_inv.get(c,'    ')[i] for i, c in enumerate(trbl))


    @staticmethod
    def join(code=None, t=' ', r=' ', b=' ', l=' '):
        code = code or t+r+b+l
        return BorderDfn.codes.get(code, BorderDfn.special.get(code, ' '))


    @staticmethod
    def define(name, *args, **kwargs):
        dfn = BorderDfn(*args, **kwargs)
        if name in BorderDfn.dfns and BorderDfn.dfns[name] != dfn:
            raise ValueError(f"Redefining BorderDfn {name!r}:\nExisting: {BorderDfn.dfns[name]}\nTrying to set: {dfn}")
        BorderDfn.dfns[name] = dfn


    @staticmethod
    def _to_bdr(v):
        if isinstance(v, BorderDfn): return v.clone()
        v = str(v).lower().split(':',1)#'.',1)
        if len(v) == 1:
            v = v[0].split('.',1)
            if v[0] not in BorderDfn.dfns: raise ValueError(f"{v[0]!r} is not a defined BorderDfn")
            bdr = BorderDfn.dfns[v[0]]
            try:
                return bdr if len(v) == 1 else BorderDfn(**{k:bdr[k] for k in v[1]})
            except KeyError:
                raise ValueError(f"Illegal selector {v[1]!r} in {'.'.join(v)!r}") 
        else:
            return BorderDfn(**{v[0]:v[1]})


    def __init__(self, *vals, **kwargs):
        self._sides = None
        if vals:
            base = reduce(lambda a,b: a.update(b), [BorderDfn._to_bdr(b) for b in vals])
        else:
            base = {k:'\n' for k in BorderDfn.fields}
        for k in BorderDfn.fields:
            self[k] = str(kwargs.get(k, base[k]))


    def __getitem__(self, k):
        try:
            return getattr(self, k)
        except AttributeError:
            return '\n'*BorderDfn.fld_size[k]


    def __setitem__(self, k, v):
        if len(v) == 1: v = v*BorderDfn.fld_size.get(k,2)
        if k == 'tl': k,v = 'c', v[0]+'\n\n\n'+v[1]+'\n\n\n'
        elif k == 'tr': k,v = 'c', '\n'+v[0]+'\n\n\n'+v[1]+'\n\n'
        elif k == 'bl': k,v = 'c', '\n\n'+v[0]+'\n'+v[1]+'\n'
        elif k == 'br': k,v = 'c', '\n\n\n'+v[0]+'\n\n\n'+v[1]
        if len(v) == 2: v = v[0]*(BorderDfn.fld_size[k]//2) + v[1]*(BorderDfn.fld_size[k]//2)
        if len(v) * 2 == BorderDfn.fld_size[k]: v = v+v
        if k == 'm':
            if not all(c in '01\n' for c in v): raise ValueError(f"Invalid mask value: {k}={v!r}")
        elif k in 'trbl':
            if len(v) == 6: v = v[:2] + v[1:3] + v[1] + v[3:5] + v[4:6] + v[4]
            elif len(v) == 8: v = v[:4] + v[1] + v[4:] + v[5]
        if len(v) != BorderDfn.fld_size[k]: raise ValueError(f"Invalid BorderDfn: {k}={v!r}")
        setattr(self, k, ''.join(o if n=='\n' else n for o,n in zip(self[k], v)))


    def clone(self):
        return BorderDfn(**{k:self[k] for k in BorderDfn.fields})


    def vals(self):
        return tuple(self[k] for k in BorderDfn.fields)


    def update(self, newer):
        out = self.clone()
        for k in BorderDfn.fields:
            out[k] = newer[k]
        return out


    def __eq__(self, other):
        return self.vals() == (other and other.vals())


    def __hash__(self):
        return hash(self.vals())


    def __repr__(self):
        _m = lambda v: f'{v[0]!r}*{len(v)}' if v[0]*len(v) == v else repr(v)
        args = [f'{k}={_m(self[k])}' for k in BorderDfn.fields]
        return f"BorderDfn({','.join(args)})"


    @property
    def sides(self):
        if not self._sides:
            self._sides = [c=='1' for c in self.m]
        return self._sides
    

    @property
    def width(self):
        _, _, l, r = self.sides
        return int(l) + int(r)


    @property
    def height(self):
        t, b, _, _ = self.sides
        return int(t) + int(b)


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



BorderDfn.define('false', m='0')
BorderDfn.define('1', m='1')
BorderDfn.define(' ', c=' ', t=' ', b=' ', l=' ', r=' ')
BorderDfn.define('-', c='┌┐└┘++++', t='─-', b='─-', l='│|', r='│|')
BorderDfn.define('=', c='╔╗╚╝####', t='═=', b='═=', l='║#', r='║#')
BorderDfn.define('[', t='┌──┐⎴-----', b='└──┘⎵-----', l='⎡⎢⎢⎣[[[[[[', r='⎤⎥⎥⎦]]]]]]')
BorderDfn.define('(', t='╭──╮⏜/--\\-', b='╰──╯⏝\\--/-', l='⎛⎜⎜⎝(/||\\(', r='⎞⎟⎟⎠)\\||/)')
BorderDfn.define('{', t='╭┴─╮⏞/`-\\*', b='╰┬─╯⏟\\,-/*', l='⎧⎨⎪⎩{/{|\\{', r='⎫⎬⎪⎭}\\}|/}')
BorderDfn.define('box', '1', '-')
