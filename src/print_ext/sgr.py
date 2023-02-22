import re
from functools import reduce

class SGR():
    ''' Set Graphics Rendition

    String codes:
      ``0`` reset
      ``krgybmcw``  foreground color (blacK, Red, Green, Yellow, Blue, Magenta, Cyan, White)
      ``^krgybmcw`` Background color
      ``!`` / ``.`` Bold / Normal
      ``;`` / ``,`` Dim / Normal
      ``_`` / ``~`` underscore / No underscore
    '''
    __props__ = ('flags',)

    flags = ['fg','bg','bold','dim','ul']

    RE = re.compile(r'^(0)|(([krgybmcw]?)(\^([krgybmcw]))?([,;.!~_]*))$')

    def __init__(self, sval='', flags=None):
        if flags != None:
            self.flags = flags
            return
        # Init from a string
        m = SGR.RE.match(sval)
        if not m: raise ValueError(f"Invalid SGR value {sval!r}")
        self.flags = {}
        for v in m[6] or []:
            for k, g in {'dim':',;', 'ul':'~_', 'bold':'!.'}.items():
                if v in g:
                    if k in self.flags:
                        raise ValueError(f"Invalid SGR value {sval!r}. Can't set flag '{v}' because it is already set to '{self.flags[k]}'.")
                    self.flags[k] = v
        if m[3]: self.flags['fg'] = 30 + 'krgybmcw'.index(m[3])
        if m[4]: self.flags['bg'] = 40 + 'krgybmcw'.index(m[5])


    def __add__(self, other):
        if not (self and other): return other
        flags = dict(self.flags)
        flags.update(other.flags)
        return SGR(flags=flags)
    

    def __bool__(self):
        return bool(self.flags)
        

    def __getitem__(self, k):
        return self.flags.get(k,'')


    def diff(self, other=None):
        ''' other -> self '''
        other = other or SGR()
        codes = []
        if not self: return '\033[0m' if other else ''
        reset = (self['fg'] == '' and other['fg']) or (self['bg'] == '' and other['bg']) or (other['ul']=='_' and other['ul'] != self['ul']) or (other['dim']==';' and other['dim'] != self['dim']) or (other['bold']=='!' and other['bold'] != self['bold'])
        if self['bold'] == '!' and (reset or self['bold'] != other['bold']): codes.append(1)
        if self['dim'] == ';' and (reset or self['dim'] != other['dim']): codes.append(2)
        if self['ul'] == '_' and (reset or self['ul'] != other['ul']): codes.append(4)
        if self['fg'] and (reset or self['fg'] != other['fg']): codes.append(self['fg'])
        if self['bg'] and (reset or self['bg'] != other['bg']): codes.append(self['bg'])
        if reset: codes.insert(0,0)
        #print(f" other: {other.flags}  ->  self: {self.flags}  codes:{codes}")
        return '\033[' + ';'.join(map(str,codes)) + 'm'


    def __hash__(self):
        return reduce(lambda h, f: h ^ hash(self.flags.get(f,'')), SGR.flags)


    def __eq__(self, other):
        return all(other.flags.get(f,'') == self.flags.get(f,'') for f in SGR.flags)


    def __str__(self):
        s = ''
        if not self: return '0'
        if 'fg' in self.flags: s += 'krgybmcw'[self.flags['fg']-30]
        if 'bg' in self.flags: s += '^'+'krgybmcw'[self.flags['bg']-40]
        return s + ''.join(self.flags.get(k,'') for k in SGR.flags[2:])


    def __repr__(self):
        return f"SGR('{self}')"
