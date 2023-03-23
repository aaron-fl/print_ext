from .stream import StreamPrinter

class OnewayPrinter(StreamPrinter):
    def rewind(self):
        raise AttributeError()
