from functools import reduce
from ..widget import Widget
from ..line import Just
from .printer_abc import Printer


class WidgetPrinter(Widget, Printer):
    ''' A Printer that is Flatten-able
    '''
         
    def calc_width(self):
        return reduce(lambda a, w: max(a, w[0].width), self._widgets, 0)


    def calc_height(self):
        return reduce(lambda a, w: a+w[0].height, self._widgets, 0)
        

    def flatten(self, w=0, h=0, **kwargs):
        justify = self['justify']
        my_w = w if (w!=0 or Just(justify,'<').h == '<') else WidgetPrinter.calc_width(self)
        if h:
            lines = reduce(lambda a, w: a + list(w[0].flatten(w=my_w)), self._widgets, [])
            yield from Just.lines(self, lines, len(lines), my_w, h, Just(justify,'^'))
        else: # h == 0
            for w in self._widgets:
                yield from w[0].flatten(w=my_w)    

