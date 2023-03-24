import os, contextvars, asyncio, random, functools
from ...context import Context, BoolCVar, IntCVar, CVar
from ..printer import printer_var
from ..widget import WidgetPrinter
from ..oneway import OnewayPrinter
from .summarizer import Summarizer


Context.define(IntCVar('collapse_when_done'))
Context.define(BoolCVar('capture'))
Context.define(IntCVar('buffer_lines'))
Context.define(CVar('summarizer'))

TASK_COMPLETE = 0
TASK_FAIL = 1
TASK_RUNNING = 2


class TaskPrinter(WidgetPrinter, collapse_when_done=1, capture=True, buffer_lines=256, height_max=5, summarizer=Summarizer):
    ''' An abstract base class for async tasks/coroutines.

    We capture the print() calls that the task makes and save them (possibly to file).
    When this printer is flattened, it returns a summary of the task's output.
    '''
    def __init__(self, *, context=None, name=None, log_file=None, **kwargs):
        if context == None: context = contextvars.copy_context()
        self.printer = context.run(lambda: printer_var.get())
        if isinstance(self.printer, OnewayPrinter): kwargs['capture'] = False
        self.context = context.copy()
        self.context.run(lambda: printer_var.set(self))
        super().__init__(**kwargs)
        self.capture = self['capture'] or isinstance(self.printer, TaskPrinter)
        self.progress = None
        self.log_file = log_file
        self.deleted_lines = 0
        self.buffer = []
        self.status_style = ['g!', 'err', '1']
        self.name = name
        self._spinner_i = random.randrange(4) # So spinners don't look synced
        self.tasks = []
        self.summarizer = self['summarizer'](parent=self)


    def task(self, coro, **kwargs):
        self.tasks.append(super().task(coro, **kwargs))
        
    

    def ensure_tasks_running(self):
        ''' If we were started outside of an event loop then we need to start all the coroutines
        '''
        for task in self.tasks:
            task.ensure_tasks_running()


    def append(self, widget, tag):
        self.progress = tag.get('progress', self.progress)
        if self.capture:
            super().append(widget, tag)
            return True # we captured the widget
        if isinstance(self.printer, TaskPrinter):
            self.printer._sub_append(widget, tag, self)
        else:
            self.printer.append(widget, tag)


    def _sub_append(self, widget, tag, task):
        ''' One of our child task's print() calls is bubbling up to us.
        '''
        raise NotImplementedError()


    def progress_pct(self, status):
        g = self.progress
        # Currently running with an unknown end
        if g == None: return 2 if status == None else -1
        # Done running with an unknown end
        if g == 'done': return 0 if status == None else -1
        # Normalize progress to the range (0.0, 1.0)  negative if error
        g = g[0]/float(g[1]) if isinstance(g, tuple) else g if isinstance(g,float) else g/100.0
        # Derive status from g
        if status == None: return 0 if g == 1.0 else 1 if g < 0 else 2
        # Don't let the bar finish until status is done
        return min(abs(g), 0.99) if status else 1.0

    
    def status(self):
        if not self.tasks: return self.progress_pct(None)
        return reduce(lambda a, s: max(a,s), self.tasks, 0)
        

    def __str__(self):
        return self.name or ''


    def clone(self, **kwargs):
        s = super().clone(**kwargs)
        s.progress = self.progress
        s.name = self.name
        return s
        

    async def wait(self, fps=5):
        self.ensure_tasks_running()
        if not self.tasks: return
        # If we aren't capturing then all prints are just going upstream.  So simply wait for everyone.
        if not self.capture:
            await asyncio.gather(*[t if isinstance(t, asyncio.Task) else t.wait() for t in self.tasks], return_exceptions=False)
            return
        # Rewindable
        with self.printer.rewind() as rewind:
            auto_id = 0
            pending = []
            for task in self.tasks:
                if not isinstance(task, asyncio.Task):
                    task = asyncio.create_task(task.wait(), name=f"{self.name}#{auto_id}" if auto_id else self.name)
                auto_id += 1
                pending.append(task)
            while pending:
                self.printer.widgets(self)
                rewind()
                done, pending = await asyncio.wait(pending, timeout=1.0/fps, return_when=asyncio.FIRST_EXCEPTION)
            self.printer.widgets(self)


    def sync(self, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon(functools.partial(self.wait, **kwargs))
        except RuntimeError:
            asyncio.run(self.wait(**kwargs))


    def calc_width(self):
        return self.summarizer.calc_width()


    def calc_height(self):
        return self.summarizer.calc_height()
    

    def flatten(self, **kwargs):
        yield from self.summarizer.flatten(**kwargs)



from .coro import CoroTaskPrinter
