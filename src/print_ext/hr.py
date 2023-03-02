from .borders import Borders, BorderDfn
from .context import Context
from .flex import Flex
from .line import Line, Just, justify_v

class HR(Flex, border=BorderDfn(l='\n\n│\n┤\n\n[\n[', r='\n\n│\n├\n\n]\n]', t='─-')):

    def calc_width(self):
        w = self['width_max']
        if not w:
            w = super().calc_width(Flex) + 6
            if w == 6: return 3
        return w


    def _flatten_empty(self, w, h, ascii, bdr, style):
        w = w or self['width_max'] or 3
        bar = bdr.t[7 if ascii else 2]
        bar_l = bdr.t[5 if ascii else 0]
        bar_r = bdr.t[8 if ascii else 3]
        line = bar if w==1 else (bar_l+bar_r) if w==2 else (bar_l + bar*(w-2) + bar_r)
        yield from justify_v([Line(parent=self)(line,style=style)], h, Just(self['justify'], '~'), Line(parent=self).insert(0,' '*w))
        

    def flatten(self, w=0, h=0, **kwargs):
        flat = list(super().flatten(w=0, h=h, **kwargs))
        ascii, bdr, style = self['ascii'], self['border'], self['border_style']
        #print(f"HR flat {self['width_max']} {flat}")
        if not any(flat):
            yield from self._flatten_empty(w,h, ascii, bdr, style)
            return
        mw = w or self['width_max']
        if mw and mw < 7:
            yield from super().flatten(w=mw, h=h, **kwargs)
            return
        mw = mw or (flat[0].width + 6)
        #print(f"   mw {mw}  {mw-6} < {flat[0].width}")
        if mw-6 < flat[0].width:
            flat = list(super().flatten(w=mw-6, h=h, **kwargs))
        innerw = flat[0].width
        just = Just(self['just'],'|~')
        hrv = just.pad_v(len(flat)-1)
        bar = bdr.t[7 if ascii else 2]
        bar_l = bdr.t[5 if ascii else 0]
        bar_r = bdr.t[8 if ascii else 3]
        join_l = bdr.l[9 if ascii else 4]
        box_l = bdr.l[7 if ascii else 2]
        join_r = bdr.r[9 if ascii else 4]
        box_r = bdr.r[7 if ascii else 2]
        left = just.pad_h(mw-innerw) or 3
        if left == mw-innerw: left = mw-innerw-3
        #print(f"JUST  {just}  bdr: {style} {bdr}  {left}/{innerw}/{mw}  h:{len(flat)}")
        for i,l in enumerate(flat):
            if i == hrv:
                lhs = bar_l + bar*(left-3) + join_l + ' '
                rhs = ' ' + join_r + bar*(mw-innerw-left-3) + bar_r
            else:
                lhs = ' '*(left-2) + box_l + ' '
                rhs = ' ' + box_r + ' '*(mw-innerw-left-2)
            yield Line(parent=self)(lhs,style=style)(l)(rhs,style=style)

