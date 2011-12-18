import time
from datetime import datetime
import json
import copy
from xml.etree import ElementTree

class VarnishStats:
    def __init__(self):
        counters = ['client_conn', 'client_req', 'cache_hit', 'cache_hitpass', 
            'cache_miss', 'client_drop', 'backend_conn']
        
        counter_list = ','.join(counters)
        self.varnish_command = 'varnishstat -x -f ' + counter_list
        self.counter_records = []
        self.record_limit = 10

    def process(self, ssh):
        while True:
            varnish_counters = self._get_current_varnish_counters(ssh)
            varnish_stats = self._process_varnish_counters(varnish_counters)
            varnish_stats['process'] = self._get_process_stats(ssh)
            
            self._write_stats(varnish_stats)
            
            time.sleep(1)
            
    def _get_current_varnish_counters(self, ssh):
        stdin, stdout, stderr = ssh.exec_command(self.varnish_command)
        varnish_stats_xml = stdout.read()
        tree = ElementTree.fromstring(varnish_stats_xml)

        stat_elements = tree.findall('stat')
        stats = []
        for stat in stat_elements:
            children = stat.getchildren()
            name = children[0].text
            
            counter = {'name': name,
                     'value': int(children[1].text),
                     'description': children[3].text}
            stats.append(counter)
        
        return {'timestamp': datetime.strptime(tree.attrib['timestamp'],'%Y-%m-%dT%H:%M:%S'), 
                'varnish': stats}

    def _process_varnish_counters(self, varnish_counters):
        self.counter_records.insert(0, copy.deepcopy(varnish_counters))
        record_count = len(self.counter_records)

        newest, oldest =  self.counter_records[0], self.counter_records[-1]
        period = float((newest['timestamp'] - oldest['timestamp']).seconds)

        if record_count == 1 or period == 0:
            for counter in varnish_counters['varnish']:
                counter['value'] = 0
            return varnish_counters

        joined = zip(newest['varnish'], oldest['varnish'], varnish_counters['varnish'])
        for join in joined:
            assert join[0]['name'] == join[1]['name'] == join[2]['name']
            difference = join[0]['value'] - join[1]['value']
            join[2]['value'] = difference / period

        if record_count == self.record_limit:
            self.counter_records.pop()
            
        return varnish_counters
    
    def _get_process_stats(self, ssh):
        stdin, stdout, stderr = ssh.exec_command('top -b -n 1 -d 1 -U nobody | grep varnishd')
        top_stats = stdout.readline().split()
        return {'cpu': top_stats[8], 'memory':top_stats[9],  
                'virtualmem': top_stats[4], 'reservedmem': top_stats[5]}

    def _write_stats(self, data):
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
        with open('stats.json', 'w') as stats_dump:
            json.dump(data, stats_dump, indent=2, default=dthandler)    