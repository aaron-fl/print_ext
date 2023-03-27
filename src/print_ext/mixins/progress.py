import random
from ..context import Context, IntCVar
from ..widget import Widget, INFINITY
from ..line import Line
from .tail import Tail

Context.define(IntCVar('collapse_when_done'))


class Progress(Tail, Widget, collapse_when_done=1):
    ''' Print the tail with some kind of progress indicator based on the tag's `progress` value
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__progress = (0,0,'')
        self.status_style = {'done':'g!', 'err':'err', '':'1'}
        self._spinner_i = random.randrange(4) # So spinners don't look synced


    def set_progress(self, g=None):
        if g == None: return self.__progress
        if isinstance(g, str):
            if g.lower() == 'done':
                g = (self.__progress[1], self.__progress[1], 'done')
            else:
                g = (self.__progress[0], self.__progress[1], g)
        elif isinstance(g, tuple):
            if len(g) < 3:
                if len(g) != 2: raise ValueError(f"Invalid progress tag: {g}")
                g = (*g, 'done' if g[0]==g[1] else self.__progress[2])
        elif isinstance(g, float):
            g = (max(0.0, min(g, 0.9999)), 1.0, self.__progress[2])
        else:
            raise ValueError(f"Invalid progress tag: {g}")
        self.__progress = g
        return self.__progress


    def append(self, widget, tag):
        if g := tag.get('progress', None): self.set_progress(g)
        super().append(widget, tag)


    def calc_height(self):
        h = self['height_max'] or 0
        if self.__progress[2] == 'done': h = self['collapse_when_done'] or h
        return min(h, self.height_visible())


    def spinner(self):
        if self.__progress[2] == 'done': return '*'
        if self.__progress[2]: return '!'
        self._spinner_i += 1
        return '|/-\\'[self._spinner_i%4]


    def bar(self, w):
        ascii = self['ascii']
        pct = self.__progress[0] / float(self.__progress[1])
        if w < 16: bar = self.spinner() if ascii or self.__progress[2] else ' ▁▂▃▄▅▆▇█'[int(pct*9)]
        if w < 4: return self.spinner()
        if w < 12: return '100%' if self.__progress[2]=='done' else f'{bar}{int(pct*100):2d}%'
        # longer bar
        chars = '=-' if ascii else '━┄'
        barw = w-4 if w < 20 else w
        bar = chars[0]*int(pct*barw) + chars[1]*(barw-int(pct*barw))
        return f"{int(pct*100):3d}%{bar}" if w < 20 else bar
        

    def flatten_one(self, w=0, h=0, **kwargs):
        name = Line(style='2').insert(0, self.name or '')
        name_w = name.width
        bar = self.bar(30 if w==0 else min(w,30,max(4, w-name_w-1))) if self.__progress[1] else self.spinner()
        line = Line()(bar,style=self.status_style.get(self.__progress[2],'err'))
        if len(bar) == w: return [line]
        if len(bar) == w-1: return [line(' ')]
        if w and len(bar)+2+name_w >= w: return [line(' ', name.justify(w and w-len(bar)-1))]
        if self.__progress[2] and self.__progress[2] != 'done':
            tail = [Line(self.__progress[2], style=self.status_style['err'])]
        elif h:
            tail = []
        else:
            tail = list(super().flatten(h=1, **kwargs))
        tail = tail[0] if tail else Line()
        if w == 0: return [line(' ', name, ' ', tail)]
        return [line(' ', name, ' ', tail.justify(w-len(bar)-2-name_w))]
      
    
    def flatten(self, w=0, h=0, **kwargs):
        my_h = h or self.height
        my_w = w or self['width_max'] or 0
        if my_w == INFINITY: my_w = 0
        if my_h == 1:
            yield from self.flatten_one(my_w, 0, **kwargs)
            return
        yield from self.flatten_one(my_w, 1, **kwargs)
        i = 1
        for line in super().flatten(my_w, my_h, **kwargs):
            yield line
            i += 1
        if not h: return
        while (i:=i+1) <= my_h:
            yield Line(parent=self)



class ProgressRewind(Progress):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rewind = None


    def append(self, widget, tag):
        super().append(widget, tag)
        if self._rewind:
            g = self.set_progress()
            self.parent.append(self, tag={'progress':g})
            if g[2] != 'done': self._rewind()
        else:
            self.parent.append(widget, tag)


    def __enter__(self):
        assert(not self._rewind)
        if self.parent.Rewinder:
            self._rewind = self.parent.rewind()
            self._rewind.__enter__()
        return self


    def __exit__(self, *args):
        if self._rewind:
            self._rewind.__exit__(*args)
            self._rewind = None
