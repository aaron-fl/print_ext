import io

def oid(obj):
    return 'None' if obj==None else str(hex(id(obj)))[-4:]

def ostr(obj):
    return f'<{obj.__class__.__name__}#{oid(obj)}> '


def print_ctx_trace(obj, to_parent=None):
    o = obj
    while o != None and o != to_parent:
        line = ('' if obj == o else '  -> ') + ostr(o) + ' '
        for trace in o.ctx_trace():
            line += ', '.join(f'{k.names[0]}={v}' for k,v in trace.items()) + ' -- '
        print(line)
        o = o.parent




def context_info(obj, parent=None):
    def _s(o):
        if o == None or o == parent: return ''
        style = ' '.join(f'{k}:{repr(v)}' for k,v in o.ctx_local.items()) if hasattr(o, 'ctx_local') else ''
        if hasattr(o, 'parent'):
            return f"{style} {'' if o.parent==None else ostr(o.parent)}  {_s(o.parent)}"
        return f'{style}'
    return _s(obj)



def ostr_ctx(obj, parent=None):
    return f'{ostr(obj)} {context_info(obj, parent)}'


def debug_dump(obj, parent=None, depth=0):
    s = ['  '*depth + ostr_ctx(obj, parent) + f' ---{obj}---']
    for sub in obj.each_child() if hasattr(obj,'each_child') else []:
        s += debug_dump(sub, obj, depth + 1)
    return s



def flat(widget, **kwargs):
    return [r.styled()[0] for r in widget.flatten(**kwargs)]


def styled(widget, **kwargs):
    return [r.styled() for r in widget.flatten(**kwargs)]


def printer(**kwargs):
    from print_ext.printer import Printer
    o = io.StringIO()
    p = Printer(stream=o, **kwargs)
    return o,p
   
