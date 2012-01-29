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
