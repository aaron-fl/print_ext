from functools import reduce
from .context import Context, IntCVar, ObjectAttr

INFINITY = 1000000000000

Context.define(IntCVar('width_nom', 'ww'))
Context.define(IntCVar('width_min', 'wm'))
Context.define(IntCVar('width_max', 'wx'))
Context.define(IntCVar('height_nom', 'hh'))
Context.define(IntCVar('height_min', 'hm'))
Context.define(IntCVar('height_max', 'hx'))



class Widget(Context, width_nom=ObjectAttr('width', None), height_nom=ObjectAttr('height', None)):
    ''' The obligatory widget; Generic ancestor to all things flattenable.

    This is an abstract base class for all things that draw to a rectangle.
    '''

    def __init__(self, *args ,**kwargs):
        super().__init__(*args, **kwargs)


    def __bool__(self):
        return bool(self.height)


    @property
    def width(self):
        return self.calc_width()


    @property
    def height(self):
        return self.calc_height()


    def calc_width(self):
        return reduce(lambda a, line: max(a, line.width), self.flatten(), 0)


    def calc_height(self, klass=None):
        return reduce(lambda a, _: a+1, self.flatten(), 0)
        

    def changed_size(self):
        self.__width = None
        #self._clear__width()
        #self._clear__height()
    