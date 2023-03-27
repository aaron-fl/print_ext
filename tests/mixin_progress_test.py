import pytest
from print_ext import Printer, StringIO, Progress
from print_ext.mixins.stream import Oneway


from tests.testutil import flat

def test_progress_bar():
    p = Printer.using(Progress)(width_max = 20, ascii=True)
    p('a', tag={'progress':(1, 4)})
    assert(p.set_progress() == (1, 4, ''))
    assert(flat(p) == [' 25%===------------ ', 'a                   '])


def test_progress_bar2():
    p = Printer.using(Progress)(width_max = 20, ascii=True)('a', tag='progress:done')
    assert(p.set_progress() == (0,0,'done'))
    assert(flat(p) == ['*  a                '])



def test_progress_bar3():
    p = Printer.using(Progress)(ascii=True)('z', tag='progress:0.5')('a', tag='progress:Bummer!')
    assert(p.set_progress() == (0.5,1.0,'Bummer!'))
    assert(flat(p) == ['===============---------------  Bummer!', 'z', 'a'])


def test_progress_bar4():
    p = Printer.using(Progress)(ascii=True, width_max=4)('z', tag='progress:0.5')('a', tag='progress:Bummer!')
    assert(flat(p) == ['!50%', 'z   ', 'a   '])


def test_progress_bar5():
    p = Printer.using(Progress)(ascii=False, width_max=8, name='alpha')('z', tag='progress:0.5')
    assert(flat(p) == ['▄50% a⋯a', 'z       '])



def test_with_progress_oneway():
    s = Printer.using(Oneway)()
    with s.progress(f'name') as update:
        for i in range(5):
            update(f'{i}', tag={'progress':(i, 5)})
        update("done", tag='progress:done')
    update('more')
    assert(str(s) == '0\n1\n2\n3\n4\ndone\nmore\n')



def test_progress_task_rewind():
    s = Printer.using(StringIO)(ascii=True)
    with s.progress(f'name') as update:
        for i in range(5):
            update(f'{i}')#, tag={'progress':(i, 5)})
        update("done", tag='progress:done')
    update('more')
    assert(str(s) == '* name done\nmore\n')
