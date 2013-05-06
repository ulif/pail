"""
Helper Functions
----------------

Minor helper functions.

"""
import tempfile
from PIL import Image


def resize(image, resolution=None, client_resolution=None, enlarge=False):
    """Resize `image` to have width `resolution`.

    `image` can be a path or some open file descriptor.

    `resolution` gives the desired maximum width in pixels.

    Returns ``None`` or a tuple

      ``(<FORMAT>, <RESULT_FILE_FD>)``

    with ``<FORMAT>`` being an image type as determined by PIL and
    ``<RESULT_FILE_FD>`` being an opened temporary file.

    If the image is already narrower than `resolution`, `None`
    is returned.

    The same applies if the image cannot be read or the resizing
    operation fails.
    """
    if resolution is None:
        return None
    try:
        im = Image.open(image)
    except IOError:
        return None
    size_x, size_y = im.size
    if size_x <= resolution:
        return None
    res_x = resolution
    res_y = resolution * size_y / size_x
    format = im.format

    #  create the resized version.
    new_im = im.resize((int(res_x), int(res_y)), Image.ANTIALIAS)

    #  save it to a temporary file.
    new_file = tempfile.TemporaryFile()
    new_im.save(new_file, format)
    new_file.seek(0)
    return format, new_file


def get_file_length(fd):
    """Get length of file denoted by a file descriptor.

    As we cannot get a stat of files of which we only have a file
    descriptor (and no path or similar), we have to do some tricks to
    get the file-length anyway.

    `fd` should be the descriptor of a file already open for reading.

    Returns the length of file as an integer.
    """
    fd.seek(0, 2)
    length = fd.tell()
    fd.seek(0)
    return length


def to_int_list(string):
    """Try to turn a string into a list of integers.

    Turns strings like `'1, 2, 3'` into regular lists like `[1, 2,
    3]`. The number have to be comma-separated. Also lists with only
    one entry are handled correctly.
    """
    if not ',' in string:
        return [int(string)]
    return [int(x) for x in string.split(',')]


def get_resolution(client_width, pixel_density, resolution_list,
                   is_mobile=True):
    """Get the desired resolution based on the input parameters.

    `client_width`
       The screen width of some client device.

    `pixel_density`
       By default 1. The amount of physical pixels representing a single
       CSS pixel. Normally 1 but on retina displays it can be more.

    `resolution_list`
       A list of supported screen widths (integers) from the web
       applications side.

    `is_mobile`
       A boolean. Indicates, whether the client device seems to be a
       mobile device. If so and no `client_width` is given, then the
       lowest possible resolution (based on `resolution_list`) is
       returned.
    """
    if client_width is None:
        return is_mobile and min(resolution_list) or max(resolution_list)
    possible_values = resolution_list
    possible_values.append(max( max(resolution_list), client_width))
    total_width = client_width * pixel_density
    result = [x * pixel_density for x in possible_values
              if total_width <= x * pixel_density]
    result = min(result + [max(possible_values) * pixel_density])
    return result
