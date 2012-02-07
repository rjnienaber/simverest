from bottle import Bottle, view, static_file
import json
import utils
from os import path

web = Bottle()
web.STATIC_PATH = ''

@web.route('/simple')
@view('simple')
def basic_view():
    view_data = json.loads(utils.read_json(utils.HEALTH_JSON_FILE))
    view_data.update(json.loads(utils.read_json(utils.STATS_JSON_FILE)))
    return view_data
    
@web.route('/')
def basic_view():
    return static_file('dashboard.html', path.join(web.STATIC_PATH, 'html'))
    
@web.route('/static/<static_path:path>')
def static_files(static_path):
    if '..' in static_path:
        return ''
        
    file_name = path.basename(static_path)
    file_path = path.join(web.STATIC_PATH, path.dirname(static_path))
    
    return static_file(file_name, file_path)