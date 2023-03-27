import asyncio

class TaskGroup():
    def __init__(self, keep_going=False, **kwargs):
        super().__init__(**kwargs)
        self.keep_going = keep_going
        self._coros = []
        self.pending = set()
        self.complete = set()


    def _start_coros(self):
        loop = asyncio.get_running_loop()
        while self._coros:
            coro, name = self._coros.pop()
            self.pending.add(self.context().run(lambda: loop.create_task(coro, name=name)))
        

    def create_task(self, coro, name=None):
        self._coros.append((coro, name))
        try:
            self._start_coros()
        except RuntimeError:
            pass # we will start these later when there is a running loop


    def cancel(self):
        ''' Cancel all pending tasks.  Uncreated coros are cleared.
        '''
        self._coros = []
        for p in self.pending:
            if not p.done(): p.cancel()


    async def wait(self, keep_going=None):
        ''' Wait for all of the pending tasks to complete.

        If `keep_going` is True then any exception in a task will be ignored and we will wait for all tasks to finish.
        After this method returns then you can check each task's result() to look for exceptions.

        If `keep_going` is False then any exception in a task will cause this method to raise that exception.
        The tasks remain running and you can `cancel()` them or `wait()` again.
        '''
        if keep_going == None: keep_going = self.keep_going
        async for task in self.as_completed():
            if keep_going: continue
            task.result()


    def __await__(self):
        yield from self.wait().__await__()


    def done(self):
        return not (self._coros or self.pending)


    async def as_completed(self):
        ''' A generator that yields each task as it completes.
        '''
        while not self.done():
            self._start_coros()
            # Return all the done tasks that don't need awaiting.
            done = set(p for p in self.pending if p.done())
            if not done:
                done, _ = await asyncio.wait(self.pending, return_when=asyncio.FIRST_COMPLETED)
            self.complete.update(done)
            self.pending.difference_update(done)
            for d in done: yield d


    async def __aenter__(self):
        return self
    

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            self.cancel()
        await self.wait(keep_going=True)
