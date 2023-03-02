from .context_cvar import ctx_vars, CallableVar, ObjectAttr, CVar, IntCVar, FloatCVar, BoolCVar, EnumCVar


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


    def __init__(self, parent=None, **kwargs):
        self.ctx_local = {}
        self.children = set()
        self.parent = parent
        if parent != None: parent.children.add(self)
        for k,v in kwargs.items():
            try:
                self.ctx(**{k:v})
            except KeyError:
                pass
        self.changed_size()


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
        vals = (self._ctx_lookup(cvar) for cvar in (cvars[k] for k in keys))
        vals = tuple(v(self) if isinstance(v, CallableVar) else v for v in vals)
        for k, v in set_vals.items():
            cv = cvars[k]
            k = cv.names[0]
            if v != None:
                v = v if isinstance(v, CallableVar) else cv.canon(v)
                self.ctx_local[k] = v
            elif k in self.ctx_local:
                del self.ctx_local[k]
        if set_vals: self.changed_ctx()      
        return None if len(vals) == 0 else vals[0] if len(vals) == 1 else vals


    def changed_ctx(self):
        self.changed_size()
        for child in self.children:
            child.changed_ctx()


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
        if parent!=None and parent.ctx_contains(self) or self.parent != None and id(self.parent) != id(parent):
            el = self.clone(**self.ctx_flatten())
        el.parent = parent
        if parent!=None: parent.children.add(el)
        return el


    def ctx_trace(self):
        cvars = ctx_vars()
        return [{cvars[k]:v for k,v in self.ctx_local.items()}, *self.__class__.ctx_class_trace]


    def clone(self, *args, **kwargs):
        ''' Perform a deep clone of this object.
        '''
        return self.__class__(*args, **kwargs)


    def _ctx_lookup(self, cvar):
        try:
            v = self._ctx_lookup_merge(cvar.merge, cvar.names[0])
        except AttributeError:
            v = self._ctx_lookup_nomerge(cvar.names[0])[0]
        return v #v(self) if isinstance(v, CallableVar) else v


    def _ctx_lookup_nomerge(self, key):
        # No merge needed so just pick the closest value
        try:
            return self.ctx_local[key], True # self object has defined a value
        except KeyError: pass
        # Our object does not define cvar,  Check parent
        try:
            val_src = self.parent._ctx_lookup_nomerge(key)
            if val_src[1]: return val_src # Our parent context is defining a value
            # Check if we have a better default to use
        except AttributeError:
            # Parent may not be defined, or may not be a Context object with ctx_lookup
            val_src = None, None # This is our last ditch effort
        # If our class defines cvar then that is better than the parent's class cvar or None
        return (self.ctx_class.get(key, None), None) or val_src


    def _ctx_lookup_merge(self, merge, key):
        vals = []
        obj = self
        while obj != None:
            vals.insert(0, (obj.ctx_class.get(key, None), obj.ctx_local.get(key, None)))
            try: obj = obj.parent
            except AttributeError: obj = None
        val = None
        for v in vals: val = v[0] if val == None else val if v[0] == None else merge(v[0], val)
        for v in vals: val = v[1] if val == None else val if v[1] == None else merge(v[1], val)
        return val


    def ctx_flatten(self):
        ''' Return a complete dictionary of context variables
        '''
        vals = ((cvar.names[0], self._ctx_lookup(cvar)) for cvar in set(ctx_vars().values()))
        return {k:v for k,v in vals if v != None}
        

    def __getitem__(self, key):
        return self.ctx(key)


    def __setitem__(self, key, val):
        self.ctx(**{key:val})


    def __delitem__(self, key):
        self.ctx(**{key:None})
