import time, sys, os
from contextlib import closing
from collectors.health import VarnishHealth
from collectors.stats import VarnishStats
from web import http_server
from subprocess import SubProcess
from options import get_arguments
import utils


def process_data(host, username, password, varnish):
    try:
        with closing(utils.start_ssh(host, username, password)) as ssh:
            varnish.process(ssh)
    except KeyboardInterrupt:
        pass

def start_web_server(varnish_hosts, port=8080, server='wsgiref'):
    try:
        http_server.start(varnish_hosts, port, server)
    except KeyboardInterrupt:
        pass
        
if __name__ == "__main__":
    utils.set_json_path(os.getcwd())
    
    arguments = get_arguments()
    
    hostname = 'testing'
    processes = []
    if not arguments.test:

        details = (arguments.host, arguments.username, arguments.password)
        hostname = hostname = utils.ssh_exec_command('hostname', host=details[0], username=details[1], password=details[2])
    
        stats = SubProcess('Stats', process_data, details + (VarnishStats(hostname),))
        health = SubProcess('Health', process_data, details + (VarnishHealth(hostname, False),))
        stats.start()
        health.start()
        print 'Started gathering varnish data'
        
        processes += [stats, health]
        
    web = SubProcess('Web', start_web_server, [hostname], {'port': arguments.port, 'server':arguments.wsgi_server})
    web.start()
    
    processes.append(web)
    
    try:
        while True:
            time.sleep(1)
            for process in processes:
                process.check()
    except KeyboardInterrupt:
        pass
        
    print 'Ending gathering of varnish data'
