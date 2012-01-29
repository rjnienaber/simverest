from bottle import Bottle, run, view, redirect, static_file, request, response
import bottle
import json
import utils
import time

from middleware import RemoveTrailingSlashesMiddleware

_varnish_hosts = {}
app = Bottle()

@app.route('/api')
def redirect_api_servers():
    redirect("/api/servers")

@app.route('/api/servers')
def list_servers():
    return _varnish_hosts

@app.route('/api/server/:name/backends')
def server_health(name):
    return process_jsonp(utils.HEALTH_JSON_FILE)

@app.route('/api/server/:name/stats')
def server_stats(name):
    return process_jsonp(utils.STATS_JSON_FILE)

def process_jsonp(file_path):
    response.content_type = 'application/json'
    return '{0}({1})'.format(request.query.callback, read_json(utils.HEALTH_JSON_FILE))
    
def read_json(file_path):
    while True:
        data = utils.read_all(file_path)
        if data != '':
            return data
        time.sleep(0.5)
    
@app.route('/')
@view('default')
def basic_view():
    view_data = json.loads(read_json(utils.HEALTH_JSON_FILE))
    view_data.update(json.loads(read_json(utils.STATS_JSON_FILE)))
    return view_data

def start(varnish_hosts, host='0.0.0.0', port=8080, debug=False):
    bottle.debug(debug)
    _varnish_hosts['servers'] = varnish_hosts
    
    stripped_slashes_app = RemoveTrailingSlashesMiddleware(app)
    print 'Starting web server on {0} and port {1}'.format(host, port)
    run(stripped_slashes_app, host=host, port=port, quiet=True)
