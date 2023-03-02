from math import ceil, modf
from functools import reduce
from collections import namedtuple
import logging

log = logging.getLogger('print-ext.size')
_err = 0.0001


class Size():
    __ports__ = ('nom','size','min','max','rate','user')

    err = _err
    def __init__(self, **kwargs):
        if 'easy' in kwargs:
            v = kwargs.pop('easy')
            if isinstance(v, int):
                kwargs = dict(min=-v, max=-v, rate=0) if v < 0 else dict(min=v)
            else:
                kwargs = dict(rate=v)
        args = dict(max=1e10, rate=1, nom=0, size=0, user=None)
        args.update(kwargs)
        for k,v in args.items(): setattr(self, k, v)
        if self.rate == None: self.min, self.max, self.rate = self.nom, self.nom, 1
        if 'min' not in args: self.min = min(max(1, self.nom if self.nom < 12 else self.nom/4), self.max)
        if self.min > self.max or self.rate < 0: raise ValueError(f"Invalid parameter {self}")
        if not self.rate:
            if self.nom < self.min: self.nom = self.min
            elif self.nom > self.max: self.nom = self.max
        #print(f"SIZE {kwargs} -> {self}")


    def clone(self, **kwargs):
        return Size(**{k:kwargs.get(k,self[k]) for k in Size.__ports__})


    def __getitem__(self, k):
        return getattr(self,k)

    def dir(self, free):
        if self.size < self.min - _err: return 1 # We must grow because we are below our minimum
        if self.size > self.max + _err: return -1 # We must shrink because we are above our maximum
        shrink = self.size > self.min + _err # We can shrink if we are above our minimum
        grow = self.size < self.max - _err # We can grow if we are below our maximum
        if free > _err: return int(grow) # There is free space so grow if we can
        if free < -_err: return -int(shrink) # We are overflowing so shrink if we can
        return 2 + int(shrink) + 2*int(grow) # We are at the target size so return an indication of which way we can go
    

    def drate(self, dir, fixed_rate=0):
        if not self.rate: return 0 # No need to go anywhere
        if dir == 0: return 0
        if dir == -1: return -1.0/self.rate
        if dir == 1:  return self.rate
        if not fixed_rate: return 0
        if fixed_rate < 0:
            return self.rate if dir >= 4 else 0
        else:
            return -1.0/self.rate if dir%2 else 0
    
    
    def t_hit(self, rate):
        # TODO: Optimize by not stopping at minimum for positive rates, or maxima for negative rates
        if rate < 0:
            target = self.min if self.size < self.max+_err else self.max
        else:
            target = self.max if self.size > self.min-_err else self.min
        return (target-self.size)/rate


    def ideal(self):
        self.size = min(max(self.min, self.nom), self.max)
        return self


    def __repr__(self):
        s = []
        if self.nom != 0: s.append(f'nom={self.nom}')
        if True: s.append(f'min={self.min}')
        if self.max != 1e10: s.append(f'max={self.max}')
        if self.rate != 1: s.append(f'rate={self.rate}')
        return 'Size(' + ', '.join(s) + f')[{self.size}]'
        

    @staticmethod
    def resize(cells, size, wrap=False, elide=None):
        if size == 0: return [[c.ideal() for c in cells]]
        rows = _resize_wrap(cells, size) if wrap else [_resize_no_wrap(cells, size)]
        return [_elide(row, size, elide) for row in rows] if elide else rows



def _elide(cells, size, elide):
    ''' If sizes overflows then replace the middle portion with the Size returned from elide()'''
    zeros = any(not x.size and x.min for x in cells)
    #print(f"_elide {sum([c.size for c in cells])} -> {size} zeros?:{zeros}", ''.join(f'\n  {c} {c.user}' for c in cells))
    if sum([c.size for c in cells]) <= size and not zeros: return cells
    total = cells[0].size
    r = [1, len(cells)]
    ri = 1
    while r[0] < r[1] and total + cells[r[ri] + 1 - ri*2].size < size:
        r[ri] += 1 - ri*2
        total += cells[r[ri]].size
        ri = (ri+1)%2
    if r[0] != r[1]:
        cells = _resize_no_wrap(cells[:r[0]] + [elide(cells[r[0]:r[1]])] + cells[r[1]:], size)
        print(f"ELIDED {cells}")
    #print(f"    {r} {total}", ''.join(f'\n  {c} {c.user}' for c in cells))
    total = sum([c.size for c in cells])
    if total > size: cells[0].size += size - total
    assert(cells[0].size > 0), f"The elided cell is to big. {cells}"
    return cells



def _round(cells, size):
    if not size: return cells
    sizes = [modf(c.size) for c in cells]
    s = [[i, int(s[1]), s[0], cells[i]] for i,s in enumerate(sizes)]
    sw = sum([x[1] for x in s])
    s = sorted(s, key=lambda x: x[2], reverse=True)
    i = 0
    while sw + i != size and i < len(s) and s[i][2]:
        s[i][1] += 1
        i += 1
    for _,s,_,cell in sorted(s, key=lambda x:x[0]): cell.size = s
    return cells

    
def _resize_wrap(cells, size):
    ci = 0
    rows = []
    while cells:
        #print(f"_resize_wrap size:{size}", ''.join(f'\n  {c} {c.user}' for c in cells))
        _resize_no_wrap(cells, size)
        if len(rows): _resize_no_wrap(rows[-1], size)
        rows.append([cells.pop(0)])
        row_size = rows[-1][0].size
        while cells:
            row_size += cells[0].size
            if row_size > size: break
            rows[-1].append(cells.pop(0))
    return rows


def _resize_no_wrap(cells, size):
    for c in cells: c.size = c.nom
    while True:
        sizes = [c.size for c in cells]   # The current actual sizes of each cell
        free = size - sum(sizes) # The amount of free space to fill
        #print(f"_resize_no_wrap {sizes}/{size}  free:{free}")
        dirs = [c.dir(free) for c in cells] # <=1 we must change,  >1 We might be able to change if needed
        if not any(dirs): return _round(cells, size) # Everyone is static
        rates = [c.drate(d) if d <= 1 else 0 for c,d in zip(cells, dirs)] # At what rate MUST each cell grow or shrink?
        fixed_rate = sum(rates) # The rate at wich the TOTAL size MUST change
        vrates = [c.drate(d, fixed_rate) if d > 1 else 0 for c,d in zip(cells,dirs)] # When we are at size, but we MUST change, then these vrates will compensate for fixed_rate
        variable_rate = sum(vrates) # The rate at which the total moves due to the vrate cells
        if not variable_rate and not fixed_rate: return _round(cells, size) # reached size and everyone inbounds
        if variable_rate: # variable cells are compensating for fixed_rate cells
            rates = [r*fixed_rate/-variable_rate if r else rates[i] for i,r in enumerate(vrates)] # variable rates step in to offset the fixed rate
        total_rate = sum(rates) # This is the rate at wich the total size will change
        ts = [c.t_hit(r) for c,r in zip(cells,rates) if r] # The time when the cell hits a critical junction
        assert(ts)
        tt = 0
        if free and total_rate: # Only fixed rates
            tt = free / total_rate # The amount of time to close the 'free' gap
            if tt >= 0: ts.append(tt)
        t = min(ts)
        assert(t)
        for c,r in zip(cells, rates): c.size += r*t
    