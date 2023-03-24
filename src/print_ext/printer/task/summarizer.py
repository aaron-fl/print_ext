from functools import reduce
from ...context import Context
from ...line import Line, Just


class Summarizer(Context):

    def __getattr__(self, attr):
        return getattr(self.parent, attr)


    def calc_width(self):
        return reduce(lambda a, w: max(a,w.width), self._widgets, 0)


    def calc_height(self):
        return min((self['height_max'] if self.status() else self['collapse_when_done']), self.printer.height_visible())


    def spinner(self, status):
        if status == 0: return '*'
        if status == 1: return '!'
        self._spinner_i += 1
        return '|/-\\'[self._spinner_i%4]


    def bar(self, w, status, pct):
        ascii = self['ascii']
        if w < 16: bar = self.spinner(status) if ascii or status<2 else ' ▁▂▃▄▅▆▇█'[int(pct*9)]
        if w < 4: return self.spinner(status)
        if w < 12: return f'{bar}{int(pct*100):2d}%' if status else '100%'
        # longer bar
        chars = '=-' if ascii else '━┄'
        barw = w-4 if w < 20 else w
        bar = chars[0]*int(pct*barw) + chars[1]*(barw-int(pct*barw))
        return f"{int(pct*100):3d}%{bar}" if w < 20 else bar
        

    def flatten_one(self, w=0, h=0, **kwargs):
        name = Line(style='2').insert(0, self.name)
        name_w = name.width
        status = self.status()
        pct = self.progress_pct(status)
        bar = self.spinner(status) if pct < 0 else self.bar(30 if w==0 else min(w,30,max(4, w-name_w-1)), status, pct)
        line = Line()(bar,style=self.status_style[status])
        if len(bar) == w: return [line]
        if len(bar) == w-1: return [line(' ')]
        if h or w and len(bar)+2+name_w >= w: return [line(' ', name.justify(w and w-len(bar)-1))]
        tail = list(self.flatten_tail(h=1, **kwargs))[0]
        if w == 0: return [line(' ', name, ' ', tail)]
        return [line(' ', name, ' ', tail.justify(w-len(bar)-2-name_w))]
      
    
    def flatten_tail(self, w=0, h=0, **kwargs):
        tail, tail_len = [], 0
        for widget, _ in reversed(self._widgets):
            lines = list(widget.flatten(w=w, **kwargs))
            tail[:0] = lines[-(h-tail_len):]
            tail_len = len(tail)
            if tail_len == h: break
        return tail


    def flatten(self, w=0, h=0, **kwargs):
        my_h = h or self.calc_height()
        if my_h == 1:
            yield from self.flatten_one(w, 0, **kwargs)
            return
        yield from self.flatten_one(w, 1, **kwargs)
        i = 1
        for line in self.flatten_tail(w-w, h=my_h-1):
            yield line
            i += 1
        #if not h: return
        while (i:=i+1) <= my_h:
            yield Line(parent=self)
