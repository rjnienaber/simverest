import time
import json
from elementtree import ElementTree

class VarnishStats:
    def __init__(self):
        counters = ['client_conn', 'client_req', 'cache_hit', 'cache_hitpass', 
            'cache_miss', 'client_drop', 'backend_conn']
        
        counter_list = ','.join(counters)
        self.varnish_command = 'varnishstat -x -f ' + counter_list
        
    def process(self, ssh):
        while True:
            varnish_stats = self._get_varnish_stats(ssh)
            varnish_stats['process'] = self._get_process_stats(ssh)
            
            self._write_stats(varnish_stats)
            
            time.sleep(1)
            
    def _get_process_stats(self, ssh):
        stdin, stdout, stderr = ssh.exec_command('top -b -n 1 -d 1 -U nobody | grep varnishd')
        top_stats = stdout.readline().split()
        return {'cpu': top_stats[8], 'memory':top_stats[9],  
                'virtualmem': top_stats[4], 'reservedmem': top_stats[5]}
    
    def _convert_string(self, value):
        return int(value) if value.isdigit() else value
    
    def _get_varnish_stats(self, ssh):
        stdin, stdout, stderr = ssh.exec_command(self.varnish_command)
        varnish_stats_xml = stdout.read()
        tree = ElementTree.fromstring(varnish_stats_xml)

        stat_elements = tree.findall('stat')
        stats = []
        for stat in stat_elements:
            children = stat.getchildren()
            name = children[0].text
            
            counter = {'name': name,
                     'value': self._convert_string(children[1].text),
                     'description': children[3].text}
            stats.append(counter)
        
        return {'timestamp': tree.attrib['timestamp'], 
                'varnish': stats}

    def _write_stats(self, data):
        with open('stats.json', 'w') as stats_dump:
            json.dump(data, stats_dump, indent=2)    