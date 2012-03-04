import time
from datetime import datetime
from contextlib import closing
import json
from paramiko import SSHClient, SSHException, AutoAddPolicy

def start_ssh(host, username, password):
    ssh = SSHClient()
    try:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
    except SSHException:
        ssh.close()
        raise
    return ssh
    
def ssh_exec_command(command, ssh=None, host=None, username=None, password=None):
    run_command = lambda sh, cmd: sh.exec_command(cmd)[1].read().strip()
        
    if ssh:
        return run_command(ssh, command)

    with closing(start_ssh(host, username, password)) as ssh:
        return run_command(ssh, command)

def get_timestamp():
    timestamp = now()
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", 
           time.gmtime(time.mktime(timestamp.timetuple())))

def now():
    return datetime.now()
