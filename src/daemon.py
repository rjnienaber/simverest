import time, sys
from contextlib import closing
from multiprocessing import Process 
from paramiko import SSHClient, SSHException, AutoAddPolicy
from health import BackendHealth

def start_ssh(host, username, password):
    ssh = SSHClient()
    try:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
    except SSHException:
        ssh.close()
        raise
        
    return ssh

def process_varnish_health(host, username, password):
    with closing(start_ssh(host, username, password)) as ssh:
        backend_health = BackendHealth(ssh)
        backend_health.process()
    
    
def process_varnish_stats(host, username, password):
    with closing(start_ssh(host, username, password)) as ssh:
        while True:
            stdin, stdout, stderr  = ssh.exec_command('cat /var/run/varnishd.pid')
            pid = stdout.readline()
            stdin, stdout, stderr = ssh.exec_command('top -b -n 1 -d 1 -U nobody | grep varnishd')
            stats = stdout.readline().split()
            print {'cpu': stats[8], 'memory':stats[9], 
                    'virtualmem': stats[4], 'reservedmem': stats[5]} 
            
            time.sleep(1)

def start_process(target, args):
    process = Process(target=target, args=args)
    process.start()
    return process
    
if __name__ == "__main__":
    host, username, password = sys.argv[1:4]
    details = tuple(sys.argv[1:4])
    
    targets = [process_varnish_stats, process_varnish_health]
    processes = [{'target': t, 'args': details, 'restarts': 0,
                  'process': start_process(target=t, args=details)} for t in targets]
    
    while True:
        time.sleep(1)
        deadprocesses = [p for p in processes if not p['process'].is_alive()]
        for deadprocess in deadprocesses:
            target, process = deadprocess['target'], deadprocess['process']
            process.terminate()
            deadprocess['process'] = start_process(target=target, args=details)
            deadprocess['restarts'] += 1
            print 'Restarts: %s' % deadprocess['restarts']
