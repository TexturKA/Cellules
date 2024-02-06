import numpy
from PIL import Image


def to_array_fast(image: Image) -> numpy.ndarray:
    image.load()
    # unpack data
    e = Image._getencoder(image.mode, 'raw', image.mode)
    e.setimage(image.im)

    # NumPy buffer for the result
    shape, typestr = Image._conv_type_shape(image)
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


def to_image(array: numpy.ndarray) -> Image:
    return Image.fromarray(array)


def to_array(image: Image) -> numpy.ndarray:
    return numpy.array(image)
