import os
import shutil
import tempfile
import unittest
from PIL import Image
from pail.helpers import resize, get_file_length, to_int_list, get_resolution

sample_jpg = os.path.join(os.path.dirname(__file__), 'lena.jpg')
sample_png = os.path.join(os.path.dirname(__file__), 'lena.png')


class HelperTests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_resize(self):
        # we can resize images
        im = Image.open(sample_jpg)
        self.assertEqual(im.size, (128, 128))
        im_type, result = resize(sample_jpg, 64)
        new_size = Image.open(result).size
        self.assertEqual(new_size, (64, 64))
        self.assertEqual(im_type, 'JPEG')
        return

    def test_resize_no_resolution(self):
        # w/o resolution, no resizing
        self.assertEqual(resize(sample_jpg, None), None)
        return

    def test_resize_too_small(self):
        # if resolution >= image width, we get no new image
        self.assertEqual(resize(sample_jpg, 128), None)
        self.assertEqual(resize(sample_jpg, 256), None)
        return

    def test_resize_invalid_img_path(self):
        # invalid paths result in `None
        self.assertEqual(
            resize('not-a-path', 64), None)
        return

    def test_resize_broken_file(self):
        # broken images are not resized
        broken = os.path.join(self.tempdir, 'broken.jpg')
        with open(broken, 'w') as fd:
            fd.write('blah blah')
        self.assertEqual(
            resize(broken, 64), None)
        return

    def test_get_file_length(self):
        # make sure get_file_length works as expected
        path = os.path.join(self.tempdir, 'testfile1')
        with open(path, 'w') as fd:
            fd.write('1234567890')
        self.assertEqual(
            get_file_length(open(path, 'rb')), 10)
        return

    def test_get_file_length_zero_length(self):
        # make sure get_file_length works as expected with zero length
        path = os.path.join(self.tempdir, 'testfile1')
        fd = open(path, 'w')
        fd.close()
        self.assertEqual(
            get_file_length(open(path, 'rb')), 0)
        return

    def test_to_int_list(self):
        # we can turn strings into lists of integers
        self.assertEqual(to_int_list('1, 2, 3'), [1, 2, 3])
        self.assertEqual(to_int_list('123'), [123])
        return

    def test_get_resolution_no_client_width(self):
        # mobiles get the smallest resolution, others the biggest
        self.assertEqual(
            get_resolution(None, 1, [480, 768, 922], True), 480)
        self.assertEqual(
            get_resolution(None, 1, [480, 768, 922], False), 922)
        return

    def test_get_resolution_pixel_density_eq_1(self):
        # get the next biggest value from resolution list
        self.assertEqual(
            get_resolution(480, 1, [480, 768, 922]), 480)
        self.assertEqual(
            get_resolution(512, 1, [480, 768, 922]), 768)
        self.assertEqual(
            get_resolution(800, 1, [480, 768, 922]), 922)
        self.assertEqual(
            get_resolution(1000, 1, [480, 768, 922]), 1000)
        return

    def test_get_resolution_pixel_density_ne_1(self):
        # with a pixel density > 1 we need larger images
        self.assertEqual(  # 2 x 480
            get_resolution(480, 2, [480, 768, 922]), 960)
        self.assertEqual(  # 2 x 768
            get_resolution(512, 2, [480, 768, 922]), 1536)
        self.assertEqual(  # 2 x 922
            get_resolution(800, 2, [480, 768, 922]), 1844)
        self.assertEqual(  # 2 x 922
            get_resolution(1000, 2, [480, 768, 922]), 2000)
        self.assertEqual(  # > 2 x 922
            get_resolution(2000, 2, [480, 768, 922]), 4000)
        return
