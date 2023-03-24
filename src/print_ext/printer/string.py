import io
from .stream import StreamPrinter
from .rewinder import Rewinder


class StringRewinder(Rewinder):
    def __init__(self, printer):
        super().__init__(printer)
        self.pos = self.printer.stream.tell()
    

    def __call__(self):
        self.printer.stream.seek(self.pos)
        self.printer.stream.truncate(self.printer.stream.tell())



class StringPrinter(StreamPrinter):
    Rewinder = StringRewinder

    def __init__(self, **kwargs):
        kwargs.setdefault('stream', io.StringIO())
        kwargs.setdefault('color', False)
        super().__init__(**kwargs)


    def __str__(self):
        return self.stream.getvalue()
