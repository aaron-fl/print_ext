from .borders import Bdr
from .card import Card
from .fill import Fill
from .flex import Flex
from .hr import HR
from .line import Line
from .pretty import pretty
from .pretty_exception import PrettyException
from .printer import Printer
from .flattener import Flattener
from .table import Table, CellDfn
from .text import Text
from . import context

import contextvars

printer_var = contextvars.ContextVar('printer', default=Flattener())

def printer(*args, **kwargs):
    print = printer_var.get()
    return print(*args, stack_offset=1, **kwargs)
