from .stream import StreamPrinter
from .rewinder import Rewinder


class TTYRewinder(Rewinder):
    def __init__(self, printer):
        super().__init__(printer)
        self.offset = len(self.printer.rw_lines) # Offset into printer.rw_lines
        # If we are the root rewinder, then turn off the cursor
        if self.offset == 0: self.printer.stream.write('\033[?25l')


    def __call__(self):
        # Clear the tail
        self.printer.stream.write('\033[0J') 
        self.printer.rw_lines[self.printer.rw_i:] = []
        # Move the cursor up some lines
        back = self.printer.rw_i - self.offset
        if back: self.printer.stream.write(f'\033[{back}F')
        self.printer.rw_i = self.offset
        self.printer.stream.flush()


    def _done(self):
        # Clear the tail
        self.printer.stream.write('\033[0J') 
        self.printer.rw_lines[self.offset:] = []
        # If we are the root rewinder then turn the cursor back on
        if self.offset == 0: self.printer.stream.write('\033[?25h')



class TTYPrinter(StreamPrinter):
    Rewinder = TTYRewinder

    def __init__(self, *, color=None, **kwargs):
        self.color = (color == None) or color
        self.rw_lines = []
        self.rw_i = 0
        super().__init__(**kwargs)


    def write_line(self, line):
        if not self.rewinders: return super().write_line(line)
        if self.rw_i == len(self.rw_lines): # New re-writable lines
            self.rw_lines.append(line)
            self.stream.write(self.format_out(*line.styled()))
        else:
            # Patch from rw_lines[rw_i] to line
            self.rw_lines[self.rw_i] = line
            self.stream.write(self.format_out(*line.styled()))
            self.stream.write(f'\033[0K')
        self.rw_i += 1
