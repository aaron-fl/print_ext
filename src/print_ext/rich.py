from functools import reduce
from .context import Context, CVar
from .cache import cache
from .widget import Widget


class ProxyContext(Context):
    def __init__(self, eoc=True, **kwargs):
        self.eoc = eoc
        super().__init__(**kwargs)

    def is_empty(self):
        return not self.ctx_local and (not self.parent or self.parent.is_empty())

    def ctx_flatten(self):
        return {} if self.is_empty() else super().ctx_flatten()

        

class LangCVar(CVar):
    def canon(self, val):
        if isinstance(val, str):
            return tuple((val.lower()+'___').split('_')[:3])
        return val

Context.define(LangCVar('lang'))



class Rich(Widget):
    ''' This is a mixin for adding rich-text parsing capabilities via the __call__ method.

    :Special characters:
        \\b
            Put an attribute on the stack.
            `\\b<key>=<value><auto-pop>`

            `\\b=R`   This gets auto-popped at the end of the call
            `\\b=y$`  This gets auto-popped at the end of the string
            `\\b=r!`  This doesn't get auto-popped.  Pop it manually with 
            `\\b=`    Pop an attribute.  It is ok to pop too many times.

        \\v
            If a string contains \\n then it is first processed with cleandoc() which removes
            preceeding whitespace and common whitespace on each line.  \\v dosen't trigger
            this logic and gets replaced as \\n

        \\t
            Triggers a move to the next 'cell'.  The meaning of 'cell' is defined by the baseclass.

        \\f
            Separate language versions
            \\f<lang>_<region>_<dialect>

            Region and dialect are optional.  The best language match will be selected.
            
    :Usage:
        Subclass this and then implement the following methods as a state machine.
            rich_append(el)
                el will be flattenable
            rich_newline()
                This is optional.  By default throws.
            rich_tab()
                This is optional.  By default throws.
    '''

    def __init__(self, *args, **kwargs):
        self.rich_stream = []
        super().__init__(**kwargs)
        self(*args)


    def __call__(self, *els, **kwargs):
        return self.append(*els, **kwargs)


    def append(self, *els, **kwargs):
        ''' Add any kind of element to this.

        If el is a str then it is parsed as rich-text. (b,f,t,v escape codes)
        If it is a Context object, then it is added as is.
        Otherwise, turn it into a Line() and add that.
        '''
        self.ctx_cur = ProxyContext(**kwargs)
        for el in els:
            if isinstance(el, str):
                lines = _unindent(el).replace('\v','\n').split('\n') # FIXME: Removed self.__l10n(el)
                self.__append_line(lines[0])
                for line in lines[1:]:
                    self.rich_newline(self.ctx_cur.ctx_flatten())
                    self.__append_line(line)
                while self.__pop(False): pass # Pop end-of-string
            elif isinstance(el, Context):
                self.rich_append(el, self.ctx_cur.ctx_flatten())
            else:
                self.rich_append(str(el), self.ctx_cur.ctx_flatten())
        self.changed_size()
        return self


    def __append_line(self, line):
        tabs = line.split('\t')
        self.__append_tab(tabs[0])
        for tab in tabs[1:]:
            self.rich_tab(self.ctx_cur.ctx_flatten())
            self.__append_tab(tab)
    

    def __append_tab(self, tab):
        parts = tab.split('\b')
        if parts[0]: self.rich_append(parts[0], self.ctx_cur.ctx_flatten())
        for part in parts[1:]:
            part = part.split(' ',1)
            eoc = part[0].endswith('$')
            part, txt = part[0][:-1] if eoc else part[0], (part[1] if len(part) > 1 else '')
            if part:
                part = part.split('=')
                kwargs = {'':part[0]} if len(part) == 1 else {part[0]:part[1]}
                self.ctx_cur = ProxyContext(eoc=eoc, parent=self.ctx_cur, **kwargs)
            else: # empty \b
                self.__pop(eoc)
            if txt: self.rich_append(txt, self.ctx_cur.ctx_flatten())


    def __pop(self, eoc):
        pctx, ctx = None, self.ctx_cur
        while ctx.parent and ctx.eoc != eoc:
            pctx, ctx = ctx, ctx.parent
        if not ctx.parent: return False
        if pctx:
            pctx.parent = ctx.parent
        else:
            self.ctx_cur = ctx.parent
        return True


    def __l10n(self, txt):
        vers = txt.split('\f')
        best = (vers[0], 0.5)
        glang = self['lang'] or ('','','')
        for ver in vers[1:]:
            try:
                lang, ver = ver.split(' ',1)
            except Exception as e:
                raise ValueError(f"Invalid \\f usage '{ver}'\nExample: '\\fen_us color\\fen_gb colour'")
            slang = (lang.lower()+'___').split('_')[:3]
            
            m = 0 if slang[0] != glang[0] else\
                1 if slang[1] != glang[1] else\
                2 if slang[2] != glang[2] else\
                3
            m += reduce(lambda a,x: a + (0.0 if x else 0.1), slang, 0)
            if m > best[1]: best = (ver, m)
        return best[0]


    def rich_append(self, el, ctx):
        try:
            el = el.ctx_parent(self)
        except AttributeError:
            pass
        self.rich_stream.append((el,ctx))
        

    def rich_newline(self, ctx):
        self.rich_stream.append(('\v',ctx))
    

    def rich_tab(self, ctx):
        self.rich_stream.append(('\t',ctx))

    

def _unindent(txt):
    if '\n' not in txt: return txt
    newlines = txt.splitlines()
    indent = ''
    for line in newlines[1:]: # The first line is skipped because it starts right after the opening '''
        stripped = line.lstrip()
        if stripped: # First non-blank line sets the indentation level
            indent = line[:len(line)-len(stripped)]
            break
    n_indent = len(indent)
    if indent: newlines = [l[n_indent:] if l.startswith(indent) else l for l in newlines]
    while newlines and not newlines[-1].strip(): newlines = newlines[:-1]
    return '\n'.join(newlines).lstrip()
