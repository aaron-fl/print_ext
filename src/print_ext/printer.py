import traceback, os
from functools import reduce
from .table import Table
from .context import Context
from .flex import Flex
from .text import Text
from .line import Just
from .pretty import pretty
from .hr import HR
from .card import Card


class Printer(Context):
    def __init__(self, tag=None, q=lambda t: t.get('v',0)>0, **kwargs):
        self._widgets = []
        self.blank = 0
        if isinstance(q, str): raise NotImplementedError()
        self.q = q
        self.tag = tag or {'v':0}
        super().__init__(**kwargs)


    def _append(self, widget, pad, tag, proxy=None, stack_offset=0):
        if isinstance(tag, str): # Convert str to dict
            tag = dict((t.split(':',1)+[True])[:2] for t in tag.split(';'))
            for k,v in tag.items():
                try: tag[k] = int(v)
                except ValueError:
                    try: tag[k] = float(v)
                    except ValueError: pass
        local_tag = dict(self.tag if tag == None else tag)
        mute = self.q(local_tag)
        rval = PrinterProxy(self, tag, mute) if proxy or (proxy==None and tag) else self
        if not widget or mute: return rval
        #widget = widget.ctx_parent(self)
        tb = traceback.extract_stack(limit=3+stack_offset)[0]
        local_tag['loc'] = (os.path.relpath(tb.filename), tb.lineno)
        if pad:
            if isinstance(pad,int):
                pad = (-pad, 0) if pad < 0 else (pad,pad)
            padl, padr = pad
            while (padl:=padl-1) >= 0:
                self.append(Text(' ',parent=self), local_tag)
            self.append(widget, local_tag)
            while (padr:=padr-1) >= 0:
                self.append(Text(' ',parent=self), local_tag)
        else:
            self.append(widget, tag)
        return rval


    def append(self, widget, tag):
        self._widgets.append((widget,tag))


    def __call__(self, *args, pad=0, tag=None, stack_offset=0, **kwargs):
        return self._append(Text(*args, parent=self, **kwargs), pad, tag, stack_offset=stack_offset)


    def flex(self, *args, pad=0, tag=None, **kwargs):
        return self._append(Flex(*args, parent=self, **kwargs), pad, tag)


    def card(self, *args, pad=0, tag=None, **kwargs):
        return self._append(Card(*args, parent=self, **kwargs), pad, tag)


    def hr(self, *args, pad=0, tag=None, **kwargs):
        return self._append(HR(*args, parent=self, **kwargs), pad, tag)


    def pretty(self, *args, pad=0, tag=None, **kwargs):
        for arg in args:
            r = self._append(Text(pretty(arg,**kwargs), parent=self, **kwargs), pad, tag)
        return r
        

    def calc_width(self):
        return max(0,0, *map(w[0].width, self._widgets))


    def flatten(self, w=0, h=0, blank=0, **kwargs):
        self.blank = blank
        if h != 0: return flatten_fix_height(w=w, h=h, **kwargs)
        if not w and Just(self['justify'],'<').h != '<':
            w = self.width # We need to be able to right/center justify to our natural width
        for widget, tag in self._widgets:
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

    
    def clone(self, **kwargs):
        s = self.__class__(**kwargs)
        s._widgets = [(w.clone(parent=s, **w.ctx_local), tag) for w,tag in self._widgets]
        s.blank = self.blank
        s.q = self.q
        s.tag = self.tag
        return s




class PrinterProxy(Printer):
    def __init__(self, printer, tag, mute):
        self.tag = tag
        self.mute = mute
        self.printer = printer


    def _append(self, widget, pad, tag, proxy=None, stack_offset=0):
        if self.mute: return self
        proxy = tag != None
        if tag == None: tag = self.tag
        return self.printer._append(widget, pad, tag, proxy=proxy, stack_offset=stack_offset)


    def __getattr__(self, attr):
        return getattr(self.printer, attr)


    def __setattribute__(self, attr, val):
        if attr in ('tag', 'mute', 'printer'):
            return super().__setattribute__(attr, val)
        return setattr(self.printer, attr, val)
