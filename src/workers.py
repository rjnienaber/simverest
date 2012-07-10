import time
from threading import Thread
from datetime import datetime


class Worker(object):
    def __init__(self, name, unit_of_work, args=(), kwargs={}):
        self.name = name
        self.unit_of_work = unit_of_work
        self.args = args
        self.kwargs = kwargs
        self.restarts = 0
        self.thread = None

    def start(self):
        self.thread = Thread(target=self.unit_of_work.start,
                             args=self.args, kwargs=self.kwargs)
        self.thread.daemon = True
        self.thread.start()

    def is_alive(self):
        #if unit of work has been updated in the last 30 seconds, it's alive
        update_interval = datetime.now() - self.unit_of_work.last_update()
        thread_still_updating = update_interval < 30
    
        return thread_still_updating and self.thread.is_alive()

    def check(self):
        if self.is_alive():
            return
        
        self.start()

        self.restarts += 1
        print('{0} restarted {1} time(s)'.format(self.name, self.restarts))

    def stop(self):
        self.unit_of_work.stop()


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
                if not self.should_continue:
                    break
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
    
    def last_update(self):
        return datetime.now()
