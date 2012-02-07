from bottle import Bottle, run, view, redirect, static_file, request, response
import bottle
import json
import utils
import time


api = Bottle()
api.varnish_hosts = {}

@api.route('/')
def redirect_api_servers():
    redirect("/api/servers")

@api.route('/servers')
def list_servers():
    return api.varnish_hosts

@api.route('/server/:name/backends')
def server_health(name):
    return process_jsonp(utils.HEALTH_JSON_FILE)

@api.route('/server/:name/stats')
def server_stats(name):
    return process_jsonp(utils.STATS_JSON_FILE)

def process_jsonp(file_path):
    response.content_type = 'application/json'
    return '{0}({1})'.format(request.query.callback, utils.read_json(file_path))
    

    



