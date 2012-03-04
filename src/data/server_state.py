import utils
from datetime import datetime

BACKEND_KEY = 'backends'
PROCESS_KEY = 'process'
VARNISH_STAT_KEY = 'varnishstat'

class ServerState(object):
    def __init__(self):
        self.servers = {}

    def _get_server(self, hostname):
        if not hostname in self.servers:
            default_process = {'virtualmem': '0m', 'reservedmem': '0m', 'cpu': '0.0', 'memory': '0.0'}
            self.servers[hostname] = {BACKEND_KEY:[], 
                                      PROCESS_KEY: default_process, 
                                      VARNISH_STAT_KEY: []}
            
        return self.servers[hostname]

    def get_servers(self):
        return {'servers': sorted([s for s in self.servers])}
        
    def update_backend(self, hostname, backend_name, state):
        backend = self.get_backend(hostname, backend_name)
        if backend == {}:
            server = self._get_server(hostname)
            server[BACKEND_KEY].append({'name': backend_name, 'state': state, 'timestamp': utils.get_timestamp()})
        else:
            backend['state'] = state
            backend['timestamp'] = utils.get_timestamp()
        
    def get_backend(self, hostname, backend_name):
        if not hostname in self.servers:
            return {}
        
        server = self.servers[hostname]
        for backend in server[BACKEND_KEY]:
            if backend['name'] == backend_name:
                return backend
        return {}

    def get_backends(self, hostname):
        if not hostname in self.servers:
            return {}
        
        return {'backends': self.servers[hostname][BACKEND_KEY]}
    
    def update_process(self, hostname, virtualmem, reservedmem, cpu, memory):
        process = self._get_server(hostname)[PROCESS_KEY]
        process['virtualmem'] = virtualmem
        process['reservedmem'] = reservedmem
        process['cpu'] = cpu
        process['memory'] = memory
        
    def get_process(self, hostname):
        if not hostname in self.servers:
            return {}
        
        return self.servers[hostname][PROCESS_KEY]
    
    def update_varnishstats(self, hostname, varnishstats):
        server = self._get_server(hostname)
        server[VARNISH_STAT_KEY] = varnishstats
        
    def get_varnishstats(self, hostname):
        if not hostname in self.servers:
            return {}
        
        return {'varnishstats': self.servers[hostname][VARNISH_STAT_KEY]}
