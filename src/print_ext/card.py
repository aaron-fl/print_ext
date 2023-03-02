from .flex import Flex
from .hr import HR
from .borders import Borders, BorderDfn
from .context import Context



class Card(Flex, border='-'):
    ''' Show a message in a card-like box.

    Use a tab (\\t) to separate the title from the body.
    
    >>> from print_ext.printer import Printer
    >>> Printer().card('\\tHello\vWorld!')
    ┌────────┐
    │ Hello  │
    │ World! │
    └────────┘
    >>> card = Card('\berr$', 'Danger', '\b$ !\\t', "Don't hold plutonium\vwith bare hands.")
    >>> Printer(lang='en')(card) 
    ┌─────┤ Danger! ├──────┐
    │ Don't hold plutonium │
    │ with bare hands.     │
    └──────────────────────┘
    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = HR(parent=self, just='_', width_max=0) # FIXME: We need a way to stop propigation
        self._filling_title = True
        self.body = Borders(border=(' ','m:01'))
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
        l = bdr.l[0:4] + BorderDfn.join(BorderDfn.ext(bdr.l[2] + ' ' + bdr.l[2] + bdr.t[2])) + bdr.l[5:10]
        r = bdr.r[0:4] + BorderDfn.join(BorderDfn.ext(bdr.l[2] + bdr.t[2] + bdr.l[2] + ' ')) + bdr.r[5:10]
        self.title['border'] = BorderDfn(bdr, t=t, l=l, r=r)
        title = list(self.title.flatten(w=w,h=0,**kwargs))
        h = h or self['height_max'] or 0
        if h and h > 2 and len(title) + 2 > h: title = list(self.title.flatten(w=w,h=1,**kwargs))
        if h: h -= len(title)
        yield from title
        body = Borders(self.body, parent=self, border=('m:0111'))
        yield from body.flatten(w=w, h=h, **kwargs)
        