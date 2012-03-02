from bottle import Bottle, redirect, request, response
import bottle
import utils

api = Bottle()
api.VARNISH_HOSTS = {}

@api.route('/')
def redirect_api_servers():
    redirect("/api/servers")

@api.route('/servers')
def list_servers():
    return api.VARNISH_HOSTS

@api.route('/server/:name/backends')
def server_health(name):
    return read_json_file(utils.HEALTH_JSON_FILE)

@api.route('/server/:name/stats')
def server_stats(name):
    return read_json_file(utils.STATS_JSON_FILE)

def read_json_file(file_path):
    response.content_type = 'application/json'
    return utils.read_json(file_path)
    

    



