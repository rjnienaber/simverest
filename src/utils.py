import os
import time
from datetime import datetime
from contextlib import closing
import json
from paramiko import SSHClient, SSHException, AutoAddPolicy

HEALTH_JSON_FILE = 'health.json'
STATS_JSON_FILE = 'stats.json'

def set_json_path(path):
    HEALTH_JSON_FILE = os.path.join(path, 'health.json')
    STATS_JSON_FILE = os.path.join(path, 'stats.json')

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

def convert_to_utc(timestamp):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", 
           time.gmtime(time.mktime(timestamp.timetuple())))
        
def dump_data(data, filepath):
    dthandler = lambda obj: convert_to_utc(obj) if isinstance(obj, datetime) else None
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=2, default=dthandler)
        
def read_all(filePath):
    with open(filePath, 'r') as file:
        return file.read()