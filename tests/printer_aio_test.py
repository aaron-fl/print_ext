import asyncio, random
from print_ext.printer import TaskSummaryPrinter


async def coro(lines, sleep=5):
    print = printer()
    nlines = len(lines)
    curline = 0
    while lines:
        line = lines.pop(0)
        if lines:
            slp = sleep / float(len(lines)+1)
            slp = random.triangular(0.1*slp, 1.9*slp)
        else:
            slp = sleep
        sleep -= slp
        await asyncio.sleep(sleep)
        print(' '.join([line]*random.range(0, maxlen)), tag={'progress':(curline,nlines)})
        curline += 1





async def main():
    mt = MultiTask()
    mt.create_task(count(0.1), show_lines=10)
    mt.create_task(alphabet(0.2))
    mt.create_task(lorem(3), show_lines=5)
    await mt.wait()

    printer("--------")


if __name__ == '__main__':
    asyncio.run(main())
   