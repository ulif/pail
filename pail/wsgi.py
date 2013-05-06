"""
WSGI Components
---------------

Middleware and other components that can be used with other WSGI
components.
"""
import tempfile
from webob import Request
from webob.static import FileIter
from pail.helpers import resize, to_int_list, get_resolution

DEFAULT_RESOLUTIONS = "1382, 992, 768, 480"


class ImageAdaptingMiddleware(object):
    """A WSGI middleware to shrink images on-the-fly.

    It works as a filter-wrapper that examines images delivered by
    other WSGI components and might reduce the image sizes on-the-fly.
    """

    #: The content types considered as handable. Only HTTP responses
    #: providing one of these types are handled by the middleware.
    acceptable_types = [
        'image/jpeg', 'image/png', 'image/gif']

    def __init__(self, app, global_conf, resolutions=DEFAULT_RESOLUTIONS):
        self.app = app
        self.global_conf = global_conf
        self.acceptable_types = [
            'image/jpeg', 'image/png', 'image/gif']
        try:
            self.resolutions = to_int_list(resolutions)
        except:
            raise ValueError('resolutions must be a comma-separated'
                             'list of integers')
        pass

    def __call__(self, environ, start_response):
        request = Request(environ)
        resolution = self.get_resolution(request)
        if self.should_ignore(request, resolution):
            return self.app(environ, start_response)
        response = request.get_response(self.app)

        if not self.should_adapt(response):
            return response(environ, start_response)

        new_img = self.create_resized_image(response, resolution)
        if new_img is None:
            return response(environ, start_response)

        im_type, new_img = new_img
        response.app_iter = FileIter(new_img)  # sets also content-length
        return response(environ, start_response)

    def create_resized_image(self, response, resolution):
        """Create a resized version of current content image.
        """
        orig_file = tempfile.TemporaryFile()
        for item in response.copy().app_iter:
            orig_file.write(item)
        orig_file.seek(0)
        return resize(orig_file, resolution)

    def get_client_resolution(self, request):
        """Get the client screen resolution from request.
        """
        cookies = request.cookies
        if not cookies:
            return None
        cookie = cookies.get('resolution')
        if not cookie:
            return None
        try:
            resolution = int(cookie)
        except ValueError:
            return None
        return resolution

    def get_resolution(self, request):
        """Determine a desired resolution from client screen
        resolution and avaiilable resolutions.
        """
        client_resolution = self.get_client_resolution(request)
        return get_resolution(client_resolution, 1, self.resolutions, False)

    def should_ignore(self, request, resolution):
        """Should the given request be ignored?
        """
        if not resolution or resolution < 1:
            return True
        return False

    def should_adapt(self, response):
        """Should we adapt the response from the wrapped app?
        """
        if response.content_type not in self.acceptable_types:
            return False
        return True


def filter_app(app, global_conf, **kw):
    """A factory that returns `ImageAdaptingMiddleware` instances.
    """
    return ImageAdaptingMiddleware(app, global_conf, **kw)
