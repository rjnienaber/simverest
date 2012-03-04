import cgi, itertools
from StringIO import StringIO

class RemoveTrailingSlashesMiddleware(object):
    '''Middleware to strip and redirect any links with trailing slashes'''
    def __init__(self, app):
        self.app = app
    def __call__(self, e, h):
        url = e['PATH_INFO']
        if url != '/' and url.endswith('/'):
            h('303 See Other', [('Location', url.rstrip('/'))])
            return []

        return self.app(e,h)

class JSONPCallbackMiddleware(object):
    '''Adds JSONP support for ajax calls'''
    def __init__(self, app):
        self.app = app
        self.callback_query_parameters = ['jsonp', 'callback']
        self.javascript_mime_types = ['text/javascript', 'application/javascript', 'application/ecmascript', 'application/x-ecmascript']

    def __call__(self, environ, start_response):
        if not 'HTTP_X_REQUESTED_WITH' in environ or 'XMLHttpRequest' != environ['HTTP_X_REQUESTED_WITH']:
            return self.app(environ, start_response)
            
        if not 'QUERY_STRING' in environ or not any(p in environ['QUERY_STRING'] for p in self.callback_query_parameters):
            return self.app(environ, start_response)
        
        if not 'HTTP_ACCEPT' in environ or not any(m in environ['HTTP_ACCEPT'] for m in self.javascript_mime_types):
            return self.app(environ, start_response)
    
        buffer = StringIO()
        def custom_start_response(status, headers, exc_info=None):
            return buffer
    
        result = list(self.app(environ, custom_start_response))

        query_string = cgi.parse_qs(environ['QUERY_STRING'].lstrip('?'))
        callback_name = query_string['callback'] if 'callback' in query_string else query_string['jsonp']

        start = callback_name[0] + '('
        length = len(start) + len(result[0]) + 1
        start_response('200 OK', [('Content-Length', str(length))])
        return itertools.chain.from_iterable([[start], result, [')']])
