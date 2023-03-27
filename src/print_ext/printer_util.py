class Rewinder():
    def __init__(self, printer):
        self.printer = printer


    def __enter__(self):
        assert(self not in self.printer.rewinders), f"Re-entered with the same rewinder {self}"
        self.printer.rewinders.append(self)
        return self


    def done(self):
        pass


    def __exit__(self, *args):
        self.done()
        self.printer.rewinders.pop()
    


class Tag():

    def __init__(self, tag=None, **kwargs):
        self.parent = tag
        self._dict = kwargs
        if isinstance(tag, str):
            self._dict = dict((t.split(':',1)+[True])[:2] for t in tag.split(';'))
            for k,v in self._dict.items():
                try: self._dict[k] = int(v)
                except ValueError:
                    try: self._dict[k] = float(v)
                    except ValueError: pass
            self._dict.update(kwargs)
            self.parent = None
        elif isinstance(tag, dict):
            self._dict.update(tag)
            self.parent = None
        if self.parent and not isinstance(self.parent, Tag):
            raise ValueError(f"{self.parent!r} is not a `Tag`")
        
    
    def get(self, key, default=None):
        if key in self._dict: return self._dict[key]
        if self.parent: return self.parent.get(key, default)
        return default
