from .task import TaskPrinter

class ProgressTaskPrinter(TaskPrinter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rewind = None


    def append(self, widget, tag):
        if not super().append(widget, tag): return
        self.printer.widgets(self)
        if self.status():
            self._rewind()


    def _sub_append(self, widget, tag, task):
        raise NotImplementedError()


    def __enter__(self):
        assert(not self._rewind)
        if not self.capture: return self
        self._rewind = self.printer.rewind()
        self._rewind.__enter__()
        return self


    def __exit__(self, *args):
        if not self.capture: return
        self._rewind.__exit__(*args)
        self._rewind = None
