from datetime import datetime
from contextlib import closing
import json
import utils
from .base import CollectorBase


class VarnishHealth(CollectorBase):
    def __init__(self, host, username, password, hostname, server_state):
        super(VarnishHealth, self).__init__(host, username, password,
              hostname, server_state)
        self.backends = {}

        varnishlog_command = "varnishlog -u -m Backend_health:.* | " \
                             "grep --line-buffered -E 'sick|healthy' | " \
                             "cut -d' ' -f 8,10,18-"

        self.health_command = varnishlog_command

    def process(self, ssh):
        try:
            with closing(ssh.get_transport()) as transport:
                with closing(transport.open_session()) as channel:
                    channel.get_pty()
                    channel.exec_command(self.health_command)
                    stdout = channel.makefile('rb', 0)

                    #this line should loop indefinitely as
                    #varnishlog never completes
                    for line in stdout:
                        if self.should_continue:
                            self._process_line(line.strip())
                        else:
                            break
        finally:
            print('Health collecting ending')

    def _process_line(self, line):
        """'line' should be in this format: 
        <webserver> <healthy|sick> <http status code> <http status text>"""
        
        self._process_status(*line.strip().split(' ', 3))

    def _process_status(self, host, state, status_code='', status_text=''):
        if host in self.backends:
            status = self.backends[host]
            if status['state'] != state:
                status['last_change'] = datetime.now()
                status['state'] = state
            self.server_state.update_backend(self.hostname, host, state, 
                                             status_code, status_text)
        else:
            self.backends[host] = {'state': state,
                                   'last_change': datetime.now()}
            self.server_state.update_backend(self.hostname, host, state, 
                                             status_code, status_text)
