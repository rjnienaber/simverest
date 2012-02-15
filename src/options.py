import argparse, sys

def add_optional_args(parser):
    parser.add_argument('-w', '--wsgi_server', help='The wsgi supporting http server to use e.g. paste, cherrypy, twisted', default='wsgiref')
    parser.add_argument('-p', '--port', help='The port to start the http server on e.g. 8080', type=int, default=8080)

def get_arguments():
    description = 'Simverest Varnish Dashboard'
    if '--test' in sys.argv:
        test_parser = argparse.ArgumentParser(description=description + ' (testing)')
        test_parser.add_argument('--test', action='store_true')
        add_optional_args(test_parser)
        return test_parser.parse_args()

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('host', help='The Varnish host to get stats from')
    parser.add_argument('username', help='The username required to connect to the Varnish host via ssh')
    parser.add_argument('password', help='The password required to connect to the Varnish host via ssh')
    add_optional_args(parser)

    args = parser.parse_args()
    args.__dict__['test'] = False
    return args
    
if __name__ == '__main__':
    print get_arguments()