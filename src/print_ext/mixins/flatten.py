from functools import reduce
from ..widget import Widget, INFINITY
from ..line import Just
from .memory import Memory


class Flatten(Memory, Widget):
    ''' We are a Widget, so we can flatten the `widgets`.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def flatten(self, w=0, h=0, **kwargs):
        justify = self['justify']
        my_w = w if (w!=0 or Just(justify,'<').h == '<') else self.width
        if h:
            lines = reduce(lambda a, w: a + list(w[0].flatten(w=my_w)), self.widgets, [])
            yield from Just.lines(self, lines, len(lines), my_w, h, Just(justify,'^'))
        else: # h == 0
            for w in self.widgets:
                yield from w[0].flatten(w=my_w)
