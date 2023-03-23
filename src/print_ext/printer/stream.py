import os, sys, locale
from functools import reduce
from ..widget import INFINITY
from ..sgr import SGR
from .printer_abc import Printer
from .rewinder import Rewinder

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



class StreamPrinter(Printer):
    ''' The things printed to this printer are immediately flattened
    and sent to the stream.
    '''

    Rewinder = Rewinder

    default_styles = {
        'err' : 'r!,',
        'warn': 'y!,',
        'em'  : '!',
        'dem' : 'w.;',
        '1' : 'y,',
        '2' : 'm,',
        '3' : 'c,',
    }


    def __new__(self, oneway=False, **kwargs):        
        if self == StreamPrinter:
            stream = kwargs.get('stream', sys.stdout)
            try:
                if not stream.isatty(): raise AttributeError()
                cls = TTYPrinter
            except AttributeError:
                cls = OnewayIOPrinter if not stream.seekable() or oneway else StringPrinter
        else: # Direct creation of subclass
            cls, stream = self, kwargs.get('stream', None)
        obj = super().__new__(cls)
        obj.stream = stream
        return obj


    def __init__(self, *args, styles=default_styles, end='\n', **kwargs):
        self.styles = styles
        self.end = end
        if 'width_max' not in kwargs:
            try:    kwargs['width_max'] = os.get_terminal_size().columns-1
            except: kwargs['width_max'] = INFINITY
        if 'ascii' not in kwargs:
            kwargs['ascii'] = (locale.getdefaultlocale()[1].lower() != 'utf-8')
        #if 'lang' not in kwargs:
        #    kwargs['lang'] = locale.getdefaultlocale()[0]
        #kwargs['lang'] = kwargs['lang'].lower()
        super().__init__(**kwargs)
        self.rewinders = []


    def append(self, widget, tag):
        for line in widget.flatten():
            self.write_line(line)
            self.write_end()


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


    def write_line(self, line):
        self.stream.write(self.format_out(*line.styled()))


    def write_end(self):
        self.stream.write(self.end)
        if self.end != '\n': self.stream.flush()
        

    def rewind(self):
        return self.Rewinder(self)


# These are subclasses of StreamPrinter
from .tty import TTYPrinter
from .string import StringPrinter
from .oneway import OnewayPrinter