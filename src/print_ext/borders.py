from .rich import Rich
from .text import Text
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



class Bdr(Text, border=(1,'-'), border_style='dem'):

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

    alias = {
        '╰':'└', '╮':'┐',  '╯':'┘', '╭':'┌',
        '╎':'⎢', '┆':'⎢', '┊':'⎢', '╏':'┃', '┇':'┃', '┋':'┃',
        '╌':'─', '┄':'─', '┈':'─', '╍':'━', '┅':'━', '┉':'━',
    }

    codes_inv = dict(zip(codes.values(), codes.keys()))   


    @staticmethod
    def ext(trbl):
        ''' Extend the top,right,bottom,left unicode border characters, return the 4-code for the center.
        '''
        return ''.join(Bdr.codes_inv.get(Bdr.alias.get(c,c), '    ')[i] for i, c in enumerate(trbl))


    @staticmethod
    def join(code=None, t=' ', r=' ', b=' ', l=' '):
        ''' Convert 4-code (trbl) to a unicode border character.
        ''' 
        code = code or t+r+b+l
        return Bdr.codes.get(code, Bdr.special.get(code, ' '))


    @staticmethod
    def dfn(*args, **kwargs):
        return BorderDfn(*args, **kwargs)


    def calc_width(self):
        bdr = self['border']
        return super().calc_width() + (bdr.width if bdr else 0)

    
    def calc_height(self):
        bdr = self['border']
        return super().calc_height() + (bdr.height if bdr else 0)


    def flatten(self, w=0, h=0, **kwargs):
        bdr = self['border']
        bdrw = w==0 or w >= bdr.width + 1
        bdrh = h==0 or h >= bdr.height + 1
        bw = int(bdrw and bdr.width)
        bh = int(bdrh and bdr.height)
        child_size = (w and w-bw), (h and h-bh)
        flat = list(super().flatten(w=child_size[0] or super().calc_width(), h=child_size[1], **kwargs))# if self.child else []
        ascii = self['ascii']
        style = self['border_style']
        lhs = bdr.side_chars(len(flat), bdr.l[5:] if ascii else bdr.l) if bdr.sides[2] else ''
        rhs = bdr.side_chars(len(flat), bdr.r[5:] if ascii else bdr.r) if bdr.sides[3] else ''
        wb = w or (flat[0].width if flat else 0) + int(bdr.sides[2]) + int(bdr.sides[3])
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
