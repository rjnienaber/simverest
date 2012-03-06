import utils
import time
import json
import random
from datetime import datetime
from threading import Thread

should_continue = True


def update_files():
    try:
        health_data = json.loads(utils.read_json(utils.HEALTH_JSON_FILE))
        health_data['name'] = 'testing'
        stats_data = json.loads(utils.read_json(utils.STATS_JSON_FILE))
        print 'Generating test data'
        while should_continue:
            #randomly make a server change status every 10 seconds
            if random.randint(1, 10) == 3:
                health_data['last_update'] = datetime.now()
                index = random.randint(0, 4)
                backend = health_data['backends'][index]

                state = 'healthy' if backend['state'] == 'sick' else 'sick'
                backend['state'] = state
                backend['last_change'] = datetime.now()

                utils.dump_data(health_data, utils.HEALTH_JSON_FILE)

            #update stats
            stats_data['process']['cpu'] = random.randint(0, 10)
            for counter in stats_data['varnish']:
                counter['value'] = random.random() * 100

            utils.dump_data(stats_data, utils.STATS_JSON_FILE)

            time.sleep(1)
    except KeyboardInterrupt:
        pass

    print 'Ending test thread'


def stop():
    should_continue = False
