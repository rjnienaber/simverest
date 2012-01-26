from bottle import route, run, view
import bottle
import json
import utils
import time

_varnish_hosts=[]

@route('/api/servers')
def list_servers():
    return json.dumps(_varnish_hosts)
    
@route('/api/server/:name/backends')
def server_health(name):
    return read_json(utils.HEALTH_JSON_FILE)

@route('/api/server/:name/stats')
def server_stats(name):
    return read_json(utils.STATS_JSON_FILE)

def read_json(filePath):
    '''Sometimes the file can be in the middle of being written and will return an empty value.
    This function will wait half a second and then retry and won't return until it has a read a non-empty value'''
    while True:
        varnish_values = utils.read_all(filePath)
        if varnish_values != '':
            return varnish_values
        time.sleep(0.5)
    
@route('/')
@view('default')
def basic_view():
    health = json.loads(server_health(None))
    health.update(json.loads(server_stats(None)))
    return health
        
def start(varnish_hosts, host='0.0.0.0', port=8080, debug=False):
    bottle.debug(debug)
    del _varnish_hosts[:]
    _varnish_hosts.extend(varnish_hosts)
    
    print 'Starting web server on {0} and port {1}'.format(host, port)
    run(host=host, port=port, quiet=True)