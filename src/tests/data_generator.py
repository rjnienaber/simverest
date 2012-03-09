import utils
import time
import json
import random
from datetime import datetime
from threading import Thread
from collectors import stats

FAKE_BACKEND_NAMES = ['FAKE-BACKEND1', 'FAKE-BACKEND2', 'FAKE-BACKEND3']
FAKE_SERVER_NAME = 'TEST-SERVER'

class DummyDataGenerator:
    def __init__(self, server_state):
        self.server_state = server_state
        self.should_continue = True

    def update_files(self):
        server_state = self.server_state
        print('Generating test data')
        
        for backend_name in FAKE_BACKEND_NAMES:
            server_state.update_backend(FAKE_SERVER_NAME, backend_name, \
                                        'healthy')
        
        while self.should_continue:
            #randomly make a server change status every 10 seconds
            if random.randint(1, 10) == 3:
                backend_name = random.choice(FAKE_BACKEND_NAMES)
                state = random.choice(['healthy', 'sick'])
                server_state.update_backend(FAKE_SERVER_NAME, backend_name,
                                            state)

            #update stats
            cpu = random.random() * 25
            server_state.update_process(FAKE_SERVER_NAME,
                                        '1400m', '234m', cpu, 4.5)

            counter = 0
            varnishstats = []
            for varnish_counter in stats.VARNISH_COUNTERS:
                value = random.random() * 400
                counter += 1
                description = 'Counter ' + str(counter)
                varnishstats.append({'name': varnish_counter, 
                                     'value': value, 
                                     'description': description})
                              
            server_state.update_varnishstats(FAKE_SERVER_NAME, varnishstats)

            time.sleep(1)

        print('Ending test thread')


    def stop(self):
        self.should_continue = False    