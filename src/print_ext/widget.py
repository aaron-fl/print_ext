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

    def __init__(self, *args ,**kwargs):
        super().__init__(*args, **kwargs)


    def flatten(self, w=0, h=0, **kwargs):
        try:
            if not w+h and not kwargs: return self.__cached_flatten
        except AttributeError:
            pass
        rows = self._flatten(w=w, h=h, **kwargs)
        if not w+h and not kwargs: self.__cached_flatten = rows
        return rows


    @property
    def width(self):
        return self.calc_width()


    @property
    def height(self):
        return self.calc_height()


    @cache
    def _width(self):
        return self.calc_width


    @cache
    def _height(self):
        return self.calc_height
     

    def calc_width(self, klass=None):
        flat = list(klass._flatten(self) if klass else self.flatten())
        return flat[0].width if flat else 0


    def calc_height(self, klass=None):
        flat = klass._flatten(self) if klass else self.flatten()
        return len(flat)


    def changed_size(self):
        self._clear__width()
        self._clear__height()
        try:
            del self.__cached_flatten
        except:
            pass
    