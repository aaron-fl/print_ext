from functools import reduce
from .rich import Rich
from .line import Line, Just, justify_v
from .span import Span


class Text(Rich):
    ''' This is a list of Lines
    '''
    def __init__(self, *args, **kwargs):
        self.__lines = []
        super().__init__(*args, **kwargs)


    @property
    def lines(self):
        if not self.rich_stream: return self.__lines
        self.__lines.append([self.__lines.pop()] if self.__lines else [])
        while self.rich_stream:
            el, ctx = self.rich_stream.pop(0)
            if el == '\n':
                self.__lines.append([])
                continue
            if isinstance(el, Line):
                lines = [Line(**ctx).insert(0,el)] if ctx else [el]
            else:
                lines = list(el.flatten()) if hasattr(el, 'flatten') else [Line().insert(0,el)]
                if ctx:
                    for l in lines: l.ctx(**ctx)
            if not lines: continue
            self.__lines[-1].append(lines[0])
            for line in lines[1:]:
                self.__lines.append([line])
        # Turn arrays of lines into a single Line object
        for i, line in enumerate(reversed(self.__lines)):
            if isinstance(line, Line): break
            self.__lines[-1-i] = line[0].ctx_parent(self) if len(line) == 1 else Line(*line, parent=self)
        return self.__lines


    def calc_width(self):
        return max(0,0,*map(lambda l: l.width, self.lines))
    

    def calc_height(self):
        return reduce(lambda a,_: a+1, self.lines, 0)


    def flatten(self, w=0, h=0, **kwargs):
        if not w and Just(self['justify'],'<').h != '<':
            w = Text.calc_width(self) # We need to be able to right/center justify to our natural width
        if h and h != Text.calc_height(self):
            yield from self.flatten_with_h(w=w,h=h,**kwargs)
        else:
            for line in self.lines:
                yield from line.flatten(w=w)  


    def flatten_with_h(self, *, w, h, **kwargs):
        rows = []
        for line in self.lines:
            rows += list(line.flatten(w=w))
        yield from justify_v(rows, h, Just(self['justify'],'^'), Line(parent=self).insert(0, ' '*w))


    def each_child(self):
        yield from self.lines


    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s.__lines = [x.clone(parent=s, **x.ctx_local) for x in self.lines]
        return s
    

    def __str__(self):
        return '\\n'.join(map(str, self.lines))


    def __repr__(self):
        return self.__class__.__name__+f'({str(self)})'
