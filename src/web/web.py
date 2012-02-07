from bottle import Bottle, view
import json
import utils

web = Bottle()

@web.route('/')
@view('default')
def basic_view():
    view_data = json.loads(utils.read_json(utils.HEALTH_JSON_FILE))
    view_data.update(json.loads(utils.read_json(utils.STATS_JSON_FILE)))
    return view_data