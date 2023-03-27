from .flatten import Flatten
from ..line import Just


class Tail(Flatten):
    ''' Just shows the tail portion when flattened to a fixed height
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def flatten(self, w=0, h=0, **kwargs):
        if h == 0:
            yield from super().flatten(w, h, **kwargs)
            return
        justify = self['justify']
        my_w = w if (w!=0 or Just(justify,'<').h == '<') else self.width
        tail, tail_len = [], 0
        for widget, _, _ in reversed(self.widgets):
            lines = list(widget.flatten(w=my_w, **kwargs))
            tail[:0] = lines[-(h-tail_len):]
            tail_len = len(tail)
            if tail_len == h: break
        yield from tail
