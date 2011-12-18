import time, sys
from contextlib import closing
from multiprocessing import Process 
from paramiko import SSHClient, SSHException, AutoAddPolicy
from health import VarnishHealth
from stats import VarnishStats

def process_data(host, username, password, varnish):
    try:
        with closing(SSHClient()) as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(host, username=username, password=password)
            varnish.process(ssh)
    except KeyboardInterrupt:
        pass
    
def start_process(target, args):
    process = Process(target=target, args=args)
    process.start()
    return process
    
if __name__ == "__main__":
    details = tuple(sys.argv[1:4])

    arguments = [details + (VarnishStats(),), details + (VarnishHealth(),)]
    processes = [{'target': process_data, 'args': a, 'restarts': 0,
                  'process': start_process(target=process_data, args=a)} 
                 for a in arguments]
    print 'Started gathering varnish data'
    
    try:
        while True:
            time.sleep(1)
            deadprocesses = [p for p in processes if not p['process'].is_alive()]
            for deadprocess in deadprocesses:
                target, process, args = deadprocess['target'], deadprocess['process'], deadprocess['args']
                process.terminate()
                deadprocess['process'] = start_process(target=target, args=args)
                deadprocess['restarts'] += 1
                print 'Restarts: %s' % deadprocess['restarts']
    except KeyboardInterrupt:
        pass
        
    print 'Ending gathering varnish data'