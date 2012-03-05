import argparse, sys

def add_optional_args(parser, for_executable):
    if not for_executable:
        parser.add_argument('-w', '--wsgi_server', help='The wsgi supporting http server to use e.g. paste, cherrypy, twisted', default='wsgiref')
    parser.add_argument('-p', '--port', help='The port to start the http server on e.g. 8080', type=int, default=8080)

def build_parser(for_executable):
    description = 'Simverest Varnish Dashboard'
    if '--test' in sys.argv and not for_executable:
        test_parser = argparse.ArgumentParser(description=description + ' (testing)')
        test_parser.add_argument('--test', action='store_true')
        add_optional_args(test_parser, for_executable)
        return test_parser.parse_args()

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('host', help='The Varnish host to get stats from')
    parser.add_argument('username', help='The username required to connect to the Varnish host via ssh')
    parser.add_argument('password', help='The password required to connect to the Varnish host via ssh')
    add_optional_args(parser, for_executable)

    args = parser.parse_args()
    args.__dict__['test'] = False
    return args
    
def get_arguments():
    return build_parser(False)

def get_executable_arguments():
    arguments = build_parser(True)
    arguments.__dict__['wsgi_server'] = 'twisted'
    return arguments
    
if __name__ == '__main__':
    print get_executable_arguments()