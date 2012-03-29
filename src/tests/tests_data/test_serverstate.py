import os
import unittest
from data.server_state import ServerState
import mock
from datetime import datetime

class ServerStateTests(unittest.TestCase):
    def test_should_return_empty_dict_for_unknown_hostname_for_backend(self):
        state = ServerState()

        backend_state = state.get_backend('varnish1', 'web1')

        self.assertEquals({}, backend_state)

    def test_should_return_empty_dict_for_unknown_backend(self):
        state = ServerState()

        state.update_backend('varnish1', 'web2', 'healthy', '200', 'OK')

        backend_state = state.get_backend('varnish1', 'web1')

        self.assertEquals({}, backend_state)

    @mock.patch('utils.now')
    def test_should_update_backend_state(self, now_mock):
        now_mock.return_value = datetime(2011, 10, 0o1)
        state = ServerState()

        state.update_backend('varnish1', 'web2', 'healthy', '200', 'OK')

        backend_state = state.get_backend('varnish1', 'web2')

        self.assertEquals({'name': 'web2', 'state': 'healthy',
                           'status_code': '200', 'status_text': 'OK',
                           'timestamp': '2011-09-30T23:00:00Z'},
                           backend_state)

    @mock.patch('utils.now')
    def test_should_update_existing_backend_state(self, now_mock):
        now_mock.return_value = datetime.now()
        state = ServerState()

        state.update_backend('varnish1', 'web2', 'healthy', '200', 'OK')

        now_mock.return_value = now = datetime(2011, 10, 0o1)
        state.update_backend('varnish1', 'web2', 'sick', '500', 
                                         'Internal Server Error')
        backend_state = state.get_backend('varnish1', 'web2')

        self.assertEquals({'name': 'web2', 'state': 'sick',
                           'status_code': '500', 
                           'status_text': 'Internal Server Error',
                           'timestamp': '2011-09-30T23:00:00Z'},
                           backend_state)

    def test_should_return_empty_dict_for_unknown_hostname_for_process(self):
        state = ServerState()

        process_state = state.get_process('varnish1')

        self.assertEquals({}, process_state)

    def test_should_return_zero_values_for_empty_process(self):
        state = ServerState()

        state._get_server('varnish1')
        process_state = state.get_process('varnish1')
        
        self.assertEquals({'virtualmem_mb': 0, 'reservedmem_mb': 0,
                           'cpu': 0.0, 'memory': 0.0}, process_state)

    def test_should_update_process_state(self):
        state = ServerState()

        state.update_process('varnish1', '410m', '109m', '2.0', '2.8')
        process_state = state.get_process('varnish1')

        self.assertEquals({'virtualmem_mb': 410, 'reservedmem_mb': 109,
                           'cpu': 2.0, 'memory': 2.8}, process_state)

    def test_should_update_existing_process_state(self):
        state = ServerState()

        state.update_process('varnish1', '410m', '109m', '2.0', '2.8')
        state.update_process('varnish1', '510m', '209m', '3.0', '3.8')
        process_state = state.get_process('varnish1')

        self.assertEquals({'virtualmem_mb': 510, 'reservedmem_mb': 209,
                           'cpu': 3.0, 'memory': 3.8}, process_state)

    def test_should_return_empty_dict_for_unknown_hostname_for_stat(self):
        state = ServerState()

        process_state = state.get_varnishstats('varnish1')

        self.assertEquals({}, process_state)

    def test_should_return_empty_list_when_no_varnish_stat_values(self):
        state = ServerState()

        state._get_server('varnish1')
        process_state = state.get_varnishstats('varnish1')

        self.assertEquals({'varnishstats': []}, process_state)

    def test_should_update_varnish_stats(self):
        state = ServerState()

        state.update_varnishstats('varnish1', [{'name': 'conns', 'value': 34.3,
                                  'description': 'connections'}])
        process_state = state.get_varnishstats('varnish1')

        self.assertEquals({'varnishstats': [{'name': 'conns', 'value': 34.3,
                           'description': 'connections'}]}, process_state)

    def test_should_return_empty_dict_of_servers(self):
        state = ServerState()

        servers = state.get_servers()

        self.assertEquals({'servers': []}, servers)

    def test_should_return_dict_of_servers(self):
        state = ServerState()

        state._get_server('varnish1')
        state._get_server('varnish2')
        servers = state.get_servers()

        self.assertEquals({'servers': ['varnish1', 'varnish2']}, servers)

    def test_should_return_empty_dict_for_unknown_hostname_for_backends(self):
        state = ServerState()

        process_state = state.get_backends('varnish1')

        self.assertEquals({}, process_state)

    def test_should_return_empty_list_when_no_backends(self):
        state = ServerState()

        state._get_server('varnish1')
        process_state = state.get_backends('varnish1')

        self.assertEquals({'backends': []}, process_state)

    @mock.patch('utils.now')
    def test_should_return_all_backends(self, now_mock):
        now_mock.return_value = datetime(2011, 10, 0o1)
        now = '2011-09-30T23:00:00Z'
        state = ServerState()

        state.update_backend('varnish1', 'web2', 'healthy', '200', 'OK')
        state.update_backend('varnish1', 'web1', 'healthy', '200', 'OK')
        backends = state.get_backends('varnish1')

        expected = {'backends': [{'name': 'web2', 'state': 'healthy',
                                  'status_code': '200', 'status_text': 'OK',
                                  'timestamp': now},
                                 {'name': 'web1', 'state': 'healthy',
                                  'status_code': '200', 'status_text': 'OK',
                                  'timestamp': now}]}

        self.assertEquals(expected, backends)
