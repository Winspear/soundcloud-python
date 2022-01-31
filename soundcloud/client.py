from functools import partial
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from soundcloud.resource import wrapped_resource
from soundcloud.request import make_request


class Client(object):
    """A client for interacting with Soundcloud resources."""

    use_ssl = True
    host = 'api.soundcloud.com'

    def __init__(self, **kwargs):
        """Create a client instance with the provided options. Options should
        be passed in as kwargs.
        """
        self.use_ssl = kwargs.get('use_ssl', self.use_ssl)
        self.host = kwargs.get('host', self.host)
        self.scheme = self.use_ssl and 'https://' or 'http://'
        self.options = kwargs

        self.client_id = kwargs.get('client_id')

        if 'access_token' in kwargs:
            self.access_token = kwargs.get('access_token')
            return


    def _request(self, method, resource, **kwargs):
        """Given an HTTP method, a resource name and kwargs, construct a
        request and return the response.
        """
        url = self._resolve_resource_name(resource)

        if hasattr(self, 'access_token'):
            kwargs.update(dict(oauth_token=self.access_token))

        kwargs.update({
            'verify_ssl': self.options.get('verify_ssl', True),
            'proxies': self.options.get('proxies', None)
        })
        return wrapped_resource(make_request(method, url, kwargs))

    def __getattr__(self, name, **kwargs):
        """Translate an HTTP verb into a request method."""
        if name not in ('get', 'post', 'put', 'head', 'delete'):
            raise AttributeError
        return partial(self._request, name, **kwargs)

    def _resolve_resource_name(self, name):
        """Convert a resource name (e.g. tracks) into a URI."""
        if name[:4] == 'http':  # already a url
            return name
        name = name.rstrip('/').lstrip('/')
        return '%s%s/%s' % (self.scheme, self.host, name)

    def _redirect_uri(self):
        """
        Return the redirect uri. Checks for ``redirect_uri`` or common typo,
        ``redirect_url``
        """
        return self.options.get(
            'redirect_uri',
            self.options.get('redirect_url', None))
