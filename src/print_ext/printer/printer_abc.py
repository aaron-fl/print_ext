import traceback, os
from functools import reduce
from ..table import Table
from ..context import Context
from ..flex import Flex
from ..text import Text
from ..line import Just
from ..hr import HR
from ..card import Card


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
        if self.parent and not isinstance(self.parent, Tag):
            raise ValueError(f"{self.parent!r} is not a `Tag`")
        
    
    def get(self, key, default=None):
        if key in self._dict: return self._dict[key]
        if self.parent: return self.parent.get(key, default)
        return default



class Printer(Context):
    def __init__(self, tag=None, q=lambda t: t.get('v',0)>0, **kwargs):
        self._widgets = []
        if isinstance(q, str): raise NotImplementedError()
        self.q = q
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
        mute = self.q(loc_tag)
        if widget and not mute:
            self.append(widget, loc_tag)
        return PrinterProxy(self, tag, mute) if proxy else self
        

    def append(self, widget, tag):
        self._widgets.append((widget,tag))


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


    def widgets(self, *widgets, tag=None, loc=0):
        print = self._append(None, tag, loc=None)
        for widget in widgets:
            print._append(widget.ctx_parent(self), loc=loc)
        return print
   

    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s._widgets = [(w.clone(parent=s, **w.ctx_local), tag) for w,tag in self._widgets]
        s.q = self.q
        s.tag = Tag(self.tag)
        return s




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
