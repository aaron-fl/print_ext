import pytest, asyncio
from print_ext import Printer, TaskGroup

@pytest.mark.xfail()
def test_task_printer_error():
    ''' Display full output when an error happens '''
    assert(0)


async def a():
    Printer('A')
    return 'a'

async def b():
    Printer('B')
    return 'b'



@pytest.mark.asyncio
async def test_task_group_keep_going():
    tp = Printer.using(TaskGroup)(keep_going=True)
    donetask = asyncio.create_task(a())
    await donetask
    tp.pending.add(donetask)
    async def err():
        tp.create_task(b())
        raise AttributeError('err')
    tp.create_task(err())
    await tp
    assert(len(tp.complete) == 3), f"{tp.complete} {tp.pending}"
    results = set()
    for t in tp.complete:
        try:
            results.add(t.result())
        except AttributeError as e:
            results.add(str(e))
    assert(results == {'a', 'b', 'err'})



@pytest.mark.asyncio
async def test_task_group_no_keep_going():
    tp = Printer.using(TaskGroup)(keep_going=False)
    async def err():
        tp.create_task(b())
        raise AttributeError('err')
    tp.create_task(err())
    with pytest.raises(AttributeError):
        await tp
    assert(len(tp.complete) == 1), f"{tp.complete} {tp.pending}"
    await tp
    results = set()
    for t in tp.complete:
        try:
            results.add(t.result())
        except AttributeError as e:
            results.add(str(e))
    assert(results == {'b', 'err'})
