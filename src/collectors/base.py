from contextlib import closing
import utils

class CollectorBase(object):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.should_continue = True

    def process_data(self):
        with closing(utils.start_ssh(self.host, self.username, self.password)) as ssh:
            self.process(ssh)

    def stop(self):
        self.should_continue = False