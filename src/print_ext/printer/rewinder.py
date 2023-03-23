
class Rewinder():
    def __init__(self, printer):
        self.printer = printer


    def __enter__(self):
        assert(self not in self.printer.rewinders), f"Re-entered with the same rewinder {self}"
        self.printer.rewinders.append(self)
        return self


    def _done(self):
        pass


    def __exit__(self, *args):
        self._done()
        self.printer.rewinders.pop()
    