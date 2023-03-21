import pytest, sys
from print_ext import Flattener


@pytest.fixture(autouse=True)
def add_printer(doctest_namespace):
    def printer(*args, **kwargs):
        print = Flattener(width=80)
        return print(*args, stack_offset=1, **kwargs)
    doctest_namespace["printer"] = printer
