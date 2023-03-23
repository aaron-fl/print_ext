import io
from .stream import StreamPrinter
from .rewinder import Rewinder


class StringRewinder(Rewinder):
    def __init__(self, printer):
        self.stream = printer.stream
        self.pos = self.stream.tell()
        super().__init__(printer)
    

    def __call__(self):
        self.stream.seek(self.pos)
        self.stream.truncate()



class StringPrinter(StreamPrinter):
    Rewinder = StringRewinder

    def __init__(self, *, color=None, **kwargs):
        if self.stream == None: self.stream = io.StringIO()
        self.color = (color != None) and color
        super().__init__(**kwargs)


    def __str__(self):
        return self.stream.getvalue()
