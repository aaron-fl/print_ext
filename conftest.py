import pytest, sys
from print_ext.printer import StreamPrinter

@pytest.fixture(autouse=True)
def add_printer(doctest_namespace):
    def printer(*args, **kwargs):
        print = StreamPrinter(width_max=80)
        return print(*args, stack_offset=1, **kwargs)
    doctest_namespace["Printer"] = printer
