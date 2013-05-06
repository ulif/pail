import os
import unittest
from pail.wsgi import ImageAdaptingMiddleware, filter_app
try:
    from cStringIO import StringIO
except ImportError:                     # pragma: no cover
    from io import BytesIO as StringIO  # pragma: no cover
from PIL import Image
from webob import Request

HTML = '''\
<html>
    <body>
        <h1>Content title</h1>
        <div id="content">Content content</div>
    </body>
</html>
'''
DATA_JPEG = open(
    os.path.join(os.path.dirname(__file__), 'lena.jpg'), 'rb').read()

DATA_GIF = open(
    os.path.join(os.path.dirname(__file__), 'lena.gif'), 'rb').read()

DATA_PNG = open(
    os.path.join(os.path.dirname(__file__), 'lena.png'), 'rb').read()

DEFAULT_COOKIE = 'resolution=128; $PATH=/'

TEST_RESOLUTIONS = '128, 64, 32'


def wsgi_app_plaintext(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain; charset=UTF-8')])
    return ['Hi!']


def wsgi_app_html(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8')])
    return [HTML]


def wsgi_app_no_content_type(environ, start_response):
    start_response('200 OK', [('Content-Type', '')])
    return []


def wsgi_app_img_jpg(environ, start_response):
    start_response('200 OK', [('Content-Type', 'image/jpeg'),
                              ('Content-Length', '%s' % len(DATA_JPEG))])
    return [DATA_JPEG]


def wsgi_app_img_gif(environ, start_response):
    start_response('200 OK', [('Content-Type', 'image/gif'),
                              ('Content-Length', '%s' % len(DATA_GIF))])
    return [DATA_GIF]


def wsgi_app_img_png(environ, start_response):
    start_response('200 OK', [('Content-Type', 'image/gif'),
                              ('Content-Length', '%s' % len(DATA_PNG))])
    return [DATA_PNG]


class WSGITests(unittest.TestCase):

    def get_request(self, cookie=DEFAULT_COOKIE):
        # get a prepopulated test request
        request = Request.blank('http://localhost/test.html')
        if cookie is not None:
            request.headers['Cookie'] = cookie
        return request

    def test_plaintext_not_filtered(self):
        # plaintext docs are passed on
        app = ImageAdaptingMiddleware(wsgi_app_plaintext, {})
        request = self.get_request()
        response = request.get_response(app)
        self.assertEqual(
            response.headers['Content-Type'], 'text/plain; charset=UTF-8')
        self.assertEqual(
            response.body, 'Hi!')
        return

    def test_html_not_filtered(self):
        # html docs are passed on
        app = ImageAdaptingMiddleware(wsgi_app_html, {})
        request = self.get_request()
        response = request.get_response(app)
        self.assertEqual(
            response.headers['Content-Type'], 'text/html; charset=UTF-8')
        self.assertEqual(
            response.body, HTML)
        return

    def test_no_content_type(self):
        # requests without content type are ignored
        app = ImageAdaptingMiddleware(wsgi_app_no_content_type, {})
        request = self.get_request()
        response = request.get_response(app)
        self.assertEqual(
            response.headers['Content-Type'], '')
        self.assertEqual(
            response.body, b'')
        return

    def test_no_cookie(self):
        # ignore content without cookie
        app = ImageAdaptingMiddleware(wsgi_app_img_jpg, {})
        request = self.get_request(cookie=None)
        response = request.get_response(app)
        self.assertEqual(response.content_length, len(response.body))
        self.assertEqual(len(DATA_JPEG), len(response.body))
        return

    def test_invalid_cookie_key(self):
        # ignore if no 'resolution' cookie was sent
        app = ImageAdaptingMiddleware(wsgi_app_img_jpg, {})
        request = self.get_request(cookie='foo=bar; $Path=/')
        response = request.get_response(app)
        self.assertEqual(response.content_length, len(response.body))
        self.assertEqual(len(DATA_JPEG), len(response.body))
        return

    def test_invalid_cookie_value(self):
        # ignore non-integer cookie values
        app = ImageAdaptingMiddleware(wsgi_app_img_jpg, {})
        request = self.get_request(cookie='resolution=foo; $Path=/')
        response = request.get_response(app)
        self.assertEqual(response.content_length, len(response.body))
        self.assertEqual(len(DATA_JPEG), len(response.body))
        return

    def test_resolution_too_large(self):
        # do not change original if resolution > actual image size
        app = ImageAdaptingMiddleware(wsgi_app_img_jpg, {})
        request = self.get_request(cookie='resolution=512; $Path=/')
        response = request.get_response(app)
        self.assertEqual(response.content_length, len(response.body))
        self.assertEqual(len(DATA_JPEG), len(response.body))
        return

    def test_no_resolution_at_all(self):
        # do not change original if no resolution at all is given
        # or resolution < 1
        app = ImageAdaptingMiddleware(
            wsgi_app_img_jpg, {}, resolutions='0')
        request = self.get_request(cookie='resolution=0; $Path=/')
        response = request.get_response(app)
        self.assertEqual(response.content_length, len(response.body))
        self.assertEqual(len(DATA_JPEG), len(response.body))
        return

    def test_shrink_jpeg_simple(self):
        # JPEGs are shrinked, if resolution is less than the original size
        app = ImageAdaptingMiddleware(
            wsgi_app_img_jpg, {}, resolutions="128, 64, 32")
        request = self.get_request(cookie='resolution=62; $Path=/')
        response = request.get_response(app)
        img_data = response.body
        image = Image.open(StringIO(img_data))
        self.assertEqual(image.size, (64, 64))
        self.assertEqual(
            response.content_length, len(img_data))
        self.assertEqual(
            response.content_type, 'image/jpeg')
        return

    def test_shrink_jpeg_min(self):
        # JPEGs are shrinked to minimal size, if client width <= lowest resol.
        app = ImageAdaptingMiddleware(
            wsgi_app_img_jpg, {}, resolutions="128, 64, 32")
        request = self.get_request(cookie='resolution=32; $Path=/')
        response = request.get_response(app)
        img_data = response.body
        image = Image.open(StringIO(img_data))
        self.assertEqual(image.size, (32, 32))
        return

    def test_shrink_jpeg_client_gt_image(self):
        # JPEGs are left untouched if client size > image size
        # This also applies, if the original size is not in set of resolutions
        app = ImageAdaptingMiddleware(
            wsgi_app_img_jpg, {}, resolutions="64, 32")
        request = self.get_request(cookie='resolution=130; $Path=/')
        response = request.get_response(app)
        img_data = response.body
        image = Image.open(StringIO(img_data))
        self.assertEqual(image.size, (128, 128))
        return

class GetClientResolutionTests(unittest.TestCase):
    # tests for ImageAdaptingMiddleware.get_client_resolution

    def setUp(self):
        self.request = Request.blank('http://localhost/test.html')
        self.middleware = ImageAdaptingMiddleware(None, {})
        return

    def test_no_cookie(self):
        # w/o cookie -> no resolution
        self.assertEqual(
            self.middleware.get_client_resolution(self.request), None)
        return

    def test_no_cookie_with_resolution_key(self):
        # we need a cookie named 'resolution' to get a resolution
        self.request.headers['Cookie'] = 'foo=bar; $Path=/'
        self.assertEqual(
            self.middleware.get_client_resolution(self.request), None)
        return

    def test_resolution_not_an_integer(self):
        # resolution cookie must contain some integer
        self.request.headers['Cookie'] = 'resolution=not-a-number; $Path=/'
        self.assertEqual(
            self.middleware.get_client_resolution(self.request), None)
        return

    def test_resolution(self):
        # integers can be extracted from the resolution cookie
        self.request.headers['Cookie'] = 'resolution=1024; $Path=/'
        self.assertEqual(
            self.middleware.get_client_resolution(self.request), 1024)
        return


class ShouldIgnoreTests(unittest.TestCase):
    # tests for ImageAdaptingMiddleware.should_ignore

    def setUp(self):
        self.middleware = ImageAdaptingMiddleware(None, {})
        return

    def test_resolution_okay(self):
        # resolution values >= 1 are okay
        self.assertEqual(self.middleware.should_ignore(None, 123), False)
        return

    def test_resolution_too_small(self):
        # resolution values < 1 are not okay
        self.assertEqual(self.middleware.should_ignore(None, -12), True)
        return

    def test_resolution_none(self):
        # unset resolution values should be ignored
        self.assertEqual(self.middleware.should_ignore(None, None), True)
        return


class ShouldAdaptTests(unittest.TestCase):
    # tests for ImageAdaptingMiddleware.should_adapt

    def setUp(self):
        self.middleware = ImageAdaptingMiddleware(None, {})

    def test_no_content_type(self):
        # docs w/o content type should not be adapted
        request = Request.blank('http://localhost/test.html')
        response = request.get_response(wsgi_app_no_content_type)
        self.assertEqual(
            self.middleware.should_adapt(response), False)
        return

    def test_jpeg_content_type(self):
        # image/jpeg docs are adapted
        request = Request.blank('http://localhost/test.html')
        response = request.get_response(wsgi_app_img_jpg)
        self.assertEqual(
            self.middleware.should_adapt(response), True)
        return

    def test_gif_content_type(self):
        # image/gif docs are adapted
        request = Request.blank('http://localhost/test.html')
        response = request.get_response(wsgi_app_img_gif)
        self.assertEqual(
            self.middleware.should_adapt(response), True)
        return

    def test_png_content_type(self):
        # image/png docs are adapted
        request = Request.blank('http://localhost/test.html')
        response = request.get_response(wsgi_app_img_png)
        self.assertEqual(
            self.middleware.should_adapt(response), True)
        return


class InitParamsTests(unittest.TestCase):
    # Tests for initial values of ImageAdaptingMiddleware

    def test_resolutions_default(self):
        # we get a default for resolutions
        app = ImageAdaptingMiddleware(None, {})
        self.assertEqual(app.resolutions, [1382, 992, 768, 480])
        return

    def test_resolutions_liststring(self):
        # we can parse resolutions list from a string
        app = ImageAdaptingMiddleware(None, {}, resolutions='1, 2, 3')
        self.assertEqual(app.resolutions, [1, 2, 3])
        return

    def test_resolutions_single_value(self):
        # we can cope with a single value passed in
        app = ImageAdaptingMiddleware(None, {}, resolutions='666')
        self.assertEqual(app.resolutions, [666])
        return

    def test_resolutions_invalid(self):
        # invalid lists result in a value error
        self.assertRaises(
            ValueError,
            ImageAdaptingMiddleware,
            None, {}, resolutions='not-a-list-of-ints')
        return


class FactoryTests(unittest.TestCase):

    def test_filter_app(self):
        # we can get a factory for ImageAdaptingMiddleware
        app = filter_app('FakeApp', {'key': 'value'}, resolutions='128, 64')
        self.assertTrue(
            isinstance(app, ImageAdaptingMiddleware))
        return
