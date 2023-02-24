from .borders import Borders, BorderDfn
from .context import Context
from .line import Line

class HR(Borders):

    default_bdr = BorderDfn(m='01', l='│││┤┤[[[[[', r='│││├├]]]]]', t='─-')

    ctx_defaults = Context.defaults(border=default_bdr)
    
    @property
    def width(self):
        return self['width_max'] or (super().width + 4)


    def flatten(self, w=0, h=0, **kwargs):
        mw = w or self['width_max'] or (super().width + 4)
        mh = h or self.height
        style = self['border_style']
        side = self['border'].t[7 if self['ascii'] else 2]
        for i,l in enumerate(super().flatten(h=h,**kwargs)):
            pad = side if i == mh-1 else ' '
            rhs = (mw-l.width)//2
            lhs = pad*(mw-l.width-rhs)
            rhs = pad*rhs
            print(f"I:{i} _{l}_ {mw-l.width} {lhs!r} {rhs!r}")
            yield l if not (lhs or rhs) else Line(parent=self)(lhs,style=style)(l)(rhs,style=style)



