from print_ext.printer.task import ProgressTaskPrinter
from print_ext.printer import StringPrinter

def test_progress_task_nocapture():
    s = StringPrinter(ascii=True)
    with s.progress(f'name', capture=False) as update:
        for i in range(5):
            update(f'{i}')#, tag={'progress':(i, 5)})
        update("done", tag='progress:done')
    assert(str(s) == '0\n1\n2\n3\n4\ndone\n')



def test_progress_task_rewind():
    s = StringPrinter(ascii=True)
    with s.progress(f'name') as update:
        for i in range(5):
            update(f'{i}')#, tag={'progress':(i, 5)})
        update("done", tag='progress:done')
    assert(str(s) == '* name done\n')


