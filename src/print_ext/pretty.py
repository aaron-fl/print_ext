import functools, traceback
from contextlib import suppress
from .table import Table
from .text import Text


class Continue(Exception):pass

def pretty(val, depth=-1, _depth=0, quote=False, **kwargs):
    if depth == 0: return repr(val)
    if isinstance(val, bytes): return repr(val)
    if isinstance(val, str): return Text(val) if not quote and (q:=val.strip()) and q==val else repr(val)
    kwargs['quote'] = quote
    with suppress(Continue): return _pretty_pretty(val, _depth, depth, **kwargs)
    with suppress(Continue): return _pretty_tuple(val, _depth, depth, **kwargs)
    with suppress(Continue): return _pretty_list(val, _depth, depth, **kwargs)
    with suppress(Continue): return _pretty_dict(val, _depth, depth, **kwargs)
    with suppress(Continue): return _pretty_iter(val, _depth, depth, **kwargs)
    return repr(val)



def _pretty_pretty(val, _depth, depth, **kwargs):
    try:
        return functools.partial(val.__pretty__, _depth=_depth, depth=depth, **kwargs)()
    except Exception as e:
        if len(traceback.extract_tb(e.__traceback__)) > 1: raise e
    raise Continue()



def _pretty_tuple(val, _depth, depth, **kwargs):
    if not isinstance(val, tuple) or not val: raise Continue()
    return _pretty_enum(val, '()', _depth, depth, **kwargs)



def _pretty_list(val, _depth, depth, **kwargs):
    if not isinstance(val, list) or not val: raise Continue()
    return _pretty_enum(val, '[]', _depth, depth, **kwargs)



def _pretty_dict(val, _depth, depth, tmpl='', quote=False, **kwargs):
    try:
        v = next(iter(val.items()))
        assert(isinstance(v, tuple) and len(v) == 2)
    except:
        raise Continue()
    t = Table(0.0, 0, tmpl=tmpl, **kwargs)
    t.cell('C0', style=str(_depth%3 + 1), just='>')
    for k,v in val.items():
        if not quote and isinstance(k, str):
            k = k if (q:=k.strip()) and q==k else repr(k)
        else:
            k = repr(k)
        t(k,' \t', pretty(v, _depth=_depth+1, depth=depth-1, quote=quote, **kwargs),'\t')
    return t



def _pretty_iter(val, _depth, depth, **kwargs):
    try:
        assert(hasattr(val, '__iter__'))
        next(iter(val))
    except:
        raise Continue()
    return _pretty_enum(val, '<>', _depth, depth, **kwargs)



def _pretty_enum(val, paren, _depth, depth, tmpl='', **kwargs):
    t = Table(0.0, 0, tmpl=tmpl, **kwargs)
    t.cell('C0', style=str(_depth%3 + 1), just='>')
    for i,v in enumerate(val):
        t(f'\bdem {paren[0]}', i, f'\bdem {paren[1]} \t', pretty(v, _depth=_depth+1, depth=depth-1, **kwargs), '\t')
    return t
