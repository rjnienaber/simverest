from bottle import Bottle, run
import bottle
import os

from .middleware import RemoveTrailingSlashesMiddleware, JSONPCallbackMiddleware, NoCacheMiddleware
from .api import api
from .web import web


def start(server_state, static_path, port, server, host='0.0.0.0',
          debug=False):
    bottle.debug(debug)
    template_path = os.path.join(os.path.dirname(__file__), 'views')
    bottle.TEMPLATE_PATH.append(template_path)

    api.VARNISH_STATE = server_state
    api.MOUNT_POINT = '/api'
    web.STATIC_PATH = static_path

    web.mount(api.MOUNT_POINT, api)

    #add middleware
    middlewares = [JSONPCallbackMiddleware, RemoveTrailingSlashesMiddleware,
                   NoCacheMiddleware]
    web_server = web
    for m in middlewares:
        web_server = m(web_server)
    
    print('Starting web server on {0} and port {1}'.format(host, port))
    run(web_server, host=host, port=port, quiet=True, server=server)
