from PIL import Image
from datetime import datetime
import numpy


def to_array_fast(im):
    im.load()
    # unpack data
    e = Image._getencoder(im.mode, 'raw', im.mode)
    e.setimage(im.im)

    # NumPy buffer for the result
    shape, typestr = Image._conv_type_shape(im)
    data = numpy.empty(shape, dtype=numpy.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        l, s, d = e.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise RuntimeError("encoder error %d in tobytes" % s)
    return data


def to_image(array):
    return Image.fromarray(array)


def to_array(image):
    return numpy.array(image)


def get_date_label():
    return datetime.now().isoformat()


def log(text):
    print(f'[{get_date_label()}] {text}')
