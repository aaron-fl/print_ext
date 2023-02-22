import pytest
from print_ext.sgr import SGR


def test_sgr_from_str():
    invalid = ['bob','bb','bk','!_.', '_b', '!b', ':,.', ',!;']
    for s in invalid:
        print(f' invalid "{s}"')
        with pytest.raises(ValueError):
            SGR(s)

    valid = ['b', 'b^k', '!', '_', '!_', '', 'b!_;', 'b!','^k_', '^y!', '^r!_']
    for s in valid:
        print(f' VALID "{s}"')
        assert(SGR(str(SGR(s))) == SGR(s))


def test_sgr_add():
    def _t(a, b, c):
        print(f" {SGR(a)}  + {SGR(b)}  == {SGR(c)}  ({SGR(a) + SGR(b)})")
        assert(SGR(a) + SGR(b) == SGR(c))
    _t('b', 'k', 'k')
    _t('b^k_', '^y.', 'b^y._')
    _t('', '', '0')
    _t('', 'b!_', 'b!_')
    _t('b!_', '', '0')


def test_sgr_diff():
    def _t(a, b, c):
        v = SGR(b).diff(SGR(a))
        print(f" {SGR(a)} || {SGR(b)} == {repr(c)}  {repr(v)}")
        assert(v == c)
    _t('r!_', 'r._', '\033[0;4;31m')
    _t('', '', '')
    _t('', 'k', '\033[30m')
    _t('k!', '', '\033[0m')
    _t('k.~', 'k!_', '\033[1;4m')
    
    
