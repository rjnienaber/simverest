import cgi, itertools

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

    def _start_response(status, response_headers, exc_info=None):
        print status, response_headers
    
    def __call__(self, e, start_response):
        self.original_start_response = start_response
        result = list(self.app(e, start_response))
        
        if not 'HTTP_X_REQUESTED_WITH' in e or 'XMLHttpRequest' != e['HTTP_X_REQUESTED_WITH']:
            return result
            
        if not 'QUERY_STRING' in e or not any(p in e['QUERY_STRING'] for p in self.callback_query_parameters):
            return result
        
        if not 'HTTP_ACCEPT' in e or not any(m in e['HTTP_ACCEPT'] for m in self.javascript_mime_types):
            return result
        
        query_string = cgi.parse_qs(e['QUERY_STRING'].lstrip('?'))
        callback_name = query_string['callback'] if 'callback' in query_string else query_string['jsonp']
        
        start = callback_name[0] + '('
        length = len(start) + len(result[0]) + 1
        start_response('200 OK', [('Content-Length', str(length))])
        return itertools.chain.from_iterable([[start], result, [')']])
        '''value = ''.join(result)
        value = start + value + ')'
        
        return [start, result, ')']'''