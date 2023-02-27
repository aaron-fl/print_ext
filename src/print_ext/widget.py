from .cache import cache
from .context import Context, IntCVar, ObjectAttr


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

    def flatten(self, w=0, h=0, **kwargs):
        return []


    @property
    def width(self):
        return self.calc_width()


    @property
    def height(self):
        return self.calc_height()


    def calc_width(self, klass=None):
        flat = list((klass or self.__class__).flatten(self))
        return flat[0].width if flat else 0


    def calc_height(self, klass=None):
        return len((klass or self.__class__).flatten(self))


    def changed_size(self):
        pass
        #self._clear__width()
        #self._clear__height()
    