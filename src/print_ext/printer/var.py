import contextvars
from .stream import StreamPrinter

printer_var = contextvars.ContextVar('printer', default=StreamPrinter())

def printer(*args, **kwargs):
    ''' A contextually aware Printer.
    '''
    print = printer_var.get()
    return print(*args, loc=1, **kwargs)
