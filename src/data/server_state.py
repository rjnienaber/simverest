import utils
from datetime import datetime
import re

BACKEND_KEY = 'backends'
PROCESS_KEY = 'process'
VARNISH_STAT_KEY = 'varnishstat'


class ServerState(object):
    def __init__(self):
        self.servers = {}
        self.stats_matcher = re.compile('\d+')

    def _get_server(self, hostname):
        if not hostname in self.servers:
            default_process = {'virtualmem_mb': 0, 'reservedmem_mb': 0,
                               'cpu': 0.0, 'memory': 0.0}
            self.servers[hostname] = {BACKEND_KEY: [],
                                      PROCESS_KEY: default_process,
                                      VARNISH_STAT_KEY: []}

        return self.servers[hostname]

    def get_servers(self):
        return {'servers': sorted([s for s in self.servers])}

    def update_backend(self, hostname, backend_name, state, 
                                       status_code, status_text):
        backend = self.get_backend(hostname, backend_name)
        if backend == {}:
            server = self._get_server(hostname)
            server[BACKEND_KEY].append({'name': backend_name, 'state': state,
                                        'status_code': status_code, 
                                        'status_text': status_text,
                                        'timestamp': utils.get_timestamp()})
        else:
            backend['state'] = state
            backend['status_code'] = status_code
            backend['status_text'] = status_text
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
        parse_memory = lambda s: int(self.stats_matcher.findall(s)[0])
        process['virtualmem_mb'] = parse_memory(virtualmem)
        process['reservedmem_mb'] = parse_memory(reservedmem)
        process['cpu'] = float(cpu)
        process['memory'] = float(memory)

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
