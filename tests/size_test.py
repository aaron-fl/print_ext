import pytest 
from functools import partial
from print_ext.size import Size


def calc(size, *args, elide=None, **kwargs):
    def _size(arg):
        # (rate, min)
        # (rate, min, max)
        # (rate, min, max, nom)
        # (nom, min, max, rate)
        if not isinstance(arg, tuple): return Size(rate=arg)
        elif len(arg) == 2: return Size(rate=arg[0], min=arg[1])
        elif len(arg) == 3: return Size(rate=arg[0], min=arg[1], max=arg[2])
        elif len(arg) == 4: return Size(rate=arg[0], min=arg[1], max=arg[2], nom=arg[3])
        
        
    els = [_size(a) for a in args]
    rstr = ''
    tot, ftot = 0, []
    rows = Size.resize(els, size, elide=elide, **kwargs)
    print(rows)
    for ri, row in enumerate(rows):
        rmax = sum([c.max for c in row])
        rmin = 0 if elide else sum([c.min for c in row])
        rsize = sum([c.size for c in row])
        print(f"{ri}: min:{rmin}/ask:{size}/max:{rmax}/got:{rsize} -- {row}")
        if size: assert(rsize == max(rmin, min(rmax, size)))
        for c in row:
            if not elide: assert(c.size >= c.min - Size.err)
            assert(c.size <= c.max + Size.err)
        rstr += ''.join(f' {c.size}' for c in row) + ' --'
    return rstr[:-3].strip()


def test_checks():
    Size()
    Size(min=0, max=0)
    Size(rate=0.1)
    for args in [{'rate':-1}, {'min':0.5, 'max':0.499999}]:
        with pytest.raises(ValueError):
            Size(**args)
   

def test_size_one():
    C = partial(calc, 100, wrap=False)
    assert(C((1,10,500,86.66666666666667)) == '100')

    for args in [(1,0,200,0), (1,0,200,120), (1,0,200,-100), 4, 0.1, (1, 99.9), (1,1,100.1)]:
        print(args)
        assert(C(args) == '100')
    assert(C((1,0,0,100)) == '0')
    assert(C((1,120)) == '120')
    assert(C((1,5,99)) == '99')
    

@pytest.mark.xfail
def test_size_rate0():
    ''' Zero rate fixes the size to nominal '''
    raise Exception()



def test_two():
    C = partial(calc, 100, wrap=False)
    assert(C((2000,60), (1, 70)) == '60 70')
    assert(C((2000,1,10), (1, 1, 60)) == '10 60')
    assert(C(1, 1) == '50 50')
    assert(C(2, 1) == '67 33')
    assert(C(200000, 1) == '99 1')
    assert(C((2000,1), (1, 25)) == '75 25')
    assert(C((2000,1,10), (1, 25)) == '10 90')
    assert(C((1,60,60), 1) == '60 40')



def test_three():
    C = partial(calc, 100, wrap=False)
    assert(C((1,40,40), 1, 1) == '40 30 30')
    assert(C((1,40,40), 2, 1) == '40 45 15')
    assert(C((1,40,40,40), 2, 1) == '40 40 20')


def test_zero():
    C = partial(calc, 0, wrap=False)
    assert(C((1,40,40), (1,0,10000, 10), (1,0,20,10000)) == '40 10 20')


def test_size_wrap():
    C = partial(calc, 100, wrap=True)
    assert(C((1, 60, 80, 60), (1, 50, 500, 1), (1, 10, 500, 1)) == '80 -- 50 50')


def test_size_round():
    ''' rounding to integer boundries produces a +/- 1 problem '''
    C = partial(calc, 20, wrap=True)
    assert(C((1.0,0,5,9), (1.0,0,10000,3), (1.0,0,10000,1)) == '5 9 6')


def test_size_fractional():
    ''' Fractionally small cells may round to zero.  If you set a minimum of zero then you have to deal with it. '''
    C = partial(calc, 3, wrap=False)
    assert(C((4,0), (1,0), (4,0), (1,0), (4,0)) == '1 0 1 0 1')


def test_overflow():
    ''' A Single cell overflows the width so it must be truncated with a warning.
    This is the only situation where the cell will fall out of bounds (less than min)
    '''
    def elide(x):
        return Size(min=4, max=8)
    assert(calc(100, (1,120), 1, (1, 99), (1,101), wrap=True, elide=(1,4,8)) == '100 -- 1 99 -- 100')
    assert(calc(100, (1,120), 1, (1, 99), (1,101), wrap=False, elide=elide) == '96 4')
    assert(calc(100, (1,120), 100, (1, 99), (1,101), wrap=True, elide=None) == '120 -- 1 99 -- 101')
    assert(calc(100, (1,120), 1, (1, 99), (1,101), wrap=False, elide=None) == '120 1 99 101')


def test_elide_zero():
    ''' If a cell wants to be zero don't force an elision '''
    def die(x):
        assert(False)
    assert(calc(100, 1, (1, 0, 0), wrap=True, elide=die) == '100 0')
    

def test_auto_params():
    ''' dont set a minimum < nom for nom < 12.
        Set min as size/4 for nom >=12
    '''
    assert(Size(nom=8).min == 8)
    assert(Size(nom=12).min == 3)
    s = Size(nom=3, rate=None)
    assert( (s.min, s.max) == (3, 3))
    assert(Size(nom=30, min=0).min == 0)
    s = Size(nom=0, min=0, max=0, rate=1)
    assert( (s.min, s.max) == (0,0))
    assert(Size(nom=0).min == 1)
    assert(Size(nom=5, max=2).min == 2)

if __name__=='__main__':
    test_overflow()
