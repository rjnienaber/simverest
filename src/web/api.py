from bottle import Bottle, redirect, request, response
import bottle
import utils
from data.server_state import ServerState

api = Bottle()
api.VARNISH_STATE = ServerState()


@api.route('/')
def redirect_api_servers():
    redirect("/api/servers")


@api.route('/servers')
def servers():
    return api.VARNISH_STATE.get_servers()


@api.route('/server/:name')
def server_stats(name):
    backends = api.VARNISH_STATE.get_backends(name)
    if backends == {}:
        return {}

    varnishstats = api.VARNISH_STATE.get_varnishstats(name)
    stats = {'process': api.VARNISH_STATE.get_process(name),
             'varnishstats': varnishstats['varnishstats'],
             'backends': backends['backends'],
             'timestamp': utils.get_timestamp()}
    return stats


@api.route('/server/:name/backends')
def server_backends(name):
    return api.VARNISH_STATE.get_backends(name)


@api.route('/server/:name/backend/:backend_name')
def server_backend(name, backend_name):
    return api.VARNISH_STATE.get_backend(name, backend_name)


@api.route('/server/:name/backend/:backend_name/:key')
def server_backend_key(name, backend_name, key):
    backend = server_backend(name, backend_name)
    if backend == {}:
        return 'Backend info not found'

    return backend[key]


@api.route('/server/:name/process')
def server_process(name):
    return api.VARNISH_STATE.get_process(name)


@api.route('/server/:name/process/:key')
def server_process_key(name, key):
    process = server_process(name)
    if not key in process:
        return 'Process stat not found'

    return process[key]


@api.route('/server/:name/varnishstats')
def server_varnishstats(name):
    return api.VARNISH_STATE.get_varnishstats(name)


@api.route('/server/:name/varnishstats/:stat_name')
def server_varnishstats_key(name, stat_name):
    stats = server_varnishstats(name)
    if stats == {}:
        return {}

    for stat in stats['varnishstats']:
        if stat['name'] == stat_name:
            return str(stat['value'])

    return 'Varnish stat not found'
