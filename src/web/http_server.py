from bottle import Bottle, run
import bottle
import os

from middleware import RemoveTrailingSlashesMiddleware, JSONPCallbackMiddleware
from api import api
from web import web


def start(server_state, static_path, port, server, host='0.0.0.0',
          debug=False):
    bottle.debug(debug)
    template_path = os.path.join(os.path.dirname(__file__), 'views')
    bottle.TEMPLATE_PATH.append(template_path)

    api.VARNISH_STATE = server_state
    web.STATIC_PATH = static_path

    web.mount('/api', api)

    jsonp_enabled_app = JSONPCallbackMiddleware(web)
    stripped_slashes_app = RemoveTrailingSlashesMiddleware(jsonp_enabled_app)
    print 'Starting web server on {0} and port {1}'.format(host, port)
    run(stripped_slashes_app, host=host, port=port, quiet=True, server=server)
