from functools import reduce
from ..context import Context, IntCVar
from ..printer_util import Tag, Rewinder

Context.define(IntCVar('keep_lines'))


class MemoryRewinder(Rewinder):
    def __init__(self, printer):
        super().__init__(printer)
        self.pos = self.printer.overflowed + len(self.printer.widgets)
    

    def __call__(self):
        cur = self.printer.overflowed + len(self.printer.widgets)
        self.printer.truncate_tail(cur - self.pos)



class Memory(Context, keep_lines=1024):
    ''' Save widgets/tags to an in-memory buffer `widgets`.
    '''
    Rewinder = MemoryRewinder

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widgets = []
        self.__height = 0
        self.overflowed = 0


    def calc_height(self):
        return self.__height


    def calc_width(self):
        return reduce(lambda a, w: max(a, w[0].width), self.widgets, 0)


    def truncate_tail(self, n):
        if not n: return
        if n > len(self.widgets):
            n -= len(self.widgets)
            self.widgets = []
            self.__height = 0
            self.overflowed -= n
        else:
            self.__height -= reduce(lambda a, w: a+w[2], self.widgets[-n:], 0)
            self.widgets[-n:] = []
            

    def append(self, widget, tag):
        keep_lines = self['keep_lines']
        h = widget.height
        while self.__height and h + self.__height > keep_lines:
            _, _, l = self.widgets.pop(0)
            self.__height -= l
            self.overflowed += 1
        self.__height += h
        self.widgets.append((widget, tag, h))
        super().append(widget, tag)


    def clone(self, **kwargs):
        s = super().clone(**kwargs)
        s.overflowed = self.overflowed
        s.widgets = [(w.clone(parent=s, **w.ctx_local), Tag(tag), h) for w,tag,h in self.widgets]
        s.__height = reduce(lambda a, w: a+w[2], s.widgets, 0)
        return s
