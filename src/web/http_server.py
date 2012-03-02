from bottle import Bottle, run
import bottle
import os

from middleware import RemoveTrailingSlashesMiddleware, JSONPCallbackMiddleware
from api import api
from web import web

def start(varnish_hosts, port, server, host='0.0.0.0', debug=False):
    bottle.debug(True)
    bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), 'views'))
    
    api.VARNISH_HOSTS['servers'] = varnish_hosts
    web.STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    
    web.mount('/api', api)
    
    jsonp_enabled_app = JSONPCallbackMiddleware(web)
    stripped_slashes_app = RemoveTrailingSlashesMiddleware(jsonp_enabled_app)
    print 'Starting web server on {0} and port {1}'.format(host, port)
    run(stripped_slashes_app, host=host, port=port, quiet=True, server=server)