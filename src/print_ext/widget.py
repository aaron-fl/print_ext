from .cache import cache
from .context import Context, IntCVar


Context.define(IntCVar('width_nom', 'ww'))
Context.define(IntCVar('width_min', 'wm'))
Context.define(IntCVar('width_max', 'wx'))
Context.define(IntCVar('height_nom', 'hh'))
Context.define(IntCVar('height_min', 'hm'))
Context.define(IntCVar('height_max', 'hx'))


class Widget(Context):
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


    @cache
    def _width(self):
        return self.calc_width


    @cache
    def _height(self):
        return self.calc_height
     

    def calc_width(self, klass=None):
        print(f"calc_width {self.__class__}  {klass}")
        flat = list((klass or self.__class__).flatten(self))
        print([f"{f}{len(f)}" for f in flat])
        return flat[0].width if flat else 0


    def calc_height(self, klass=None):
        return len((klass or self.__class__).flatten(self))


    def changed_size(self):
        self._clear__width()
        self._clear__height()
    