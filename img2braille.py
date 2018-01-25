from PIL import Image, ImageOps, ImageEnhance

white_threshold = 128

def dither(pixels, dims):
    (width, height) = dims
    for i in range(height-1):
        for j in range(1, width-1):
            old = pixels[i][j] 
            new = 255 if old > white_threshold else 0
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
            try:
                offset += (pixels[ i ][ j ] < white_threshold) * 2 ** 0 + (pixels[ i ][j+1] < white_threshold) * 2 ** 3
                offset += (pixels[i+1][ j ] < white_threshold) * 2 ** 1 + (pixels[i+1][j+1] < white_threshold) * 2 ** 4
                offset += (pixels[i+2][ j ] < white_threshold) * 2 ** 2 + (pixels[i+2][j+1] < white_threshold) * 2 ** 5
                offset += (pixels[i+3][ j ] < white_threshold) * 2 ** 6 + (pixels[i+3][j+1] < white_threshold) * 2 ** 7
            except IndexError:
                pass 
            c = chr(0x2800 + offset)
            braille[-1].append(c) 
    return braille


def img2braille(filename):
    with Image.open(filename) as img:
        img.thumbnail((400,400))
        pixels = []
        (width, height) = img.size
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1)
        for i, px in enumerate(ImageOps.grayscale(img).getdata()):
            if (i % width == 0):
                pixels.append([])
            pixels[-1].append(px)
        dither(pixels, img.size)
        for row in toBraille(pixels, img.size):
            for c in row:
                print(c, end='')
            print('')


