import argparse
import sys
from os import path
import ConfigParser
from ConfigParser import ParsingError

def _add_required_args(parser):
    parser.add_argument('host', help='The Varnish host to get stats from')
    parser.add_argument('username', help='The username required to connect ' \
                                         'to the Varnish host via ssh')
    parser.add_argument('password', help='The password required to connect ' \
                                         ' to the Varnish host via ssh')

def _add_optional_args(parser, for_executable, for_test):
    default_web_server = 'twisted' if for_executable else 'wsgiref'
    
    parser.add_argument('-w', '--wsgi_server', help='The wsgi supporting' \
                        ' http server to use e.g. paste, cherrypy, ' \
                        'twisted', default=default_web_server)
    parser.add_argument('-p', '--port', help='The port to start the http ' \
                            'server on e.g. 8080', type=int, default=8080)
    parser.add_argument('-s', '--stat_window', help='The number of samples' \
                        ' to use in order to smooth the stats window e.g. 5', 
                        type=int, default=5)
    parser.add_argument('-c', '--config_file', help='An ini file that' \
                        'provides details of varnish serverst', default='')
    
    test_action = 'store_true' if for_test else 'store_false'
    parser.add_argument('--test', action=test_action, default=False)
    

def _parse_args(for_executable, args=None):
    description = 'Simverest Varnish Dashboard'
    
    has_test_argument = '--test' in args and not for_executable
    if has_test_argument:
        description += ' (testing)'

    parser = argparse.ArgumentParser(description=description)
    
    has_config = '-c' in args or '--config_file' in args
    must_add_required_args = not has_test_argument and not has_config
    if must_add_required_args:
        _add_required_args(parser)
    
    _add_optional_args(parser, for_executable, has_test_argument)

    options = parser.parse_args(args).__dict__
    if must_add_required_args:
        server = {'host': options['host'], 'username': options['username'],
                  'password': options['password']}
        del options['host']
        del options['username']
        del options['password']
        
        options['servers'] = [server]
    
    return options

    
def _parse_ini_file(filepath):
    config = ConfigParser.RawConfigParser()
    server_configs = []
    successful_read = False
    failure = False
    try:
        if path.exists(filepath):
            config.read(filepath)

            successful_read = True
            for section in config.sections():
                server_configs.append(dict(config.items(section)))
    except ParsingError:
        failure = True

    return {'successful_read': successful_read, 'failure': failure,
            'server_configs': server_configs}

def get_config(for_executable=False, args=None):
    args = args if args else sys.argv[1:]

    options = _parse_args(for_executable, args)
    
    config_file = options['config_file']
    if config_file != '':
        result = _parse_ini_file(config_file)
       
        if result['successful_read']:
            options['servers'] = result['server_configs']
        else:
            if result['failure']:
                sys.stderr.write("Could not parse '{0}'\n".format(config_file))
            else:
                sys.stderr.write("Could not read '{0}'\n".format(config_file))
            sys.exit(1)
       
    del options['config_file']
    return options   

    
def get_executable_config():
    return get_config(True)
