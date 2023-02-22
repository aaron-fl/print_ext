import re
from math import ceil
from functools import reduce
from .flex import Flex
from .context import Context, CtxProxy, CVar
from .text import Text
from .size import Size
from tests.testutil import debug_dump
Context.define(CVar('cls'))

class CellRange():
    RE = re.compile(r'(R(-?\d+)?(%(\d+))?)?(C(-?\d+)?(%(\d+))?)?$')

    def __init__(self, cstr, **kwargs):
        self.kwargs = kwargs
        m = CellRange.RE.match(cstr)
        if not m: raise ValueError(f"Invalid Cell Range {cstr!r}")
        self.r, self.rmod = (int(m[2] or 0), int(m[4]) if m[3] else 0) if m[1] else (0, 1)
        self.c, self.cmod = (int(m[6] or 0), int(m[8]) if m[7] else 0) if m[5] else (0, 1)

    
    def ctx_merge(self, ctx, r, c, n_rows, n_cols):
        if not self.matches(r, c, n_rows, n_cols): return ctx
        return Context(parent=ctx, **self.kwargs)


    def matches(self, r, c, n_rows, n_cols):
        r_off = self.r % n_rows
        c_off = self.c % n_cols

        if self.rmod:
            if (r < r_off) or (r-r_off)%self.rmod: return False
        elif r_off != r: return False

        if self.cmod:
            if (c < c_off) or (c-c_off)%self.cmod: return False
        elif c_off != c: return False

        return True

    
    def is_open_ended(self):
        return self.r >= 0


    def __repr__(self):
        return f'R{self.r}%{self.rmod}C{self.c}%{self.cmod}'



class ColDfn():
    ''' You can define the 
    '''
    def __init__(self, val):
        if isinstance(val, float):
            val = dict(rate=val)
        elif isinstance(val, int):
            if val < 0: val = dict(rate=0, min=-val, max=-val)
            else: val = dict(rate=1.0, min=val)
        self.val = val

    def __getitem__(self, key):
        return self.val.get(key, None)



class Table(Flex):
    def __init__(self, *args, **kwargs):
        self.cols = [ColDfn(a) for a in args]
        self._cell_ctx = []
        super().__init__(**kwargs)


    def __bool__(self):
        return bool(self.__len__())


    def __len__(self):
        return len(self.cells)


    @property
    def cells(self):
        while self.rich_stream:
            elctx = self.rich_stream.pop(0)
            if elctx[0] == '\t':
                self._cells.append([])
            else:
                self._cells[-1].append(elctx)
        return self._cells[:-1] if self._cells[-1] == [] else self._cells


    def is_open_ended(self):
        return all(c.is_open_ended() for c in self._cell_ctx)


    def _cell_ctx_reduce(self, r, c, n_rows, n_cols):
        return reduce(lambda a,b: b.ctx_merge(a, r, c, n_rows, n_cols), self._cell_ctx, Context())


    def _cell_instance(self, cell, ctx):
        if cls:=ctx['cls']:
            el = cls(parent=self, **ctx.ctx_flatten())
            if cell: el.rich_newline(cell[0][1]) if cell[0][0]==None else el.rich_append(*cell[0])
        elif cell and isinstance(cell[0][0], Context):
            kwargs = ctx.ctx_flatten()
            kwargs.update(cell[0][1])
            kwargs.update(cell[0][0].ctx_local)
            el = cell[0][0].clone(parent=self, **kwargs)
        else:
            el = Text(parent=self, **ctx.ctx_flatten())
            if cell: el.rich_newline(cell[0][1]) if cell[0][0]==None else el.rich_append(*cell[0])
        for args in cell[1:]:
            el.rich_newline(args[1]) if args[0]==None else el.rich_append(*args)
        return el


    def flatten(self, w=0, h=0, **kwargs):
        n_cols = len(self.cols)
        cells = self.cells
        n_rows = ceil(len(cells)/n_cols)
        noms = [0]*n_cols
        els = []
        # Instanciate each el and calculate maximum nominal widths
        for i, cell in enumerate(cells):
            c = i%n_cols
            ctx = self._cell_ctx_reduce(i//n_cols, c, n_rows, n_cols)
            els.append(self._cell_instance(cell, ctx))
            if noms[c] < (nom:=els[-1]['width_nom']): noms[c] = nom
        # Calculate sizes
        sizes = [Size(nom=noms[i], min=self.cols[i]['min'], max=self.cols[i]['max'], rate=self.cols[i]['rate']) for i in range(n_cols)]
        if len(sizes) != n_cols: raise NotImplementedError()
        print(f" FLatten {len(cells)} else into table {n_rows}x{n_cols} => {sizes} ")
        def elide_cols(ecells):
            return Size(nom=1, rate=0, user=ecells)
        cols = Size.resize(sizes, w, wrap=False, elide=elide_cols)[0]
        # Flatten
        row_els = []
        for i, e in enumerate(els):
            row_els.append(e)
            if len(row_els) == n_cols or i == len(cells)-1:
                if h:
                    raise NotImplementedError()
                else:
                    for e,c in zip(row_els + [Text(parent=self)]*(len(cols)-len(row_els)), cols): c.user = e
                    yield from self._flatten_width_row(cols, w, 0)
                row_els = []


    def cell(self, rstr, **kwargs):
        self._cell_ctx.append(CellRange(rstr, **kwargs))

    