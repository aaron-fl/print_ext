import traceback, os, contextvars
from functools import reduce
from ..table import Table
from ..context import Context, MetaContext
from ..flex import Flex
from ..text import Text
from ..line import Just, Line
from ..hr import HR
from ..card import Card
from ..widget import INFINITY


class Tag():

    def __init__(self, tag=None, **kwargs):
        self.parent = tag
        self._dict = kwargs
        if isinstance(tag, str):
            self._dict = dict((t.split(':',1)+[True])[:2] for t in tag.split(';'))
            for k,v in self._dict.items():
                try: self._dict[k] = int(v)
                except ValueError:
                    try: self._dict[k] = float(v)
                    except ValueError: pass
            self._dict.update(kwargs)
            self.parent = None
        elif isinstance(tag, dict):
            self._dict.update(tag)
            self.parent = None
        if self.parent and not isinstance(self.parent, Tag):
            raise ValueError(f"{self.parent!r} is not a `Tag`")
        
    
    def get(self, key, default=None):
        if key in self._dict: return self._dict[key]
        if self.parent: return self.parent.get(key, default)
        return default



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

    @staticmethod
    def replace(printer=None, context=None, **kwargs):
        def in_ctx():
            p = StreamPrinter(**kwargs) if printer==None else printer
            printer_var.set(p)
            return p
        if context:
            return context.run(in_ctx)
        else:
            return in_ctx()


    def __init__(self, tag=None, filter=lambda t: t.get('v', 0) <= 0, **kwargs):
        if isinstance(filter, str): raise NotImplementedError()
        self.filter = filter
        self.tag = Tag(tag)
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
        raise NotImplementedError()


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


    def self_printer_context(self):
        ctx = contextvars.copy_context()
        ctx.run(lambda: printer_var.set(self))
        return ctx


    def progress(self, *args, **kwargs):
        return ProgressTaskPrinter(context=self.self_printer_context(), name=Line(*args), parent=self, **kwargs)


    def task(self, coro, **kwargs):
        return CoroTaskPrinter(coro, context=self.self_printer_context(), parent=self, **kwargs)


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



# pretty requires PrinterWidget which requires Printer
from ..pretty import pretty
from .stream import StreamPrinter
printer_var = contextvars.ContextVar('Printer', default=StreamPrinter())
# TaskPrinter requires printer_var
from .task import ProgressTaskPrinter, CoroTaskPrinter
