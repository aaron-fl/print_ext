import asyncio, pytest
from print_ext import print
from .testutil import printer


def test_progress_spinner_gone():
    o,p = printer()
    bar = p.progress()
    bar('\b1 Ready')
    bar('\b1 Set')
    bar('\b1 Go', done=True)
    print(o.getvalue())
    assert(o.getvalue() == 'Ready\nSet   \nGo  \n')
    


def test_spinner():
    print['ascii'] = False
    p = print.progress(steps=30)
    for i in range(30):
        p(f'\b{i%3+1} カタカナん {i}')
    p('done??', style='err', done=True)
    print('---')


async def many_bars():
    pass
    #go to the (start of the) previous line: \033[F
    #move along ncols: \03[{ncols}G


if __name__ == '__main__':
    asyncio.run(many_bars())
