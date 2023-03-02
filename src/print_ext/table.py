import re
from math import ceil
from functools import reduce
from .flex import Flex
from .line import StyleCVar
from .context import Context, CVar
from .text import Text
from .size import Size
from .borders import Borders, BorderDfn


Context.define(CVar('cls'))
Context.define(CVar('tmpl'))


class CellDfn():
    RE = re.compile(r'(r(-?\d+)?(%(\d+))?)?(c(-?\d+)?(%(\d+))?)?$')

    def __init__(self, cstr, **kwargs):
        self.kwargs = kwargs
        cstr = cstr.lower()
        if cstr == 'all': m = (None, True, 0, True, 1, True, 0, True, 1)
        else: m = CellDfn.RE.match(cstr)
        if not m: raise ValueError(f"Invalid Cell Range {cstr!r}")
        self.r, self.rmod = (int(m[2] or 0), int(m[4]) if m[3] else 0) if m[1] else (0, 1)
        self.c, self.cmod = (int(m[6] or 0), int(m[8]) if m[7] else 0) if m[5] else (0, 1)


    def __hash__(self):
        return hash(self.vals())


    def __eq__(self, other):
        return self.vals() == (other and other.vals())


    def vals(self):
        v = self.r, self.rmod, self.c, self.cmod
        return  v + tuple((k,self.kwargs[k]) for k in sorted(self.kwargs))
    
    
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
        return f'R{self.r}%{self.rmod}C{self.c}%{self.cmod} {self.kwargs}'



class Table(Flex, tmpl='pad,em'):    
    _tmpls = {}

    @staticmethod
    def define_tmpl(style, *cells):
        if style in Table._tmpls and cells != Table._tmpls[style]:
            raise ValueError(f"Table style {style!r} is already defined:\nExisting: {Table._tmpls[style]}\nTrying to set: {cells}")
        Table._tmpls[style] = cells


    def __init__(self, *args, **kwargs):
        self.cols = [Size(easy=a) for a in args]
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



    def calc_width(self):
        n_cols = len(self.cols)
        cells = self.cells
        n_rows = ceil(len(cells)/n_cols)
        els = self._cell_instances(n_rows, n_cols)
        # Calculate max col widths
        noms = [0]*n_cols
        for i, el in enumerate(els):
            c = i%n_cols
            if noms[c] < (nom:=el['width_nom']): noms[c] = nom
        sizes = [col.clone(nom=noms[i]) for i,col in enumerate(self.cols)]
        if len(sizes) != n_cols: raise NotImplementedError()
        def elide_cols(ecells):
            return Size(nom=1, rate=0, user=ecells)
        cols = Size.resize(sizes, 0, wrap=False, elide=elide_cols)[0]
        return reduce(lambda a,c: a + c.size, cols, 0)


    def is_open_ended(self):
        return all(c.is_open_ended() for c in self._cell_ctx)


    def _cell_ctx_reduce(self, r, c, n_rows, n_cols):
        ctx = reduce(lambda a,b: b.ctx_merge(a, r, c, n_rows, n_cols), self._cell_ctx, Context())
        tmpl = [x.strip() for x in (ctx['tmpl'] or self['tmpl']).split(',') if x.strip()]
        #while '0' in tmpl: tmpl = tmpl[tmpl.index('0')+1:]
        tmpls = [a for t in tmpl for a in Table._tmpls[t]]
        if tmpls:
            ctx_pre = reduce(lambda a,b: b.ctx_merge(a, r, c, n_rows, n_cols), tmpls, Context())
            pctx = ctx
            while pctx.parent != None:
                pctx = pctx.parent
            pctx.parent = ctx_pre
        return ctx


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


    def _cell_instances(self, n_rows, n_cols):
        if self.__cell_instances != None: return self.__cell_instances
        self.__cell_instances = []
        for i, cell in enumerate(self.cells):
            c = i%n_cols
            ctx = self._cell_ctx_reduce(i//n_cols, c, n_rows, n_cols)
            self.__cell_instances.append(self._cell_instance(cell, ctx))
        return self.__cell_instances
            

    def changed_size(self):
        self.__cell_instances = None
        super().changed_size()


    def flatten(self, w=0, h=0, **kwargs):
        n_cols = len(self.cols)
        cells = self.cells
        n_rows = ceil(len(cells)/n_cols)
        els = self._cell_instances(n_rows, n_cols)
        # Calculate max col widths
        noms = [0]*n_cols
        for i, el in enumerate(els):
            c = i%n_cols
            if noms[c] < (nom:=el['width_nom']): noms[c] = nom
        # Calculate sizes
        sizes = [col.clone(nom=noms[i]) for i,col in enumerate(self.cols)]
        if len(sizes) != n_cols: raise NotImplementedError()
        #print(f"table flatten {len(cells)} els into table {n_rows}x{n_cols} => {sizes}  :{w}x{h}")
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
        self._cell_ctx.append(CellDfn(rstr, **kwargs))


    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s._cells = []
        for row in self.cells:
            rcells = []
            for col in row:
                if isinstance(col[0], Context):
                    rcells.append( (col[0].clone(parent=s, **col[0].ctx_local), col[1]) )
                else:
                    rcells.append( col )
            s._cells.append(rcells)


        #s._cells = [c.clone(parent=s, **c.ctx_local) for c in self.cells]
        if self._cells[-1] == []: s._cells.append([])
        s.cols = list(self.cols)
        s._cell_ctx = list(self._cell_ctx)
        return s



Table.define_tmpl('em', CellDfn('R0', style='em'))
Table.define_tmpl('pad',
    CellDfn('ALL', cls=Borders, border=(' ', 'm:0010')),
    CellDfn('C0', border='m:\n\n0\n'),
)
Table.define_tmpl('sep',
    CellDfn('R0', cls=Borders, border=('b:─-', 'c:\n\n──\n\n--', 'm:\n1\n\n')),
    CellDfn('R0C0', border=('c:\n\n├\n\n\n|\n')),
    CellDfn('R0C-1', border=('c:\n\n\n┤\n\n\n|')),
)
Table.define_tmpl('grid',
    CellDfn('ALL', cls=Borders, border=('-','c:┼┤┴┘++++','m:1010')),
    CellDfn('R0', border=('c:┬┐\n\n++\n\n')),
    CellDfn('C0', border=('c:├\n└\n+\n+\n')),
    CellDfn('C-1', border=('m:1011')),
    CellDfn('R-1', border=('m:1110')),
    CellDfn('R-1C-1', border=('m:1')),
    CellDfn('R0C0', border=('c:┌\n\n\n+\n\n\n')),
)
Table.define_tmpl('dbl',
    CellDfn('R-1', cls=Borders, border=('c:\n\n╧╝\n\n##', 'b:═#', 'm:\n1\n\n')),
    CellDfn('C0', cls=Borders, border=('c:╟╤╚╧####', 'l:║#', 'm:\n\n1\n')),
    CellDfn('C-1', cls=Borders, border=('c:\n╢╧╝\n###','r:║#','m:\n\n\n1')),
    CellDfn('R0', cls=Borders, border=('c:╤╗\n\n##\n\n', 't:═#', 'm:1\n\n\n')),
    CellDfn('R0C0', border=('c:╔\n\n\n#\n\n\n')),
)
Table.define_tmpl('kv',
    #CellDfn('ALL', cls=Borders, border=(' ', 'm:0010')),
    CellDfn('C0', border='m:\n\n0\n', style='1', just='>'),
    #CellDfn('C1', cls=Borders, border=('-', 'm:1'), width_rate=1)
)
