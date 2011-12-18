from datetime import datetime
from contextlib import closing
import json

class VarnishHealth:
    def __init__(self):
        self.backends = {}
        
        #we keep a count of how many lines processed so we dump the status regularly
        self.lines_processed = 0

    def process(self, ssh):
        with closing(ssh.get_transport()) as transport:
            with closing(transport.open_session()) as channel:
                channel.get_pty()
                channel.exec_command("unbuffer varnishlog | grep --line-buffered -E 'sick|healthy' | awk '{print $4,$6; fflush();}'")
                stdout = channel.makefile('rb', 0)
                
                #this line should loop indefinitely as the varnishlog never completes
                for line in stdout:
                    print line.strip()
                    self._process_line(line.strip())
    
    def _process_line(self, line):
        """'line' should be in this format: webserver Still healthy"""
        fragments = line.split()
        if (len(fragments) != 2): 
            return
            
        host, state = fragments

        result = self._check_status(host, state)
        if (result or self.lines_processed == 100):
            self._write_status()
            self.lines_processed = 0
            
        self.lines_processed += 1
        
    def _check_status(self, host, state):
        if host in self.backends:
            status = self.backends[host]
            has_changed = status['state'] != state
            if has_changed:
                status['last_change'] = datetime.now()
                status['state'] = state
            return has_changed     
        
        self.backends[host] = {'state': state, 'last_change': datetime.now()}
        return True
        
    def _write_status(self):
        data = {'backends': self.backends, 'last_update': datetime.now()}
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
        with open('health.json', 'w') as health_dump:
            json.dump(data, health_dump, indent=2, default=dthandler)    
    
    
        