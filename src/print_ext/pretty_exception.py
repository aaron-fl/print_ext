from .printer import Flattener
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
        w = self.msg if hasattr(self, 'msg') else pretty(self)
        return Flattener(ascii=True, color=False).to_str(w).rstrip()


    def __repr__(self):
        s = f"{self.__class__.__name__}("
        args = [f'{k}={v!r}' for k,v in self.__dict__.items()]
        return s+ ', '.join(args) + ')'


    def pretty(self):
        msg = (': ', self.msg) if hasattr(self, 'msg') else ('', )
        t = Text(self.__class__.__name__, *msg)
        if self.__dict__:
            t('\n',pretty({k:v for k,v in self.__dict__.items() if k != 'msg'}))
        return t


