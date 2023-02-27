from .context_cvar import ctx_vars, CallableVar, ObjectAttr, CVar, IntCVar, FloatCVar, BoolCVar, EnumCVar
from tests.testutil import ostr


class MetaContext(type):
    def __new__(self, name, bases, attrs, **kwargs):
        cls = super().__new__(self, name, bases, attrs)
        try:
            cls.ctx_class = dict(cls.__mro__[1].ctx_class)
            cls.ctx_class_trace = list(cls.__mro__[1].ctx_class_trace)
        except:
            cls.ctx_class = {}
            cls.ctx_class_trace = []
        cvars = ctx_vars()
        cls.ctx_class_trace.insert(0, {cvars[k]:v if isinstance(v, CallableVar) else cvars[k].canon(v) for k,v in kwargs.items()})
        for cv,v in cls.ctx_class_trace[0].items():
            if hasattr(cv, 'merge') and cv.names[0] in cls.ctx_class:
                v = cv.merge(v, cls.ctx_class[cv.names[0]])
            cls.ctx_class[cv.names[0]] = v
        return cls



class Context(metaclass=MetaContext):
    ''' 
    The lookup for a context variable
     1. defined on self
     2. defined in a parent
     3. defined in ctx_defaults
     4. defined in a parent's ctx_defaults
     5. None

    A context object might want to live in two places at once::

        obj = Bob()
        Cob(obj)
        Bill(obj)
        obj['x'] == ???

    Or you might create loops::

        a = Apple()
        b = Ball()
        a(b)
        b(a)
    '''


    #@classmethod
    #def defaults(self, **kwargs):
    #    print(f"DEFAULTS {self}  {kwargs}")
    #    def _f(cls):
    #        cvars = ctx_vars()
    #        cls._clsctx = {cvars[k].names[0]: v if isinstance(v, CallableVar) else cvars[k].canon(v)  for k,v in kwargs.items()}
    #        return cls
    #    return _f


    @classmethod
    def define(self, cvar):
        cvars = ctx_vars()
        for name in cvar.names:
            if name not in cvars:
                cvars[name] = cvar
            elif cvar != cvars[name]:
                raise ValueError(f"Can't register the duplicate name '{name}'\nCurrent: {cvars[name]}\nTrying to register: {cvar}")
        return cvar


    #@classmethod
    #def _ctx_lookup_class(self, cvar):
    #    return self.ctx_class.get(cvar.names[0], None), False
        #key = cvar.names[0]
        #for cls in self.__mro__:
        #    try: return cls.ctx_defaults[key], cls
        #    except (AttributeError, KeyError): continue


    def __init__(self, parent=None, **kwargs):
        self.ctx_local = {}
        self.ctx_cache = {}
        self.children = set()
        self.parent = parent
        if parent != None: parent.children.add(self)
        self.ctx(**kwargs)


    def ctx(self, *keys, **set_vals):
        ''' get/set/delete context variables on this object

        If you want to override __getitem__/__setitem__ to do other things then you can use this method to access the context.

        Parameters:
            *keys (str,)
                Key names to lookup.  They may be aliases.
            **set_vals
                Set these values on this object.  If the key is also defined in ``keys`` then
                the previous value will also be returned.
                
                Setting a key to None clears the value from self.

        Returns:
            A tuple of values, one for each key in ``*keys``.

        Raises:
            KeyError
                A key name has not been defined with ``Context.define()``
        '''
        cvars = ctx_vars()
        vals = tuple(v(self) if isinstance(v,CallableVar) else v for v in (self.ctx_lookup(cvars[k])[0] for k in keys))
        for k, v in set_vals.items():
            cv = cvars[k]
            k = cv.names[0]
            if v != None:
                v = v if isinstance(v, CallableVar) else cv.canon(v)
                self.ctx_local[k] = v
            elif k in self.ctx_local:
                del self.ctx_local[k]
            self.clear_ctx_cache(k)
        return None if len(vals) == 0 else vals[0] if len(vals) == 1 else vals


    def clear_ctx_cache(self, k):
        #print(f'Clear Cache {k}')
        self.changed_size()
        #try: del self.ctx_cache_flatten
        #except: pass
        if k in self.ctx_cache: del self.ctx_cache[k]
        for child in self.children:
            child.clear_ctx_cache(k)


    def changed_size(self):
        pass


    def each_child(self):
        yield from []


    def ctx_contains(self, other):
        ctx = self
        while ctx != None:
            if id(ctx) == id(other): return True
            ctx = ctx.parent
        return False


    def ctx_parent(self, parent):
        el = self
        if parent.ctx_contains(self) or self.parent != None and id(self.parent) != id(parent):
            el = self.clone(**self.ctx_flatten())
        el.parent = parent
        parent.children.add(el)
        return el


    def ctx_trace(self):
        cvars = ctx_vars()
        return [{cvars[k]:v for k,v in self.ctx_local.items()}, *self.__class__.ctx_class_trace]


    def clone(self, *args, **kwargs):
        ''' Perform a deep clone of this object.
        '''
        return self.__class__(*args, **kwargs)


    def ctx_lookup(self, cvar):
        k = cvar.names[0]
        if k not in self.ctx_cache:
            self.ctx_cache[k] = self._ctx_lookup(cvar)
        return self.ctx_cache[k]


    def _ctx_lookup(self, cvar):
        ''' Lookup a single cvar on this object
        
        Returns:
            A tuple (value, defining_object)
        '''
        if hasattr(cvar, 'merge'): return self._ctx_lookup_merge(cvar), True
        # No merge needed so just pick the closest value
        if (k:=cvar.names[0]) in self.ctx_local:
            return self.ctx_local[k], True # self object has defined a value
        # Our object does not define cvar,  Check parent
        try:
            val_src = self.parent.ctx_lookup(cvar)
            if val_src[1]: return val_src # Our parent context is defining a value
            # Check if we have a better default to use
        except AttributeError:
            # Parent may not be defined, or may not be a Context object with ctx_lookup
            val_src = None, False # This is our last ditch effort
        # If our class defines cvar then that is better than the parent's class cvar or None
        return (self.ctx_class.get(cvar.names[0], None), False) or val_src


    def ctx_lookup_self(self, cvar):
        return self.ctx_class.get(cvar.names[0], None), self.ctx_local.get(cvar.names[0], None)


    def _ctx_lookup_merge(self, cvar):
        vals = []
        obj = self
        while obj != None:
            vals.insert(0, obj.ctx_lookup_self(cvar))
            try: obj = obj.parent
            except AttributeError: obj = None
        val = None
        for v in vals: val = v[0] if val == None else val if v[0] == None else cvar.merge(v[0], val)
        for v in vals: val = v[1] if val == None else val if v[1] == None else cvar.merge(v[1], val)
        return val


    def ctx_flatten(self):
        try:
            return self.ctx_cache_flatten
        except AttributeError:
            self.ctx_cache_flatten = self._ctx_flatten()
            return self.ctx_cache_flatten


    def ctx_flatten(self):
        ''' Return a complete dictionary of context variables
        '''
        ctx = {}
        for cvar in set(ctx_vars().values()):
            val, _ = self.ctx_lookup(cvar)
            if val == None: continue
            ctx[cvar.names[0]] = val
        return ctx
    

    def __getitem__(self, key):
        return self.ctx(key)


    def __setitem__(self, key, val):
        self.ctx(**{key:val})


    def __delitem__(self, key):
        self.ctx(**{key:None})
