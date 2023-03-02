from .text import Text
from .rich import Rich
from .span import Span
from .line import Line
from .size import Size
from .context import Context, ObjectAttr, CVar, BoolCVar, EnumCVar, FloatCVar


Context.define(BoolCVar('flex_reverse'))
Context.define(BoolCVar('flex_wrap'))
Context.define(EnumCVar('flex_dir', options=('-','|')))
Context.define(FloatCVar('height_rate', 'hs'))
Context.define(FloatCVar('width_rate', 'ws'))



class Flex(Rich):
    ''' A list of objects

    :Attributes:
        just:
            flex Justification:
                `<` : Left
                `.` : Center
                `>` : Right
                `#` : Space between
                `%` : Space around
        flex_reverse:
            Render the elements in reverse order

    :Examples:

        
    '''    
    def __init__(self, *args, **kwargs):
        self._cells = [[]]
        super().__init__(*args, **kwargs)


    @property
    def cells(self):
        if not self.rich_stream: return self._cells[:-1] if self._cells[-1] == [] else self._cells
        if self._cells[-1] != []: self._cells.append([self._cells.pop()])
        while self.rich_stream:
            elctx = self.rich_stream.pop(0)
            if elctx[0] == '\t':
                self._cells.append([])
            else:
                self._cells[-1].append(elctx)
        # Form arrays of (el,ctx) into a single Context object
        for i, els in enumerate(reversed(self._cells)):
            if i==0 and els==[]: continue # skip trailing []
            if isinstance(els, Context): break
            if els and isinstance(els[0], Context):
                self._cells[-1-i] = els.pop(0)
            elif els and isinstance(els[0][0], Context):
                el, ctx = els.pop(0)
                el = el.ctx_parent(self)
                el.ctx(**ctx)
                self._cells[-1-i] = el
            else:
                self._cells[-1-i] = Text(parent=self)
            for el, ctx in els:
                self._cells[-1-i](el, **ctx)
        return self._cells[:-1] if self._cells[-1] == [] else self._cells


    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s._cells = [c.clone(parent=s, **c.ctx_local) for c in self.cells]
        if self._cells[-1] == []: s._cells.append([])
        return s


    def each_child(self):
        yield from self.cells


    def _flatten_width_row(self, cells, w, h):
        #print(f"_flatten_width_row {w}x{h} : {cells} ")
        flat = [list(c.user.flatten(w=c.size,h=h)) for c in cells]
        if h == 0:
            mh = len(flat[0]) if len(flat) == 1 else max(*[len(x) for x in flat])
            flat = [f if len(f) == mh else list(c.user.flatten(w=c.size,h=mh)) for f, c in zip(flat, cells)]
        return [Line(*f, parent=self).justify(w) for f in zip(*flat)]


    def _flatten_width(self, cells, wrap, w, h):
        #print(f'_flatten_width wrap?:{wrap}  {w}x{h}')
        #for cell in cells:
        #    print(f'   --{cell.user}-- ', cell)

        def elide_cols(cells):
            dots = '~' if self['ascii'] else '…'
            if w > 30: dots = f'{dots}{len(cells)}{dots}'
            s = Line(style="dem", parent=self).insert(0, dots)
            return Size(nom=s.width, rate=0, user=s)

        def elide_rows(cells):
            vbar = '|' if self['ascii'] else '⋮'
            s = Line(parent=self, style="dem", justify='|').insert(0, f'{vbar}{len(cells)}{vbar}')
            if w and s.width > w: s = Line(parent=self, style="dem", justify='|').insert(0, vbar)
            return Size(nom=1, rate=0, user=[Size(size=w, nom=s.width, user=s)])

        rows = Size.resize(cells, w, wrap, elide_cols)
        flats = [self._flatten_width_row(row, w, 0) for row in rows]
        collapse = [z for y in flats for z in y]
        if not h or len(collapse) == h: return collapse
        # Our height doesn't fit, so perform another resize for the cross axis
        #print("="*80)
        hcells = [Size(nom=len(flat), user=row) for row,flat in zip(rows,flats)]
        col = Size.resize(hcells, h, wrap=False, elide=elide_rows)[0]
        flats = [self._flatten_width_row(c.user, w, c.size) for c in col]
        #print(f"HEIGHTS", ''.join(f'\n   {c} {c.user}' for c in col))
        collapse = [z for y in flats for z in y]
        assert(len(collapse) == h)
        return collapse


    _keys = ('nom', 'min', 'max', 'rate')

    def flatten(self, w=0, h=0, **kwargs):
        wrap = self['flex_wrap']
        els = list(reversed(self.cells) if self['flex_reverse'] else self.cells)
        if not els: return []
        d = 'width' if (self['flex_dir'] or '-') == '-' else 'height'
        def _size(e):
            args = {k:e.ctx(f'{d}_{k}') for k in Flex._keys}
            return Size(user=e, **{k:v for k,v in args.items() if v != None})
        cells = [_size(e) for e in els]
        if d == 'width': return self._flatten_width(cells, wrap, w, h)
        raise NotImplementedError()


    def tab(self, **kwargs):
        _ = self.cells
        if self._cells[-1] == []:self._cells.pop()
        self._cells.append(Text(parent=self, **kwargs))
        return self
