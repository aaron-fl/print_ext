from .printer import Printer
from .text import Text
from .table import Table
from .pretty import pretty


class PrettyException(Exception):
    ''' This implements the pretty() method to show a pretty version of the exception.
    
    __str__ and __repr__ return normal, not-pretty, strings.
    '''
    def __init__(self, **kwargs):
        for k,v in kwargs.items(): setattr(self, k, v)


    def __str__(self):
        for line in Printer(ascii=True, color=False).each_line(pretty(self)):
            return str(line)
        else:
            return repr(self)


    def __repr__(self):
        s = f"{self.__class__.__name__}("
        args = [f'{k}={v!r}' for k,v in self.__dict__.items()]
        return s+ ', '.join(args) + ')'


    def pretty(self):
        t = Text(self.__class__.__name__)
        if self.__dict__:
            t('\v',pretty(self.__dict__))
        return t


