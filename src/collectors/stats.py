import time
from datetime import datetime
from xml.etree import ElementTree
import utils
from .base import CollectorBase

VARNISH_COUNTERS = ['client_conn', 'client_req', 'cache_hit', 'cache_hitpass',
            'cache_miss', 'client_drop', 'backend_conn']

class VarnishStats(CollectorBase):
    def __init__(self, host, username, password, hostname, server_state, stats_window):
        super(VarnishStats, self).__init__(host, username, password,
                                           hostname, server_state)

        counters = ','.join(VARNISH_COUNTERS)
        self.varnish_command = 'varnishstat -x -f ' + counters
        self.counter_records = []
        self.record_limit = stats_window

    def process(self, ssh):
        try:
            while self.should_continue:
                self._process_varnishstats(ssh)
                self._process_top_stats(ssh)

                time.sleep(1)
        finally:
            print('Stats collecting ending')

    def _get_current_varnish_counters(self, ssh):
        varnish_stats_xml = utils.ssh_exec_command(self.varnish_command,
                                                   ssh=ssh)
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

        return {'timestamp': datetime.now(),
                'varnish': stats}

    def _process_varnishstats(self, ssh):
        varnish_counters = self._get_current_varnish_counters(ssh)

        self.counter_records.insert(0, varnish_counters)
        record_count = len(self.counter_records)

        newest, oldest = self.counter_records[0], self.counter_records[-1]
        period = float((newest['timestamp'] - oldest['timestamp']).seconds)

        #if we don't have enough periods to process, do nothing
        if record_count == 1 or period == 0:
            return

        #calculate averages for the period
        varnish_stats = []
        joined = list(zip(newest['varnish'], oldest['varnish']))
        for join in joined:
            assert join[0]['name'] == join[1]['name']
            difference = join[0]['value'] - join[1]['value']
            average = difference / period
            name, description = join[0]['name'], join[0]['description']
            varnish_stats.append({'name': name, 'value': average,
                                  'description': description})

        self.server_state.update_varnishstats(self.hostname, varnish_stats)

        #remove old records
        if record_count == self.record_limit:
            self.counter_records.pop()

        return varnish_counters

    def _process_top_stats(self, ssh):
        command = 'top -b -n 1 -d 1 -U nobody | grep varnishd'
        top_stats = utils.ssh_exec_command(command, ssh=ssh).split()

        stats = {'cpu': top_stats[8], 'memory': top_stats[9],
                'virtualmem': top_stats[4], 'reservedmem': top_stats[5]}
        self.server_state.update_process(self.hostname, **stats)
