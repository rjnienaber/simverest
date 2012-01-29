import time, sys, os
from contextlib import closing
from collectors.health import VarnishHealth
from collectors.stats import VarnishStats
from web import api
from subprocess import SubProcess
import utils

def process_data(host, username, password, varnish):
    try:
        with closing(utils.start_ssh(host, username, password)) as ssh:
            varnish.process(ssh)
    except KeyboardInterrupt:
        pass

def start_web_server(varnish_hosts, port=8080, server='wsgiref'):
    try:
        api.start(varnish_hosts, port, server)
    except KeyboardInterrupt:
        pass
        
if __name__ == "__main__":
    utils.set_json_path(os.getcwd())

    details = tuple(sys.argv[1:4])
    host, username, password, http_port, server = sys.argv[1:6]
    hostname = utils.ssh_exec_command('hostname', host=host, username=username, password=password)
    
    stats = SubProcess('Stats', process_data, details + (VarnishStats(hostname),))
    health = SubProcess('Health', process_data, details + (VarnishHealth(hostname, False),))
    web = SubProcess('Web', start_web_server, [hostname], {'port': http_port, 'server':server})

    stats.start()
    health.start()
    print 'Started gathering varnish data'
    
    web.start()
    
    processes = [stats, health, web]
    
    try:
        while True:
            time.sleep(1)
            for process in processes:
                process.check()
    except KeyboardInterrupt:
        pass
        
    print 'Ending gathering of varnish data'
