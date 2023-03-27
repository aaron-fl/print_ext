import traceback, os, sys, contextvars, locale, asyncio
from functools import reduce
from .table import Table
from .context import Context, MetaContext
from .flex import Flex
from .text import Text
from .line import Just, Line
from .hr import HR
from .card import Card
from .widget import INFINITY
from .printer_util import Tag 


class MetaPrinter(MetaContext):
    def __call__(self, *args, **kwargs):
        if self != Printer: return super().__call__(*args, **kwargs)
        p = printer_var.get()
        return p(*args, loc=1, **kwargs)



class Printer(Context, metaclass=MetaPrinter, width_max=INFINITY):
    ''' An abstract base class for Printer-like objects.

    Use Printer objects as a replacement for the standard python `print()` function.
    
    Since this is an abstract base class.  Trying to instantiate one with ``Printer()``
    will use the `contextvars` to return a Printer from the current context.
    '''

    Rewinder = None

    @staticmethod
    def using(*bases, name=None, **kwargs):
        bases = (*bases, Printer)
        if not name: name = ''.join(b.__name__ for b in bases)
        return type(name, bases, {}, **kwargs)


    @staticmethod
    def replace(printer=None, context=None, **kwargs):
        if printer == None: printer = Printer().__class__(**kwargs)
        def in_ctx():
            printer_var.set(printer)
            return printer
        if context:
            return context.run(in_ctx)
        else:
            return in_ctx()


    def __init__(self, *, tag=None, name=None, filter=lambda t: t.get('v', 0) <= 0, context=None, **kwargs):
        if isinstance(filter, str): raise NotImplementedError()
        self.filter = filter
        self.name = name
        self._context = context
        self.tag = Tag(tag)
        self.rewinders = []
        super().__init__(**kwargs)


    def _append(self, widget, tag=None, loc=0, proxy=None):
        if proxy == None and tag: proxy = True
        tag = self.tag if tag == None else Tag(tag)
        # Figure out the calling location
        if loc == None:
            loc_tag = tag
        else:
            tb = traceback.extract_stack(limit=3+loc)[0]
            loc_tag = Tag(tag, loc=(os.path.relpath(tb.filename), tb.lineno))
        # Check to see if this tag is filtered
        mute = not self.filter(loc_tag)
        if widget and not mute:
            self.append(widget, loc_tag)
        return PrinterProxy(self, tag, mute) if proxy else self
        

    def append(self, widget, tag):
        pass


    def __call__(self, *args, tag=None, loc=0, **kwargs):
        return self._append(Text(*args, parent=self, **kwargs), tag, loc)


    def flex(self, *args, tag=None, loc=0, **kwargs):
        return self._append(Flex(*args, parent=self, **kwargs), tag, loc)


    def card(self, *args, tag=None, loc=0, **kwargs):
        return self._append(Card(*args, parent=self, **kwargs), tag, loc)


    def hr(self, *args, tag=None, loc=0, **kwargs):
        return self._append(HR(*args, parent=self, **kwargs), tag, loc)


    def pretty(self, *args, tag=None, **kwargs):
        print = self._append(None, tag, loc=None)
        for arg in args:
            pretty(arg, print=print, **kwargs)
        return print


    def context(self):
        ctx = contextvars.copy_context() if self._context == None else self._context.copy()
        ctx.run(lambda: printer_var.set(self))
        return ctx


    def progress(self, *args, **kwargs):
        return Printer.using(ProgressRewind)(context=self.context(), name=Line(*args), parent=self, **kwargs)


    def task_group(self, *args, **kwargs):
        return PrinterProgressWaiter(self, name=Line(*args), **kwargs)


    def widgets(self, *widgets, tag=None, loc=0):
        print = self._append(None, tag, loc=None)
        for widget in widgets:
            print._append(widget.ctx_parent(self), loc=loc)
        return print
   

    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s.filter = self.filter
        s.tag = Tag(self.tag)
        return s


    def height_visible(self):
        return INFINITY


    def rewind(self):
        if not self.Rewinder: raise ValueError(f"{self} is not rewindable")
        return self.Rewinder(self)



class PrinterProgressWaiter():
    def __init__(self, printer, fps=5, **kwargs):
        self.printer = printer
        self.fps = fps
        self.tg = Printer.using(TaskGroup, Progress)(context=printer.context(), parent=printer, **kwargs)


    async def __aenter__(self):
        return self.tg


    async def __aexit__(self, *args):
        if not self.printer.Rewinder:
            await self.tg
            return
        with self.printer.rewind() as rewind:
            i = 0
            done = False
            while not done:
                self.printer.widgets(self.tg)
                i += 1
                rewind()
                done, pending = await asyncio.wait([self.tg], timeout=1.0/self.fps)
                if done:
                    done = done.pop()
                    done.result()
            self.printer.widgets(self.tg)


class PrinterProxy(Printer):
    def __init__(self, parent, tag, mute):
        self.tag = tag
        self.mute = mute
        self._parent = parent


    def _append(self, widget, tag=None, loc=0, proxy=None):
        if self.mute: return self
        return self._parent._append(widget, tag, loc, tag != None)


    def __getattr__(self, attr):
        return getattr(self._parent, attr)


    def __setattribute__(self, attr, val):
        if attr in ('tag', 'mute', '_printer'):
            return super().__setattribute__(attr, val)
        return setattr(self._parent, attr, val)


# Pretty requires Printer
from .pretty import pretty


def printer_for_stream(**kwargs):
    kwargs.setdefault('stream', sys.stdout)
    if 'ascii' not in kwargs: kwargs['ascii'] = (locale.getdefaultlocale()[1].lower() != 'utf-8')
    #if 'lang' not in kwargs:
    #    kwargs['lang'] = locale.getdefaultlocale()[0]
    #kwargs['lang'] = kwargs['lang'].lower()
    try:
        if not kwargs['stream'].isatty(): raise AttributeError()
        kind = TTY
    except AttributeError:
        try:
            if not kwargs['stream'].seekable(): raise AttributeError()
            kind = StringIO
        except AttributeError:
            kind = Oneway
    return Printer.using(kind)(**kwargs)

from .mixins import TaskGroup, StringIO, Oneway, ProgressRewind, Progress
from .mixins.stream import TTY

printer_var = contextvars.ContextVar('Printer', default=printer_for_stream())

