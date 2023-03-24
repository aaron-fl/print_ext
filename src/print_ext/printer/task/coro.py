from asyncio import InvalidStateError, create_task
from .task import TaskPrinter


class CoroTaskPrinter(TaskPrinter):
    def __init__(self, coro, **kwargs):
        super().__init__(**kwargs)
        self._coro = (coro, self.name)
        try:
            self.ensure_tasks_running()
        except RuntimeError:
            pass # we can start them later, when an event loop is running


    def ensure_tasks_running(self):
        if not hasattr(self, '_coro'): return
        self.tasks.append(self.context.run(lambda: create_task(self._coro[0], name=self._coro[1])))
        if not self.name: self.name = self.tasks[0].get_name()
        del self._coro
    

    def status(self):
        try:
            self.tasks[0].exception()
        except InvalidStateError:
            return 2
        except Exception as e:
            self.exception = e
            return 1
        return 0


from ..printer import printer_var
