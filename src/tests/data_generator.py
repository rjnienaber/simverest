import utils
import time
import json
import random
from datetime import datetime
from threading import Thread
from collectors import stats

FAKE_BACKEND_NAMES = ['FAKE-BACKEND1', 'FAKE-BACKEND2', 'FAKE-BACKEND3']
FAKE_SERVER_NAMES = ['TEST-SERVER1', 'TEST-SERVER2', 'TEST-SERVER3']
FAKE_HTTP_CODES = {'200': 'OK', '302':'Found', '404': 'Not Found', 
                   '500':'Internal Server Error', '':''}

class DummyDataGenerator:
    def __init__(self, server_state):
        self.server_state = server_state
        self.should_continue = True

    def start(self):
        server_state = self.server_state
        print('Generating test data')
        
        for server in FAKE_SERVER_NAMES:
            for backend_name in FAKE_BACKEND_NAMES:
                server_state.update_backend(server, backend_name, 'healthy', 
                                            '200',
                                            FAKE_HTTP_CODES['200'])
        
        while self.should_continue:
            for server in FAKE_SERVER_NAMES:
                self.generate_fake_data(server, server_state)

            time.sleep(1)

        print('Ending test thread')
        
    def generate_fake_data(self, server, server_state):
        #randomly make a server change status every 10 seconds
        if random.randint(1, 10) % 2 == 0:
            backend_name = random.choice(FAKE_BACKEND_NAMES)
            state = random.choice(['healthy', 'sick'])
            if state == 'sick':
                codes = FAKE_HTTP_CODES.keys()
                codes.remove('200')
                status_code = random.choice(codes)
            else:
                status_code = '200'
            server_state.update_backend(server, backend_name, state, 
                                        status_code, 
                                        FAKE_HTTP_CODES[status_code])

        #update stats
        cpu = random.random() * 25
        server_state.update_process(server, '1400m', '234m', cpu, 4.5)

        counter = 0
        varnishstats = []
        for varnish_counter in stats.VARNISH_COUNTERS:
            value = random.random() * 400
            counter += 1
            description = 'Counter ' + str(counter)
            varnishstats.append({'name': varnish_counter, 'value': value, 
                                 'description': description})
                          
        server_state.update_varnishstats(server, varnishstats)

    def stop(self):
        self.should_continue = False
    
    def last_update(self):
        return datetime.now()