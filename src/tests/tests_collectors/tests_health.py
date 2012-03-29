import os
import unittest
from collectors.health import VarnishHealth
import mock
from datetime import datetime


class VarnishHealthTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_should_handle_normal_state(self):
        server_state = MockServerState()
    
        health = VarnishHealth('', '', '', 'VARNISH1', server_state)
        health._process_line('WEB1 healthy 200 OK  ')
        
        self.assertEquals(('VARNISH1', 'WEB1', 'healthy', '200', 'OK'),
                           server_state.last_arguments)


    def test_should_put_http_text_as_a_phrase(self):
        server_state = MockServerState()

        health = VarnishHealth('', '', '', 'VARNISH1', server_state)
        health._process_line('WEB1 sick 500 Internal Server Error  ')

        self.assertEquals(('VARNISH1', 'WEB1', 'sick', '500', 
                           'Internal Server Error'), 
                           server_state.last_arguments)

    def test_should_handle_change_to_normal_state(self):
        server_state = MockServerState()
    
        health = VarnishHealth('', '', '', 'VARNISH1', server_state)
        health._process_line('WEB1 healthy  ')
        health._process_line('WEB1 healthy 302 Redirect')
        health._process_line('WEB1 healthy 500 Internal Server Error')
        health._process_line('WEB1 healthy 200 OK')
        
        self.assertEquals(('VARNISH1', 'WEB1', 'healthy', '200', 'OK'),
                           server_state.last_arguments)

                           
    def test_should_handle_error_state(self):
        server_state = MockServerState()
    
        health = VarnishHealth('', '', '', 'VARNISH1', server_state)
        health._process_line('WEB1 healthy')
        
        self.assertEquals(('VARNISH1', 'WEB1', 'healthy', '' ,''),
                           server_state.last_arguments)

    def test_should_handle_change_in_state_when_erroring(self):
        server_state = MockServerState()
    
        health = VarnishHealth('', '', '', 'VARNISH1', server_state)
        health._process_line('WEB1 healthy')
        health._process_line('WEB1 sick')
        
        self.assertEquals(('VARNISH1', 'WEB1', 'sick', '' ,''),
                           server_state.last_arguments)

class MockServerState(object):
    def update_backend(self, *args):
        self.last_arguments = args
