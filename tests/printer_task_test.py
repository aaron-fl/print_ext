import pytest, asyncio, random
from print_ext import Printer
from print_ext.printer import TaskPrinter, StringPrinter


@pytest.mark.xfail()
def test_task_printer_buffer_truncate():
    ''' old widgets should be discarded when they overflow `buffer_lines`'''
    assert(0)


@pytest.mark.xfail()
def test_task_printer_buffer_file():
    ''' save old widgets to file'''
    assert(0)


@pytest.mark.xfail()
def test_task_printer_error():
    ''' Display full output when an error happens '''
    assert(0)



async def coro(lines, sleep=5, maxlen=50):
    print = Printer()
    for i, line in enumerate(lines):
        if i < len(lines)-1:
            slp = sleep / float(len(lines)-i+1)
            slp = random.triangular(0.1*slp, 1.9*slp)
        else:
            slp = sleep
        sleep -= slp
        await asyncio.sleep(slp)
        print(' '.join([line]*random.randrange(maxlen)), tag={'progress':(i,len(lines))})


async def tcoro():
    print = Printer()
    print('1')
    print.hr()
    print('2')



@pytest.mark.asyncio
async def test_task_coro_wait_nocapture():
    p = StringPrinter(ascii=True)
    await p.task(tcoro(), name='tcoro', capture=False).wait()
    assert(str(p) == '1\n---\n2\n')




@pytest.mark.asyncio
async def test_task_coro_wait():
    p = StringPrinter(ascii=True)
    await p.task(tcoro(), name='bob').wait()
    assert(str(p) == '* bob 2\n')



def test_task_printer_sync_nocapture():
    p = StringPrinter()
    p.task(tcoro(), capture=False).sync()
    assert(str(p) == '1\n───\n2\n')



def test_task_printer_sync():
    p = StringPrinter()
    p.task(tcoro(), name='bob').sync()
    assert(str(p) == '* bob 2\n')



async def main():
    p = Printer()
    await p.task(coro('abcdefg', 5), capture=True).wait()
    p('goodbye')


if __name__ == '__main__':
    asyncio.run(main())

