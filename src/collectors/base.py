from contextlib import closing
import utils


class CollectorBase(object):
    def __init__(self, host, username, password, hostname, server_state):
        self.host = host
        self.username = username
        self.password = password
        self.should_continue = True
        self.hostname = hostname
        self.server_state = server_state

    def process_data(self):
        self.should_continue = True
        ssh_details = (self.host, self.username, self.password)
        with closing(utils.start_ssh(*ssh_details)) as ssh:
            self.process(ssh)

    def stop(self):
        self.should_continue = False
