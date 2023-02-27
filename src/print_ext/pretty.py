from .table import Table


def pretty(val, _depth=0, **kwargs):
    if isinstance(val, tuple): return _pretty_list(val, '()', _depth, **kwargs) if val else 'tuple()'
    if isinstance(val, list):  return _pretty_list(val, '[]', _depth, **kwargs) if val else '[]'
    if hasattr(val, 'items'): return _pretty_dict(val, _depth, **kwargs) if val else '{}'
    return val


def _pretty_list(val, paren, _depth, tmpl='', **kwargs):
    t = Table(0.0, 0, tmpl=tmpl, **kwargs)
    t.cell('C0', style=str(_depth%3 + 1), just='>')
    for i,v in enumerate(val):
        t(f'\bdem {paren[0]}', i,f'\bdem {paren[1]} ', '\t', pretty(v, _depth+1), '\t')
    return t


def _pretty_dict(val, _depth, tmpl='', **kwargs):
    t = Table(0.0, 0, tmpl=tmpl, **kwargs)
    t.cell('C0', style=str(_depth%3 + 1), just='>')
    for k,v in val.items():
        t(k,' ', '\t', pretty(v, _depth+1),'\t')
    return t
