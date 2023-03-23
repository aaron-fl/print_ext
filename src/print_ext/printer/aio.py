import contextvars, asyncio, random
from .printer_abc import Printer
from .var import printer_var
from ..context import Context, BoolCVar, IntCVar
from ..line import Line, Just

Context.define(BoolCVar('aio_collapse'))
Context.define(IntCVar('show_lines'))


class TaskSummaryPrinter(Printer, aio_collapse=True, show_lines=5):
    ''' A Task that runs in the context of this printer.

    The AIOPrinter captures the print() calls that the task makes and 
    saves them.  When this printer is flattened, it returns a summary
    of the captured print calls.


    '''
    
    def __init__(self, coro, *, context=None, name=None, **kwargs):
        super().__init__(**kwargs)
        ctx = context or contextvars.copy_context()
        ctx.run(lambda: printer_var.set(self))
        self.progress = None
        self.task = ctx.run(lambda: asyncio.create_task(coro, name=kwargs.get('name',None)))
        self.name = name
        self._flatten_count = random.randrange(4) # So spinners don't look synced


    def append(self, line, tag):
        super().append(line, tag)
        if 'progress' in tag:
            self.progress = tag['progress']
        

    #def calc_width(self):
    #    return max(0,0, *map(w[0].width, self._widgets))


    def flatten(self, w=0, h=0, blank=0, show_lines=None, **kwargs):
        if show_lines == None: show_lines = self['show_lines']
        if not show_lines: return []
        if show_lines == -1: return super().flatten(w=w, h=h, blank=blank, **kargs)
        # TODO: Do we use the width of the last N lines or super().calc_width?
        if not w and Just(self['justify'],'<').h != '<':
            raise NotImplementedError()
        status = self.status()
        if not status and self['aio_collapse']: show_lines = 1
        # Collect the last `show_lines` lines
        tail, tail_len = [], 0
        for widget, _ in reversed(self._widgets):
            lines = list(widget.flatten(w=w, **kwargs))
            tail = lines[-(show_lines-tail_len):] + tail
            tail_len = len(tail)
            if tail_len == show_lines: break
        else:
            tail += [Line(parent=self)]*(show_lines-tail_len)
        # Create the bar
        style = ('g!','1','err')[status]
        bar = Line(parent=self)
        if self.progress == None:
            if status == 1:
                bar('|/-\\'[self._flatten_count%4], style=style)
                self._flatten_count += 1
            else:
                bar('!' if status else '*', style=style)
        else:
            chars = '=-' if self['ascii'] else '━┄'
            g = self.progress
            pct = g[0]/float(g[1]) if isinstance(g, tuple) else g if isinstance(g,float) else g/100.0
            barw = 30
            nleft = min(int(pct * barw), barw) if status else barw
            bar(chars[0]*nleft, f"\b;. {chars[1]*(barw-nleft)}", style=style)
        # The end of the bar
        
        if name:=str(self): bar(f'\b2  {name}')
        if len(tail) == 1:
            yield bar(' ', tail[0])
        else:
            yield bar
            yield from tail
        

    def status(self):
        if self.task.done(): return 0
        if self.task.cancelled(): return 2
        return 1


    def __str__(self):
        if self.name!=None: return self.name
        return '' if self.task == None else self.task.get_name()
