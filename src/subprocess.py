from multiprocessing import Process 

class SubProcess(object):
    def __init__(self, name, target, args=(), kwargs={}):
        self.name = name
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.restarts = 0
        self.process = None
        
    def start(self):
        if self.process != None:
            self.process.terminate()
        self.process = Process(target=self.target, args=self.args, kwargs=self.kwargs)
        self.process.start() 
        return self
        
    def check(self):
        if self.process.is_alive():
            return
        self.start()
        self.restarts += 1
        print '{0} restarted {1} time(s)'.format(self.name, self.restarts)
