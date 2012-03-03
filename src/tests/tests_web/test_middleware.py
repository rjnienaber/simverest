import os, unittest
from web.middleware import JSONPCallbackMiddleware

JSON_RESULT = ['{}']
QUERY_STRING = '?callback=jquery23423562352358'
HTTP_ACCEPT = 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01'

response_headers = []

class JSONPCallbackMiddlewareTests(unittest.TestCase):
    def setUp(self):
        global response_headers
        response_headers = []

    def test_should_do_nothing_when_no_headers_not_supplied(self):
        middleware = JSONPCallbackMiddleware(lambda x,y: JSON_RESULT)
        result = middleware({}, None)
        self.assertEquals(JSON_RESULT, result)
    
    def test_should_not_wrap_JSON_not_ajax_call(self):
        middleware = JSONPCallbackMiddleware(lambda x, y: JSON_RESULT)
        headers = {'QUERY_STRING': QUERY_STRING,
                   'HTTP_ACCEPT': HTTP_ACCEPT}
        
        result = middleware(headers, None)
        self.assertEquals(JSON_RESULT, result)
        
    def test_should_not_wrap_JSON_if_no_callback_in_query_string(self):
        middleware = JSONPCallbackMiddleware(lambda x, y: JSON_RESULT)
        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', 
                   'HTTP_ACCEPT': HTTP_ACCEPT}
        
        result = middleware(headers, None)
        self.assertEquals(JSON_RESULT, result)
        
    def test_should_not_wrap_JSON_if_javascript_as_return_not_accepted(self):
        middleware = JSONPCallbackMiddleware(lambda x, y: JSON_RESULT)
        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', 
                   'QUERY_STRING': QUERY_STRING}
        
        result = middleware(headers, None)
        self.assertEquals(JSON_RESULT, result)
        
    def test_should_wrap_JSON_in_callback_when_right_headers_supplied(self):
        def handler(status, passed_headers):
            global response_headers
            response_headers += passed_headers
            return JSON_RESULT

        middleware = JSONPCallbackMiddleware(lambda x, y: JSON_RESULT)
        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', 
                   'QUERY_STRING': QUERY_STRING,
                   'HTTP_ACCEPT': HTTP_ACCEPT}
        
        result = middleware(headers, handler)
        self.assertEquals(['jquery23423562352358(', '{}', ')'], list(result))
        self.assertEquals([('Content-Length', '24')], response_headers)

    def test_should_update_content_length_if_it_has_been_set(self):
        def initial_handler(environ, start_response):
            start_response('200 OK', [('Content-Length', '2')])
            return JSON_RESULT

        middleware = JSONPCallbackMiddleware(initial_handler)
        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', 
                   'QUERY_STRING': QUERY_STRING,
                   'HTTP_ACCEPT': HTTP_ACCEPT}
        
        def handler(status, passed_headers):
            global response_headers
            response_headers += passed_headers
            return JSON_RESULT
            
        result = middleware(headers, handler)
        self.assertEquals(['jquery23423562352358(', '{}', ')'], list(result))
        self.assertEquals([('Content-Length', '24')], response_headers)