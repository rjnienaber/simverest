import utils, time, json, random
from datetime import datetime
from threading import Thread

def update_files():
    try:
        health_data = json.loads(utils.read_json(utils.HEALTH_JSON_FILE))
        health_data['name'] = 'testing'
        stats_file = json.loads(utils.read_json(utils.STATS_JSON_FILE))
        print 'Generating test data'
        while True:
            if random.randint(1, 10) == 3:
                health_data['last_update'] = datetime.now()
                index = random.randint(0, 4)
                backend = health_data['backends'][index]

                backend['state'] = 'healthy' if backend['state'] == 'sick' else 'sick'
                backend['last_change'] = datetime.now()
                    
                utils.dump_data(health_data, utils.HEALTH_JSON_FILE)
        
            #utils.dump_data(varnish_stats, utils.STATS_JSON_FILE)
            
            time.sleep(1) 
    except KeyboardInterrupt:
        pass
    
    print 'Ending test thread'
        
def generate_test_data():    
    t = Thread(target=update_files)
    t.start()