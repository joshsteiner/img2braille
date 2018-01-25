from PIL import Image, ImageOps, ImageEnhance

white_threshold = 128

def is_black(pixel):
    return pixel < white_threshold


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
        for j in range(0, width, 2):
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


def img2braille(filename):
    with Image.open(filename) as img:
        #img.thumbnail((400, 400))
        pixels = []
        (width, height) = img.size
        try:
            img = ImageEnhance.Contrast(img).enhance(1)
            img = ImageEnhance.Brightness(img).enhance(1)
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


