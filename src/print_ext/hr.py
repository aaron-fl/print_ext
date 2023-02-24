from .borders import Borders, BorderDfn
from .context import Context
from .flex import Flex
from .line import Line, Just

class HR(Flex):

    default_bdr = BorderDfn(l='\n┤│\n\n\n[[\n\n', r='\n├│\n\n\n]]\n\n', t='─-')

    ctx_defaults = Context.defaults(border=default_bdr)
    
    @property
    def width(self):
        return self['width_max'] or (super().width + 6)


    def flatten(self, w=0, h=0, **kwargs):
        nom = super().width
        mw = w or self['width_max'] or (nom + 6)
        innerw = min(mw-6, nom)
        if innerw <= 0:
            yield from super().flatten(w=mw, h=h, **kwargs)
            return
        flat = list(super().flatten(w=innerw, h=h, **kwargs))
        if not flat: return []
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

