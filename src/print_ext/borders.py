from .rich import Rich
from .flex import Flex
from .line import Line, StyleCVar
from .context import Context, CVar
from .border_dfn import BorderDfn


class BorderCVar(CVar):
    def canon(self, val):
        if isinstance(val, tuple): return BorderDfn(*val)
        if isinstance(val, dict): return BorderDfn(**val)
        return BorderDfn(val)

    def merge(self, val, pval):
        return pval.update(val)


Context.define(StyleCVar('border_style'))
Context.define(BorderCVar('border'))



class Borders(Flex, border=(1,'-'), border_style='dem'):

    def calc_width(self):
        bdr = self['border']
        return super().calc_width(Flex) + (bdr.width if bdr else 0)

    
    def calc_height(self):
        bdr = self['border']
        return super().calc_height(Flex) + (bdr.height if bdr else 0)


    def flatten(self, w=0, h=0, **kwargs):
        bdr = self['border']
        bdrw = w==0 or w >= bdr.width + 1
        bdrh = h==0 or h >= bdr.height + 1
        bw = int(bdrw and bdr.width)
        bh = int(bdrh and bdr.height)
        child_size = (w and w-bw), (h and h-bh)
        flat = super().flatten(w=child_size[0], h=child_size[1], **kwargs)# if self.child else []
        ascii = self['ascii']
        style = self['border_style']
        lhs = bdr.side_chars(len(flat), bdr.l[5:] if ascii else bdr.l) if bdr.sides[2] else ''
        rhs = bdr.side_chars(len(flat), bdr.r[5:] if ascii else bdr.r) if bdr.sides[3] else ''
        wb = w or (flat[0].width if flat else 0) + int(bdr.sides[2]) + int(bdr.sides[3])
        #print(f'borders flatten {w}x{h}  bdwh:{bw}x{bh}  {child_size}  ->  bw:{wb} {lhs!r} {rhs!r}')
        if bdrh and (txt:=bdr.top_line(wb, ascii)):
            yield Line(parent=self, style=style).insert(0, txt)
        if not lhs and not rhs:
            yield from flat
        else:
            for i, f in enumerate(flat):
                l = Line(parent=self)
                if lhs: l(lhs[i], style=style)
                l(f)
                if rhs: l(rhs[i], style=style)
                yield l
        if bdrh and (txt:=bdr.bottom_line(wb, ascii)):
            yield Line(parent=self, style=style).insert(0, txt)
