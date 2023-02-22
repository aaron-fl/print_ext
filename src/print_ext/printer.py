import os, sys, locale
from functools import reduce
#from .text import Text
#from .progress import ProgressBar
#from .box import Box
from .table import Table
from .context import Context
from .flex import Flex
from .fill import Fill
from .sgr import SGR
from .hr import HR
from tests.testutil import debug_dump

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
        b = min(stack[0].s if stack else 1000000000, _pop[-1].e if _pop else 1000000000)


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
    ''' This is an object for aliasing the print function.
    '''
    default_styles = {
        'err' : 'r!_',
        'warn': 'y!',
        'em'  : '!_',
        'dem' : 'k!',
        '1' : 'y!',
        '2' : 'm!',
        '3' : 'c!',
    }

    def __init__(self, *, stream=None, color=None, width=None, isatty=None, styles=default_styles, **kwargs):
        self.styles = styles
        self.stream = stream or sys.stdout
        kwargs = {k:v for k,v in kwargs.items() if v != None}
        if isatty==None:
            try:    isatty = self.stream.isatty()
            except: isatty = False
        if 'lang' not in kwargs:
            kwargs['lang'] = locale.getdefaultlocale()[0]
        kwargs['lang'] = kwargs['lang'].lower()
        if width == None:
            try:    width = os.get_terminal_size().columns-1
            except: width = 78
        kwargs['width_max'] = width
        if 'ascii_only' not in kwargs:
            kwargs['ascii_only'] = (locale.getdefaultlocale()[1].lower() == 'utf-8')
        self.color = isatty if color == None else color
        super().__init__(**kwargs)
        self.blank = 0


    def format_out(self, txt, styles):
        stripped = txt.rstrip()
        s = ''
        sgr_prev = SGR()
        for t,stk in stack_enum(txt, styles):
            sgrs = [SGR(self.styles.get(y,y)) for y in stk] or [SGR()]
            #print(f'format_out {repr(stripped[:len(t)])} {stk} -> {sgrs}')
            if self.color:
                sgr_next = reduce(lambda a,b: a+b, sgrs)
                code = sgr_next.diff(sgr_prev)
                #print(f"         {sgr_prev} -> {sgr_next}  {repr(code)}")
                s += code
                sgr_prev = sgr_next
            s += stripped[:len(t)]
            stripped = stripped[len(t):]
        if sgr_prev: s += '\033[0m'
        return s


    def stream_out(self, lines):
        new_blank = 0
        for line in lines:
            line = self.format_out(*line.styled()) if hasattr(line, 'styled') else str(line).rstrip()
            if not line and self.blank:
                self.blank -= 1
                continue
            self.blank = 0
            new_blank = 0 if line else new_blank + 1
            self.stream.write(line+'\n')
        self.blank += new_blank


    def __call__(self, *args, **kwargs):
        f = Flex(*args, parent=self, **kwargs)
        self.stream_out(f.flatten(**kwargs))


    def table(self, *args, **kwargs):
        return Table(*args, parent=self, **kwargs)


    def progress(self, *msg, **kwargs):
        kwargs.setdefault('pad', (1,0))
        self.ln(*msg, **kwargs)
        return ProgressBar(ctx=self, **kwargs)


    #def box(self, *msg, **kwargs):
    #    self(*Box(*msg, **kwargs).reflow(kwargs.get('width',0), kwargs.get('height',0)))


    def hr(self, *args, **kwargs):
        print(f"SELFMAX {self['width_max']}")
        self(HR(*args, **kwargs))


    def pretty(self, v, width=0):
        flat = repr(v)
        if len(flat) <= width: return [flat]
        lines = []
        if isinstance(v, list):
            for el in v:
                els = self.pretty(el, width=width-2)
                lines += ['- '+els[0]] + ['  '+x for x in els[1:]]
        elif isinstance(v, dict):
            keymax = max(map(len, v.keys()))
            for k, v in v.items():
                vels = self.pretty(v, width=width-keymax-2)
                lines += [' '*(keymax-len(k))+k+' : '+vels[0]] + [' '*(keymax+3)+l for l in vels[1:]]
        elif hasattr(v, 'pretty'):
            lines += v.pretty(width=width)
        else:
            while len(flat) > width:
                lines.append(flat[:width])
                flat = flat[width:]
            if flat: lines.append(flat)
        return lines or ['']
