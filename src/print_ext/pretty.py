from .table import Table


def pretty(val, depth=0):
    if isinstance(val, tuple): return _pretty_list(val, '()', depth) if val else 'tuple()'
    if isinstance(val, list):  return _pretty_list(val, '[]', depth) if val else '[]'
    if hasattr(val, 'items'): return _pretty_dict(val, depth) if val else '{}'
    return val


def _pretty_list(val, paren, depth):
    t = Table(0.0, 0, tmpl='')
    t.cell('C0', style=str(depth%3 + 1), just='>')
    for i,v in enumerate(val):
        t(f'\bdem {paren[0]}', i,f'\bdem {paren[1]} ', '\t', pretty(v, depth+1), '\t')
    return t


def _pretty_dict(val, depth):
    t = Table(0.0, 0, tmpl='')
    t.cell('C0', style=str(depth%3 + 1), just='>')
    for k,v in val.items():
        t(k,' ', '\t', pretty(v, depth+1),'\t')
    return t
