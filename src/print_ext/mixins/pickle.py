import datetime, pickle, weakref


class Pickle():
    ''' Save widgets/tags to a file for possible later playback.
    '''

    def __init__(self, log_file=None, **kwargs):
        self.f = open(log_file, 'ab')
        weakref.finalize(self, self.f.close)
        self.__pickler = pickle.Pickler(f)
        self.__pickler.dump(datetime.datetime.now())


    def append(self, widget, tag):
        self.__pickler((widget, tag))
        super().append(widget, tag)
