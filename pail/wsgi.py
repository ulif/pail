"""
WSGI Components
---------------

Middleware and other components that can be used with other WSGI
components.
"""
import re
import tempfile
from webob import Request
from webob.static import FileIter
from pail.helpers import resize, to_int_list, get_resolution

#: Default Resolution set used, when no other was given in config.
DEFAULT_RESOLUTIONS = "1382, 992, 768, 480"

#: Regular expressions from http://detectmobilebrowsers.com/ (public domain)
reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)

reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)


class ImageAdaptingMiddleware(object):
    """A WSGI middleware to shrink images on-the-fly.

    It works as a filter-wrapper that examines images delivered by
    other WSGI components and might reduce the image sizes on-the-fly.

    `resolutions`
       a string containing a comma separated list of integers. These
       number give the supported resolutions. The list does not have
       to be sorted.
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

        Returns a tuple ``(CLIENT_SCREEN_WIDTH, RETINA_VALUE)``.

        Here ``CLIENT_SCREEN_WITH`` gives the assumed screen width of the
        client device (an integer) or ``None``.

        ``RETINA_VALUE`` represents the factor of retina displays and
        is always an integer. If one CSS pixel stands for three
        physical pixels, this value would be ``3``. If no such value
        can be extracted from request, the default value ``1`` is
        returned.

        The method expects in `request` a cookie named `resolution`
        containing either a single integer or a float.

        If the value is an integer, we assume a retina value of
        ``1``. Otherwise we expect the client screen width before the
        dot and the retina factor after the dot.

        So a client providing a device width of 640 (CSS) pixels but
        with a retina display, that supports 3 physical pixels per CSS
        pixel, should pass in a cookie named `resolution` with value
        of ``640.3``.
        """
        cookies = request.cookies
        if not cookies:
            return (None, 1)
        cookie = cookies.get('resolution')
        if not cookie:
            return (None, 1)
        resolution, retina_value = cookie, '1'
        if '.' in cookie:
            resolution, retina_value = cookie.split('.', 1)
        try:
            resolution = int(resolution)
        except ValueError:
            resolution = None
        try:
            retina_value = int(retina_value)
        except ValueError:
            retina_value = 1
        return (resolution, retina_value)

    def get_resolution(self, request):
        """Determine a desired resolution from client screen
        resolution and available resolutions.
        """
        client_resolution, retina_value = self.get_client_resolution(request)
        is_mobile = self.is_mobile(request)
        return get_resolution(
            client_resolution, retina_value, self.resolutions, is_mobile)

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

    def is_mobile(self, request):
        """Is the device that sent `request` a mobile?
        """
        user_agent = request.headers.get('HTTP_USER_AGENT', None)
        if not user_agent:
            return False
        if reg_b.search(user_agent) or reg_v.search(user_agent[:4]):
            return True
        return False


def filter_app(app, global_conf, **kw):
    """A factory that returns `ImageAdaptingMiddleware` instances.
    """
    return ImageAdaptingMiddleware(app, global_conf, **kw)
