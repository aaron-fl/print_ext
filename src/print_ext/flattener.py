import os, sys, locale, io
from functools import reduce
from .printer import Printer
from .widget import INFINITY
from .sgr import SGR
from .progress import Progress


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

    def __init__(self, *, stream=None, color=None, width=None, isatty=None, styles=default_styles, **kwargs):
        self.styles = styles
        self.stream = stream or sys.stdout
        kwargs = {k:v for k,v in kwargs.items() if v != None}
        if isatty==None:
            try:    self.isatty = self.stream.isatty()
            except: self.isatty = False
        #if 'lang' not in kwargs:
        #    kwargs['lang'] = locale.getdefaultlocale()[0]
        #kwargs['lang'] = kwargs['lang'].lower()
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


    def append(self, widget, tag):
        super().append(widget, tag)
        for line in self.flatten(blank=self.blank):
            self.stream.write(self.format_out(*line.styled()))
            self.stream.write('\n')
        self._widgets = []


    def progress(self, *args, **kwargs):
        return Progress(*args, parent=self, **kwargs)
        

    def to_str(self, *args, **kwargs):
        saved = self.stream
        self.stream = io.StringIO()
        self(*args, **kwargs)
        val = self.stream.getvalue()
        self.stream = saved
        return val
