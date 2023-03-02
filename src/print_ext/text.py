
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
            if el == '\v':
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


    def flatten(self, w=0, h=0, **kwargs):
        rows = []
        for line in self.lines:
            rows += list(line.flatten(w=w))
        maxw = rows[0].width if len(rows) == 1 else max(*[r.width for r in rows]) if rows and w == 0 else w
        for row in rows: row.justify(maxw)
        yield from justify_v(rows, h, Just(self['justify'],'^'), Line(parent=self).insert(0, ' '*maxw))


    def each_child(self):
        yield from self.lines


    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s.__lines = [x.clone(parent=s, **x.ctx_local) for x in self.lines]
        return s
    

    def __str__(self):
        return '\\v'.join(map(str, self.lines))


    def __repr__(self):
        return self.__class__.__name__+f'({str(self)})'
