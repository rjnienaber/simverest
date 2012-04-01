import time
import sys
import os
from collectors.health import VarnishHealth
from collectors.stats import VarnishStats
from web import http_server
from data.server_state import ServerState
from workers import Worker, WorkerMonitor
from data.options import get_config
import utils

def add_server(monitor, server_config, server_state, stat_window):
    hostname = utils.ssh_exec_command('hostname', **server_config)

    host, user, password = server_config['host'], server_config['username'], server_config['password']
    stats = VarnishStats(host, user, password, hostname, server_state, 
                         stat_window)  
    
    stat_name = 'Stats [{0}]'.format(host)
    monitor.add_worker(Worker(stat_name, stats.process_data, stats.stop))

    health_name = 'Health [{0}]'.format(host)
    health = VarnishHealth(host, user, password, hostname, server_state)
    monitor.add_worker(Worker(health_name, health.process_data, health.stop))

def main(config, static_path):
    hostname = 'testing'
    monitor = WorkerMonitor()
    server_state = ServerState()
    if not config['test']:
        for server_config in config['servers']:
            add_server(monitor, server_config, server_state, config['stat_window'])
        print('Started gathering varnish data')

    else:
        from tests.data_generator import DummyDataGenerator
        dummydata = DummyDataGenerator(server_state)
        worker = Worker('Testing', dummydata.update_files, dummydata.stop)
        monitor.add_worker(worker)

    Worker('WorkerMonitor', monitor.start, monitor.stop).start()
    http_server.start(server_state, static_path, config['port'], config['wsgi_server'])

    print('Simverest stopping...')
    monitor.stop()

if __name__ == "__main__":
    static_path = os.path.join(os.path.dirname(__file__), 'web', 'static')
    main(get_config(), static_path)
