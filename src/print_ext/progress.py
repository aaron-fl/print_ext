from print_ext.line import Line
from print_ext.context import Context
from print_ext.widget import Widget


class Bar(Widget):
    def __init__(self, chars=None, steps=1, **kwargs):
        self.i = 0
        self.steps = steps
        super().__init__(**kwargs)
        self.chars = chars or ('#-' if self['ascii'] else '━┄')
        

    def calc_width(self):
        return 35
    

    def calc_height(self):
        return 1


    def step(self, pct=None):
        self.i = (self.i+1) if pct == None else min(max(0, pct*self.steps), self.steps)


    def flatten(self, w=0, h=0, **kwargs):
        w = w or 30
        nleft = min(int(self.i * w / self.steps), w)
        return [Line(parent=self).insert(0,self.chars[0]*nleft).insert(-1,self.chars[1]*(w-nleft), style=';.')]



class Spinner(Bar):

    def __init__(self, chars=None, **kwargs):
        super().__init__(**kwargs)
        self.chars = chars or '/-\\|'
        

    def calc_width(self):
        return 3
 

    def flatten(self, w=0, h=0, **kwargs):
        i = int(self.i)%len(self.chars)
        w = w or 1
        return [Line(parent=self).insert(0,' ' + self.chars[i])]



class Progress(Context):
    def __init__(self, fn=None, steps=0, *, parent, **kwargs):
        kwargs.setdefault('style','1')
        self.fn = fn
        self.prev_width = 0
        super().__init__(parent=parent)
        self.bar = Bar(steps=steps, parent=self, **kwargs) if steps else Spinner(parent=self, **kwargs)
       

    def __call__(self, *args, done=False, style=None, **kwargs):
        self.bar.step()
        done = done or not self.parent.isatty
        #print(f'bar {self.bar!r}')
        line = Line(*args, parent=self, **kwargs)
        if not done or not isinstance(self.bar, Spinner):
            line.insert(0,' ').insert(0, self.bar, style=style).insert(0, ' ')
        txt = self.parent.format_out(*line.styled())
        pad = self.prev_width - line.width
        pad = ' '*pad if pad > 0 else ''
        self.prev_width = line.width+1
        self.parent.stream.write(txt + pad + ('\n' if done else '\r'))

