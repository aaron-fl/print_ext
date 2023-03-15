import os, sys, locale, io
from functools import reduce
from .table import Table
from .context import Context
from .flex import Flex
from .text import Text
from .line import Just
from .pretty import pretty
from .sgr import SGR
from .hr import HR
from .rich import Rich
from .card import Card
from .progress import Progress
from .widget import INFINITY


def stack_enum(txt, stack):
    a, b = 0, 0
    _pop, stk = [], []
    while a < len(txt):
        if a != b:
            yield txt[a:b], stk
            a = b
        # Apply pop styles to stk
        while _pop and _pop[-1].e == b:
            j, s = 0, _pop.pop().style
            while not s: j, s = j+1, _pop[-j-1].style
            stk.append(_pop[-2*(j-1)-1].style) if j else stk.pop()
        # Apply pre styles to stk 
        while stack and stack[0].s == b:
            _pop.append(stack.pop(0))
            stk.append(_pop[-1].style) if _pop[-1].style else stk.pop()
        # Advance to the next style boundry
        b = min(stack[0].s if stack else INFINITY, _pop[-1].e if _pop else INFINITY)



def _stack_enum(txt, stack):
    # De-duplicate styles
    ps, pstk = '', None
    for s, stk in _stack_enum(txt,stack):
        if pstk == None or pstk == stk:
            ps += s
        else:
            yield ps, pstk
            ps = s
        pstk = stk[:]
    yield ps, pstk



class Printer(Context):
    def __init__(self, **kwargs):
        self._widgets = []
        self.blank = 0
        super().__init__(**kwargs)


    def append(self, widget):
        self._widgets.append(widget)


    def padded(self, pad, el):
        if isinstance(pad,int):
            pad = (-pad, 0) if pad < 0 else (pad,pad)
        padl, padr = pad
        while (padl:=padl-1) >= 0:
            self.append(Text(' ',parent=self))
        self.append(el)
        while (padr:=padr-1) >= 0:
            self.append(Text(' ',parent=self))
        return self


    def __call__(self, *args, pad=0, **kwargs):
        if pad: return self.padded(pad, Text(*args, parent=self, **kwargs))
        self.append(Text(*args, parent=self, **kwargs))
        return self


    def flex(self, *args, pad=0, **kwargs):
        if pad: return self.padded(pad, Flex(*args, parent=self, **kwargs))
        self.append(Flex(*args, parent=self, **kwargs))
        return self


    def card(self, *args, pad=0, **kwargs):
        if pad: return self.padded(pad, Card(*args, parent=self, **kwargs))
        self.append(Card(*args, parent=self, **kwargs))
        return self


    def hr(self, *args, pad=0, **kwargs):
        if pad: return self.padded(pad, HR(*args, parent=self, **kwargs))
        self.append(HR(*args, parent=self, **kwargs))
        return self


    def pretty(self, *args, pad=0, **kwargs):
        return self(*(pretty(a,**kwargs) for a in args), pad=pad, **kwargs)


    def calc_width(self):
        return max(0,0, *map(w.width, self._widgets))


    def flatten(self, w=0, h=0, blank=0, **kwargs):
        self.blank = blank
        if h != 0: return flatten_fix_height(w=w, h=h, **kwargs)
        if not w and Just(self['justify'],'<').h != '<':
            w = self.width # We need to be able to right/center justify to our natural width
        for widget in self._widgets:
            new_blank = 0
            for line in widget.flatten(w=w, **kwargs):
                if (is_blank:=line.is_blank()) and self.blank:
                    self.blank -= 1
                    continue
                self.blank = 0
                new_blank = new_blank+1 if is_blank else 0
                yield line
            self.blank += new_blank


    def flatten_fix_height(self, *, w, h, **kwargs):
        raise NotImplementedError()


    def __repr__(self):
        return f"<Printer>"



class Flattener(Printer):
    ''' This is an object for aliasing the print function.
    '''
    default_styles = {
        'err' : 'r!,',
        'warn': 'y!,',
        'em'  : '!',
        'dem' : 'w.;',
        '1' : 'y,',
        '2' : 'm,',
        '3' : 'c,',
    }

    print = print # The legacy print() function

    def __init__(self, *, stream=None, color=None, width=None, isatty=None, styles=default_styles, **kwargs):
        self.styles = styles
        self.stream = stream or sys.stdout
        kwargs = {k:v for k,v in kwargs.items() if v != None}
        if isatty==None:
            try:    self.isatty = self.stream.isatty()
            except: self.isatty = False
        if 'lang' not in kwargs:
            kwargs['lang'] = locale.getdefaultlocale()[0]
        kwargs['lang'] = kwargs['lang'].lower()
        if width == None:
            try:    width = os.get_terminal_size().columns-1
            except: width = INFINITY
        kwargs['width_max'] = width
        if 'ascii' not in kwargs:
            kwargs['ascii'] = (locale.getdefaultlocale()[1].lower() != 'utf-8')
        self.color = self.isatty if color == None else color
        super().__init__(**kwargs)
        self.blank = 0


    def format_out(self, txt, styles):
        stripped = txt.rstrip()
        if not self.color: return stripped
        s = ''
        sgr_prev = SGR()
        for t,stk in stack_enum(txt, styles):
            sgrs = [SGR(self.styles.get(y,y)) for y in stk] or [SGR()]
            sgr_next = reduce(lambda a,b: a+b, sgrs)
            code = sgr_next.diff(sgr_prev)
            s += code
            sgr_prev = sgr_next
            s += stripped[:len(t)]
            stripped = stripped[len(t):]
        if sgr_prev: s += '\033[0m'
        return s


    def append(self, widget):
        super().append(widget)
        for line in self.flatten(blank=self.blank):
            self.stream.write(self.format_out(*line.styled()))
            self.stream.write('\n')
        self._widgets = []


    #def each_line(self, *args, **kwargs):
    #    t = Text(*args, parent=self, **kwargs)
    #    yield from t.flatten(**kwargs)


    def progress(self, *args, **kwargs):
        return Progress(*args, parent=self, **kwargs)
        

    def to_str(self, *args, **kwargs):
        saved = self.stream
        self.stream = io.StringIO()
        self(*args, **kwargs)
        val = self.stream.getvalue()
        self.stream = saved
        return val
