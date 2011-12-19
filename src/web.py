from bottle import route, run, view
import bottle
import json
import utils

_varnish_hosts=[]

@route('/api/servers')
def list_servers():
    return json.dumps(_varnish_hosts)
    
@route('/api/server/:name/backends')
def server_health(name):
    with open(utils.HEALTH_JSON_FILE, 'r') as file:
        return file.read()

@route('/api/server/:name/stats')
def server_stats(name):
    with open(utils.STATS_JSON_FILE, 'r') as file:
        return file.read()

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