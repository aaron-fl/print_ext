import asyncio, pytest
from .testutil import printer as printer


def test_progress_spinner_gone():
    o,p = printer()
    bar = p.progress()
    bar('\b1 Ready')
    bar('\b1 Set')
    bar('\b1 Go', done=True)
    assert(o.getvalue() == 'Ready\nSet   \nGo  \n')
    

@pytest.mark.skip(reason="Change spinner impl")
def test_spinner():
    #print['ascii'] = False
    p = print.progress(steps=30)
    for i in range(30):
        p(f'\b{i%3+1} カタカナん {i}')
    p('done??', style='err', done=True)
