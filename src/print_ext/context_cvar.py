from threading import current_thread


def ctx_vars(reset=False):
    ''' These can't be tied to any particular object and must be consistant throughout the program
    '''
    try:
        assert(not reset)
        return current_thread()._ctx_vars_231174
    except:
        vars = {}
        current_thread()._ctx_vars_231174 = vars
        return vars



class CallableVar():
    pass



class ObjectAttr(CallableVar):
    def __init__(self, attr, default=None):
        self.attr = attr
        self.default = default

    def __call__(self, obj):
        try: return getattr(obj, self.attr)
        except AttributeError: return self.default



class CVar():
    ''' This is the prototype/class for a context variable.
    These get registered and must be uniuqe. i.e. 'style' can mean only
    one thing in the program
    '''
    def __init__(self, *names):
        self.names = tuple([names[0]] + sorted(names[1:]))


    def __hash__(self):
        return hash(self.names)

    
    def __eq__(self, other):
        return self.names == other.names


    def __repr__(self):
        return f"{self.__class__.__name__}({','.join(map(repr,self.names))})"


    def canon(self, sval):
        ''' Convert from *any* representation of the value to the canonical value.

        The value will never be ``None``.
        '''
        return sval



class IntCVar(CVar):
    def canon(self, sval):
        return int(sval) 


class FloatCVar(CVar):
    def canon(self, sval):
        return float(sval) 


class BoolCVar(CVar):
    def canon(self, sval):
        if not isinstance(sval, str): return bool(sval)
        return sval.lower().strip() not in ['', 'f','false','off','no','0']


class EnumCVar(CVar):
    def __init__(self, *args, options):
        super().__init__(*args)
        self.options = options

    def canon(self, sval):
        if sval not in self.options: raise ValueError(f"EnumCvar value {sval!r} not in {self.options!r}")
        return sval
    