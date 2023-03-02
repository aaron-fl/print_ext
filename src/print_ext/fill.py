from print_ext.context import Context
from print_ext.line import Line
from print_ext.span import Span
from print_ext.text import Text
import print_ext.flex

class Fill(Text, width_min=0, height_min=0):
    ''' Fills the given block of space (when flattened) with a simple repeating pattern.

    :Examples:

        >>> [str(l) for l in Fill().flatten(2,2)]
        ['  ', '  ']
        >>> [str(l) for l in Fill('abc').flatten(5,2)]
        ['abcab', 'abcab']
        >>> [str(l) for l in Fill('a\v','b').flatten(3,3)]
        ['aaa', 'bbb', 'aaa']
    
    more
    '''

    def calc_width(self):
        return 0


    def calc_height(self):
        return 0


    def flatten(self, w=0, h=0, **kwargs):
        rows = [x.clone(parent=self, **x.ctx_local) for x in self.lines]
        if not rows: rows = [Line(' ', parent=self)]
        if not w: w = rows[0].width if len(rows) == 1 else max(*[r.width for r in rows])
        for ri, line in enumerate(rows):
            if h and ri == h: break # slight optimization?
            if not line: line.insert(0, ' '*w)
            while line.width < w:
                line.insert(-1, line.clone(parent=line.parent, **line.ctx_local))
            line.trim(w).insert(-1, ' '*(w-line.width))
        for i in range(h or len(rows)):
            yield rows[i%len(rows)]
