import time
from threading import Thread


class Worker(object):
    def __init__(self, name, start_target, stop_target, args=(), kwargs={}):
        self.name = name
        self.start_target = start_target
        self.stop_target = stop_target
        self.args = args
        self.kwargs = kwargs
        self.restarts = 0
        self.thread = None

    def start(self):
        self.thread = Thread(target=self.start_target,
                             args=self.args, kwargs=self.kwargs)
        self.thread.start()

    def is_alive(self):
        return self.thread.is_alive()

    def check(self):
        if self.is_alive():
            return

        self.start()

        self.restarts += 1
        print('{0} restarted {1} time(s)'.format(self.name, self.restarts))

    def stop(self):
        self.stop_target()


class WorkerMonitor(object):
    def __init__(self):
        self.workers = []
        self.should_continue = True

    def add_worker(self, worker):
        self.workers.append(worker)
        worker.start()

    def start(self):
        while self.should_continue:
            time.sleep(1)
            for worker in self.workers:
                try:
                    worker.check()
                except:
                    pass

    def stop(self):
        self.should_continue = False
        while True:
            for worker in [w for w in self.workers if w.is_alive()]:
                worker.stop()
            time.sleep(0.5)
            if len([w for w in self.workers if w.is_alive()]) == 0:
                break
