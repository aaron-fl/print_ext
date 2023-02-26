from .borders import Borders, BorderDfn
from .context import Context
from .flex import Flex
from .line import Line, Just

class HR(Flex, border=BorderDfn(l='\n┤│\n\n\n[[\n\n', r='\n├│\n\n\n]]\n\n', t='─-')):

    def calc_width(self):
        return self['width_max'] or (super().calc_width(Flex) + 6)


    def flatten(self, w=0, h=0, **kwargs):
        flat = list(super().flatten(w=0, h=h, **kwargs))
        if not flat: return []
        print(f"---------- {w} {flat[0].width}")
        if w and w <= 6:
            yield from super().flatten(w=w, h=h, **kwargs)
            return
        mw = w or self['width_max'] or (flat[0].width + 6)
        if mw-6 < flat[0].width:
            flat = list(super().flatten(w=mw-6, h=h, **kwargs))
        innerw = flat[0].width
        ascii, bdr, style = self['ascii'], self['border'], self['border_style']
        just = Just(self['just'],'|~')
        hrv = just.pad_v(len(flat)-1)
        bar = bdr.t[7 if ascii else 2]
        bar_l = bdr.t[5 if ascii else 0]
        bar_r = bdr.t[8 if ascii else 3]
        join_l = bdr.l[6 if ascii else 1]
        box_l = bdr.l[7 if ascii else 2]
        join_r = bdr.r[6 if ascii else 1]
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

