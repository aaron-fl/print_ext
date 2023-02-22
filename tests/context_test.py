import pytest 
from print_ext.context import Context, CVar, IntCVar, FloatCVar, ObjectAttr
from .testutil import debug_dump

Context.define(CVar('d'))
Context.define(CVar('z'))
Context.define(IntCVar('m'))
Context.define(IntCVar('q','Q'))
Context.define(IntCVar('a','A','aa'))
Context.define(FloatCVar('pi','PI'))


class Animal(Context):
    ctx_defaults = Context.defaults(a=3, pi=3.1415)


class Cat(Animal):
    ctx_defaults = Context.defaults(A=4)

    @property
    def width(self):
        return 99 + self['a']


class Dog(Animal):
    ctx_defaults = Context.defaults(a=5)


def test_ctx_redefine():
    with pytest.raises(ValueError):
        Context.define(IntCVar('A','a','aa'))
    with pytest.raises(ValueError):
        Context.define(IntCVar('a','A'))
    Context.define(IntCVar('a','aa','A'))



def test_ctx_CallableVar():
    c = Animal(width_nom=ObjectAttr('width', -101))
    assert(c['width_nom'] == -101)
    c = Cat(width_nom=ObjectAttr('width', -101))
    assert(c['width_nom'] == 103)



@pytest.mark.xfail
def test_ctx_parent_loops():
    ''' Don't create loops
    '''
    assert(False)



def test_kwargs():
    c = Cat(pi=3.1)
    assert(c['pi'] == 3.1)
    c['PI'] = 2
    assert(c['pi'] == 2)



def test_not_found():
    c = Cat()
    with pytest.raises(KeyError):
        c['dne']
    


def test_context_defaults():
    c = Cat()
    assert(c['a'] == 4)
    assert(c['q'] == None)
    assert(Animal()['a'] == 3)
    


def test_del():
    c = Cat(A=99)
    assert(c['a'] == 99)
    del c['a']
    assert(c['a'] == 4)


def test_parent_value():
    c1 = Cat(m=99, q=424, d='cat')
    c2 = Dog(m=33, z='zz', parent=c1)
    assert(c1['m'] == 99)
    assert(c2['m'] == 33)
    assert(c1['q'] == 424)
    assert(c2['q'] == 424)
    assert(c2['z'] == 'zz')
    assert(c2['a'] == 5)
    assert(c2['d'] == 'cat')
    del c1['d']
    assert(c2['d'] == None)


def test_ctx_empty_get():
    c1 = Cat(m=99, q=424, d='cat')
    assert(c1.ctx() == None)
    