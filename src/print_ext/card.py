from .flex import Flex
from .hr import HR
from .borders import Bdr
from .context import Context



class Card(Flex, border='-', border_style='dem'):
    ''' Show a message in a card-like box.

    Use a tab (\\t) to separate the title from the body.

    >>> Printer().card('\\tHello\\nWorld!')
    ┌────────┐
    │ Hello  │
    │ World! │
    └────────┘
    <print_ext...
    >>> Printer().card('\berr$', 'Danger', '\b$ !\\t', "Don't hold plutonium\\nwith bare hands.")
    ┌┤ Danger! ├───────────┐
    │ Don't hold plutonium │
    │ with bare hands.     │
    └──────────────────────┘
    <print_ext...
    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = HR(parent=self, just='_', width_max=0) # FIXME: We need a way to stop propagation
        self._filling_title = True
        self.body = Bdr(border=(' ','m:01'))
        self(*args)


    def _process_rich_stream(self):
        while self.rich_stream:
            elctx = self.rich_stream.pop(0)
            if isinstance(elctx[0], Context): elctx[0].ctx_parent(None) # reparent to title or body
            if self._filling_title and elctx[0] == '\t':
                self._filling_title = False
                continue
            (self.title if self._filling_title else self.body).rich_stream.append(elctx)
            
    
    def calc_width(self):
        self._process_rich_stream()
        return max(self.title.width, self.body.width+2)


    def calc_height(self):
        self._process_rich_stream()
        return self.title.height + self.body.height + 1


    def flatten(self, w=0, h=0, **kwargs):
        self._process_rich_stream()
        w = w or self.width
        bdr = self['border']
        t = bdr.c[0]+bdr.t[1:3]+bdr.c[1]+bdr.t[4]+  bdr.c[4]+bdr.t[6:8]+bdr.c[5]+bdr.t[9]
        self.title['border'] = Bdr.dfn(bdr, t=t)
        title = list(self.title.flatten(w=w,h=0,**kwargs))
        h = h or self['height_max'] or 0
        if h and h > 2 and len(title) + 2 > h: title = list(self.title.flatten(w=w,h=1,**kwargs))
        if h: h -= len(title)
        yield from title
        body = Bdr(self.body, parent=self, border=('m:0111'))
        yield from body.flatten(w=w, h=h, **kwargs)
        