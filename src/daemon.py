import time, sys, os
from collectors.health import VarnishHealth
from collectors.stats import VarnishStats
from web import http_server
from data.server_state import ServerState
from workers import Worker, WorkerMonitor
from options import get_arguments
import utils

def main(arguments, static_path):
    hostname = 'testing'
    monitor = WorkerMonitor()
    server_state = ServerState()
    if not arguments.test:
        host, user, password = arguments.host, arguments.username, arguments.password
        hostname = hostname = utils.ssh_exec_command('hostname', host=host, username=user, password=password)

        stats = VarnishStats(host, user, password, hostname, server_state)
        monitor.add_worker(Worker('Stats', stats.process_data, stats.stop))
        
        health = VarnishHealth(host, user, password, hostname, server_state)
        monitor.add_worker(Worker('Health', health.process_data, health.stop))
        
        print 'Started gathering varnish data'
        
    else:
        import testing
        monitor.add_worker(Worker('Testing', testing.update_files, testing.stop))
        print 'Started generating test data'

    Worker('WorkerMonitor', monitor.start, monitor.stop).start()
    http_server.start(server_state, static_path, arguments.port, arguments.wsgi_server)
    
    print 'Simverest stopping...'
    monitor.stop()

if __name__ == "__main__":
    static_path = os.path.join(os.path.dirname(__file__), 'web', 'static')
    main(get_arguments(), static_path)
