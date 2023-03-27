import os, sys, locale, io
from functools import reduce
from ..widget import INFINITY
from ..sgr import SGR
from ..context import Context, CVar
from ..printer_util import Rewinder

Context.define(CVar('end'))


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



class Stream(Context, end='\n'):
    ''' This is an abstract base class for Printers that send their widgets to an `io.Stream`

    When widgets are appended to `StreamPrinter`s they are flattened, serialized, and written to the underlying stream.

    Since it cannot be instantiated directly, calling `StreamPrinter(stream=...)` returns the appropriate subclass that matches the stream.  If no stream is given then `sys.stdout` is used.
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


    def __init__(self, *, stream, styles=default_styles, color=False, **kwargs):
        self.stream = stream
        self.styles = styles
        self.color = color
        super().__init__(**kwargs)


    def append(self, widget, tag):
        for line in widget.flatten():
            self.write_line(line)
            self.stream.write(self['end'])
        super().append(widget, tag)


    def write_line(self, line):
        self.stream.write(self.format_out(*line.styled()))


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


    def __str__(self):
        try:
            return self.stream.getvalue()
        except:
            return repr(self)


class StringRewinder(Rewinder):
    def __init__(self, printer):
        super().__init__(printer)
        self.pos = self.printer.stream.tell()
    

    def __call__(self):
        self.printer.stream.seek(self.pos)
        self.printer.stream.truncate(self.printer.stream.tell())



class StringIO(Stream):
    Rewinder = StringRewinder

    def __init__(self, **kwargs):
        kwargs.setdefault('stream', io.StringIO())
        kwargs.setdefault('color', False)
        super().__init__(**kwargs)



class Oneway(Stream):
    def __init__(self, **kwargs):
        kwargs.setdefault('stream', io.StringIO())
        kwargs.setdefault('color', False)
        super().__init__(**kwargs)



class TTYRewinder(Rewinder):
    def __init__(self, printer):
        super().__init__(printer)
        self.offset = len(self.printer.rw_lines) # Offset into printer.rw_lines
        # If we are the root rewinder, then turn off the cursor
        if self.offset == 0: self.printer.stream.write('\033[?25l')


    def __call__(self):
        # Clear the tail
        self.printer.stream.write('\033[0J') 
        self.printer.rw_lines[self.printer.rw_i:] = []
        # Move the cursor up some lines
        back = self.printer.rw_i - self.offset
        if back: self.printer.stream.write(f'\033[{back}F')
        self.printer.rw_i = self.offset
        self.printer.stream.flush()


    def done(self):
        # Clear the tail
        self.printer.stream.write('\033[0J') 
        self.printer.rw_lines[self.offset:] = []
        # If we are the root rewinder then turn the cursor back on
        if self.offset == 0: self.printer.stream.write('\033[?25h')



class TTY(Stream):
    Rewinder = TTYRewinder

    def __init__(self, **kwargs):
        kwargs.setdefault('color', True)
        try:
            kwargs.setdefault('width_max', os.get_terminal_size().columns-1)
        except OSError: # stdout has been redirected
            pass
        self.rw_lines = []
        self.rw_i = 0
        super().__init__(**kwargs)


    def write_line(self, line):
        if not self.rewinders: return super().write_line(line)
        if self.rw_i == len(self.rw_lines): # New re-writable lines
            self.rw_lines.append(line)
            self.stream.write(self.format_out(*line.styled()))
        else:
            # Patch from rw_lines[rw_i] to line
            self.rw_lines[self.rw_i] = line
            self.stream.write(self.format_out(*line.styled()))
            self.stream.write(f'\033[0K')
        self.rw_i += 1


    def visible_height(self):
        try:
            return os.get_terminal_size().lines-1
        except OSError: # stdout has been redirected
            return INFINITY
