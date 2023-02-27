from .widget import Widget
from .table import Table



def pretty(val):
    if isinstance(val, tuple): return PrettyList(val, '()')
    if isinstance(val, list):  return PrettyList(val, '[]')
    if hasattr(val, 'items'): return PrettyDict(val)
    return val


class PrettyList(Widget):
    def __init__(self, val, paren='[]', **kwargs):
        self.val = val
        self.paren = paren
        super().__init__(**kwargs)

    
    def _flatten(self, w=0, h=0, **kwargs):
        try: self.flatten_count += 1
        except: self.flatten_count = 0

        t = Table(0.0,0,tmpl='kv')
        for i,v in enumerate(self.val):
            t(f'\bdem {self.paren[0]}', i,f'\bdem {self.paren[1]} ', '\t', pretty(v), '\t')
        yield from t.flatten(w=w,h=h,**kwargs)


    def clone(self, **kwargs):
        return self.__class__(self.val, self.paren, **kwargs)



class PrettyDict(Table):
    def __init__(self, val, **kwargs):
        #self.val = val
        kwargs.setdefault('tmpl', 'kv')
        super().__init__(0.0, 0, **kwargs)
        for k,v in val.items():
            self(k, ' ', '\t', pretty(v), '\t')

    
    #def _flatten(self, w=0, h=0, **kwargs):
    #    t = Table(0.0, 0, tmpl='kv')
    # #   for k,v in self.val.items():
    #        t(k,' ', '\t',pretty(v),'\t')
    #    yield from t.flatten(w=w,h=h,**kwargs)
    

    #def clone(self, **kwargs):
    #    return self.__class__(self.val, **kwargs)
