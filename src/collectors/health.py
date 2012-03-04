from datetime import datetime
from contextlib import closing
import json
import utils
from base import CollectorBase

class VarnishHealth(CollectorBase):
    def __init__(self, host, username, password, hostname, server_state, use_unbuffer=False):
        super(VarnishHealth, self).__init__(host, username, password, hostname, server_state)
        self.backends = {}

        varnishlog_command = "varnishlog | grep --line-buffered -E 'sick|healthy' | awk '{print $4,$6; fflush();}'"
        self.health_command = 'unbuffer ' + varnishlog_command if use_unbuffer else varnishlog_command

    def process(self, ssh):
        try:
            with closing(ssh.get_transport()) as transport:
                with closing(transport.open_session()) as channel:
                    channel.get_pty()
                    channel.exec_command(self.health_command)
                    stdout = channel.makefile('rb', 0)
                    
                    #this line should loop indefinitely as varnishlog never completes
                    for line in stdout:
                        if self.should_continue:
                            self._process_line(line.strip())
                        else:
                            break
        finally:
            print 'Health collecting ending'
    
    def _process_line(self, line):
        """'line' should be in this format: <webserver> healthy"""
        fragments = line.split()
        if (len(fragments) != 2): 
            return
            
        self._process_status(*fragments)
        
    def _process_status(self, host, state):
        if host in self.backends:
            status = self.backends[host]
            has_changed = status['state'] != state
            if has_changed:
                self.server_state.update_backend(self.hostname, host, state)
        else:
            self.server_state.update_backend(self.hostname, host, state)
