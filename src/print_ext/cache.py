import types


class _CacheDecorator():
    def __init__(self, fn):
        self.fn = fn
        
    def __set_name__(self, owner, name):
        fn = self.fn.fget if isinstance(self.fn, property) else self.fn
        def _get(s, *args, **kwargs):
            try:
                return s._cache[name]
            except KeyError:
                v = fn(s, *args, **kwargs)
                s._cache[name] = v
                return v

        def _clear(s):
            if name in s._cache: del s._cache[name]

        setattr(owner, f'_clear_{name}', _clear)
        if isinstance(self.fn, property):
            setattr(owner, name, property(_get).setter(self.fn.fset).deleter(self.fn.fdel))
        elif isinstance(self.fn, types.FunctionType):
            setattr(owner, name, _get)
        else:
            raise ValueError(f"Can't cache '{name}' of type '{type(self.fn)}' on class '{owner}'")
        if not hasattr(owner, '_has_cache'):
            super_init = owner.__init__
            def _init(self, *args, **kwargs):
                self.__dict__['_cache'] = {}
                super_init(self, *args, **kwargs)  
            setattr(owner, '__init__', _init)
            owner._has_cache = True
        

    def __getattr__(self, attr):     
        def _f(*args, **kwargs):
            self.fn = getattr(self.fn, attr)(*args, **kwargs)
            return self
        return _f
        

def cache(fn):
    return _CacheDecorator(fn)
