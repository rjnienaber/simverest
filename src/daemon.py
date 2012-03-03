import time, sys, os
from collectors.health import VarnishHealth
from collectors.stats import VarnishStats
from web import http_server
from workers import Worker, WorkerMonitor
from options import get_arguments
import utils

if __name__ == "__main__":
    utils.set_json_path(os.getcwd())
    
    arguments = get_arguments()
    
    hostname = 'testing'
    monitor = WorkerMonitor()
    if not arguments.test:
        host, user, password = arguments.host, arguments.username, arguments.password
        hostname = hostname = utils.ssh_exec_command('hostname', host=host, username=user, password=password)

        stats = VarnishStats(host, user, password, hostname)
        monitor.add_worker(Worker('Stats', stats.process_data, stats.stop))
        
        health = VarnishHealth(host, user, password, hostname)
        monitor.add_worker(Worker('Health', health.process_data, health.stop))
        
        print 'Started gathering varnish data'
        
    else:
        import testing
        monitor.add_worker(Worker('Testing', testing.update_files))
        print 'Started generating test data'

    Worker('WorkerMonitor', monitor.start, monitor.stop).start()
    http_server.start(hostname, arguments.port, arguments.wsgi_server)

    monitor.stop()
    print 'Ending gathering of varnish data'
