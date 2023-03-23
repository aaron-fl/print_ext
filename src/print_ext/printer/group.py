from .aio import TaskSummaryPrinter
from ..context import Context, BoolCVar

Context.define(BoolCVar('rewindable'))



class ParallelPrinter(TaskSummaryPrinter):
    def __init__(self, context=None, **kwargs):
        super().__init__(**kwargs)
        self.context = context or contextvars.copy_context()
        self.tasks = []


    def create_task(self, coro, context=None, **kwargs):
        task = AIOPrinter.create_task(coro, context=context or self.context, **kwargs)
        self.tasks.append(task.ctx_parent(self))


    def flatten(self, w=0, h=0, *, rewindable=True, **kwargs):
        if not rewindable: return self._flatten_no_rewind(w,h,**kwargs)
        if h: raise NotImplementedError()
        for task in self.tasks:
            for line in task.flatten(w=w, h=h, **kwargs):
                yield line


    def _flatten_no_rewind(self, w, h, **kwargs):
        raise NotImplementedError()


    async def wait(self, fps=0):
        print = self.context.run(lambda: printer())
        pending = [t.task for t in self.tasks]
        try:
            rewind = print.rewind()
        except AttributeError:
            return await self._wait_no_rewind(fps or 1, print, pending)
        with rewind:
            return await self._wait_rewind(fps or 5, print, pending, rewind)


    async def _wait_rewind(self, fps, print, pending, rewind):        
        print('_wait_rewind')
        while pending:
            rewind()
            done, pending = await asyncio.wait(pending, timeout=1.0/fps, return_when=asyncio.FIRST_EXCEPTION)
            print.widgets(self, h=os.get_terminal_size().lines)
        print('Goodbye')
        

    async def __aexit__(self, exc_type, exc, tb):
        if exc: return self.abort(exc_type, exc, tb)
        await self.wait()


    def abort(self, exc_type, exc, tb):
        for t in self.tasks:
            t.task.cancel()
        self.context = None
        del self.kwargs

