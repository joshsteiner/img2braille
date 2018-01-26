#!/usr/bin/env python3

"""
Usage:
  img2braille.py [--dims=DIMS] [--contrast=CONTRAST] [--brightness=BRIGHTNESS] FILE
  img2braille.py --help

Arguments:
  FILE                                     image to convert

Options:
  -h --help                                show help
  -d DIMS --dims=DIMS                      image dimensions - 'width,height'
  -c CONTRAST --contrast=CONTRAST          image contrast     [default: 1]
  -b BRIGHTNESS --brightness=BRIGHTNESS    image brightness   [default: 1]
"""

from docopt import docopt
from PIL import Image, ImageOps, ImageEnhance

WHITE_THRESHOLD = 128

def is_black(pixel):
    return pixel < WHITE_THRESHOLD


def dither(pixels, dims):
    (width, height) = dims
    for i in range(height-1):
        for j in range(1, width-1):
            old = pixels[i][j]
            new = 0 if is_black(old) else 255
            err = old - new
            pixels[ i ][ j ]  = new
            pixels[i+1][ j ] += err * 7/16
            pixels[i-1][j+1] += err * 3/16
            pixels[ i ][j+1] += err * 5/16
            pixels[i+1][j+1] += err * 1/16
    return pixels


# U+2800 + offset
def toBraille(pixels, dims):
    braille = []
    (width, height) = dims
    for i in range(0, height, 4):
        braille.append([])
        for j in range(0, width-1, 2):
            offset = 0
            for k in range(min(4, height - i)):
                offset += is_black(pixels[i+k][j]) * 2 ** k
                offset += is_black(pixels[i+k][j+1]) * 2 ** (k+3)
                if k == 4:
                    offset += is_black(pixels[i+k][j]) * 2 ** 6
                    offset += is_black(pixels[i+k][j+1]) * 2 ** 7
            c = chr(0x2800 + offset)
            braille[-1].append(c)
    return braille


def img2braille(filename, dims=None, brightness=1, contrast=1):
    with Image.open(filename) as img:
        if dims:
            img.thumbnail(dims)
        pixels = []
        (width, height) = img.size
        try:
            img = ImageEnhance.Brightness(img).enhance(brightness)
            img = ImageEnhance.Contrast(img).enhance(contrast)
        except ValueError:
            pass
        for i, px in enumerate(ImageOps.grayscale(img).getdata()):
            if i % width == 0:
                pixels.append([])
            pixels[-1].append(px)
        dither(pixels, img.size)
        for row in toBraille(pixels, img.size):
            for c in row:
                print(c, end='')
            print('')


if __name__ == '__main__':
    args = docopt(__doc__)

    if args['--dims']:
        dims = [int(x) for x in args['--dims'].split(',')]
    else:
        dims = None

    img2braille(
        args['FILE'],
        dims,
        brightness=float(args['--brightness']),
        contrast=float(args['--contrast'])
    )
