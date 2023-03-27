import pytest, sys
from print_ext import Printer, StringIO
from print_ext.printer import printer_for_stream

@pytest.fixture(autouse=True)
def add_printer(doctest_namespace):
    def printer(*args, **kwargs):
        print = printer_for_stream(width_max=80)
        return print(*args, stack_offset=1, **kwargs)
    doctest_namespace["Printer"] = printer
