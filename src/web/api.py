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
def list_servers():
    return api.VARNISH_STATE.get_servers()

@api.route('/server/:name/backends')
def server_backends(name):
    return api.VARNISH_STATE.get_backends(name)

@api.route('/server/:name/stats')
def server_stats(name):
    stats = {'process': api.VARNISH_STATE.get_process(name),
             'varnishstats': api.VARNISH_STATE.get_varnishstats(name),
             'timestamp': utils.get_timestamp()}
    return stats
    

    



