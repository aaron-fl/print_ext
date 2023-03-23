from .printer import StringPrinter
from .text import Text
from .table import Table


class PrettyException(Exception):
    ''' This implements the pretty() method to show a pretty version of the exception.
    
    __str__ and __repr__ return normal, not-pretty, strings.
    '''
    def __init__(self, **kwargs):
        for k,v in kwargs.items(): setattr(self, k, v)


    def __str__(self):
        print = StringPrinter(ascii=True, color=False)
        if hasattr(self, 'msg'):
            print(self.msg)
        else:
            print(repr(self))
        return str(print).rstrip()


    def __repr__(self):
        s = f"{self.__class__.__name__}("
        args = [f'{k}={v!r}' for k,v in self.__dict__.items()]
        return s+ ', '.join(args) + ')'


    def __pretty__(self, print, **kwargs):
        if hasattr(self, 'msg'):
            print(self.msg)
        else:
            print(self.__class__.__name__)
        vars = {k:v for k,v in self.__dict__.items() if k != 'msg'}
        if vars: print.pretty(vars, pad=-1, **kwargs)
