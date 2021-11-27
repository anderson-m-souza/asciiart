#!/usr/bin/env python3

import argparse
import colorsys 
import subprocess

import colorama
import fpdf
from PIL import Image


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-b',
        '--brightness-mode',
        default='luminosity',
        choices=[
            'average',
            'lightness',
            'luminosity'
        ],
        help='defines how the brightness of pixel is calculated'
    )

    parser.add_argument(
        '-x',
        '--max-width',
        type=int,
        help='maximum number of characters in each line'
    )

    parser.add_argument(
        '-c',
        '--color',
        choices=[
            'black',
            'blue',
            'cyan',
            'green',
            'magenta',
            'red',
            'white',
            'yellow'
        ],
        help='output color'
    )

    parser.add_argument(
        '-i',
        '--invert',
        action='store_true',
        help='invert brightness'
    )

    parser.add_argument(
        '-r',
        '--repeat-characters',
        type=int,
        default=2,
        choices=[1, 2, 3],
        help='number of characters for each pixel'
    )

    parser.add_argument(
        '-m',
        '--character-map',
        type=int,
        default=3,
        choices=[1, 2, 3, 4],
        help='character map used for pictures'
    )

    parser.add_argument(
        '-w',
        '--webcam',
        action='store_true',
        help='use input from webcam'
    )

    parser.add_argument(
        '-p',
        '--paint',
        action='store_true',
        help='paint red, blue and green accordingly to the image'
    )

    parser.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='the image path'
    )

    parser.add_argument(
        '-o',
        '--output',
        metavar='NAME',
        help='generate a pdf file with the ascii art'
    )

    return parser.parse_args()


def main():
    if args.webcam:
        input_file = './snap.jpg'
        subprocess.run(['uvccapture', '-m', 'x640', '-y480']) 
    else:
        input_file = args.file

    image = open_img(input_file)
    matrix = image_to_rgb_matrix(image)
    image.close()
    colorama.init()
    asciiart = get_main_color()

    for row in matrix:
        for rgb in row:
            brightness = rgb_to_brightness(rgb)
            chars = brightness_to_chars(brightness)
            if args.paint:
                chars = get_char_color(rgb) + chars + get_main_color()
            asciiart += chars
        asciiart += '\n'

    if args.output:
        generate_pdf(asciiart)

    print(asciiart, end='')
    colorama.deinit()


def open_img(path):
    max_width = args.max_width
    image = Image.open(path)

    if max_width and image.width > max_width:
        image = resize(image, max_width)

    return image 
    

def resize(image, max_width):
    w = max_width
    h = round(image.height * (w/image.width))
    return image.resize((w, h))


def image_to_rgb_matrix(image):
    w = image.width
    h = image.height
    pixels = list(image.getdata())
    matrix = list()
    pos = 0

    i = 0
    while i < h:
        line = list()

        j = 0
        while j < w:
            rgb = pixels[pos]
            line.append(rgb)
            pos += 1
            j += 1

        matrix.append(line)
        i += 1

    return matrix


def rgb_to_brightness(rgb):
    brightness = 0
    (r, g, b) = rgb
    mode = args.brightness_mode

    if mode == 'average':
        brightness = avg_bright(r, g, b)
    elif mode == 'lightness':
        brightness = light_bright(r, g, b)
    elif mode == 'luminosity':
        brightness = lum_bright(r, g, b)

    return brightness


def avg_bright(r, g, b):
    avg = round((r+g+b) / 3)
    return avg


def light_bright(r, g, b):
    light = round((max(r, g, b) + min(r, g, b)) / 2)
    return light


def lum_bright(r, g, b):
    lumin = round(0.21*r + 0.72*g + 0.07*b)
    return lumin


def brightness_to_chars(b):
    chars = get_char_map(args.character_map)

    if args.invert:
        b = invert_brightness(b)

    i = 0
    if b != 0:
        i = round(((len(chars)-1) / (255/b))) 

    return chars[i] * args.repeat_characters


def get_char_map(cmap):
    if cmap == 1:
        return (' `^",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW'
                '&8%B@$')
    elif cmap == 2:
        return (' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkha'
                'o*#MW&8%B@$')
    elif cmap == 3:
        return ' .:¬=+*x#%@$'

    else:
        return ' .:-=+*#%@'


def invert_brightness(b):
    return abs(b - 255)


def get_main_color():
    color = args.color

    if not color:
        return ''

    elif color == 'black':
        return colorama.Fore.BLACK

    elif color == 'red':
        return colorama.Fore.RED

    elif color == 'green':
        return colorama.Fore.GREEN

    elif color == 'yellow':
        return colorama.Fore.YELLOW

    elif color == 'blue':
        return colorama.Fore.BLUE

    elif color == 'magenta':
        return colorama.Fore.MAGENTA

    elif color == 'cyan':
        return colorama.Fore.CYAN

    elif color == 'white':
        return colorama.Fore.WHITE

    else:
        return colorama.Fore.RESET


def get_char_color(rgb):
    (r, g, b) = rgb
    (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    if s <= 0.11:
        return colorama.Fore.LIGHTWHITE_EX

    else:
        if v <= 0.05:
            return colorama.Fore.BLACK

        else:
            if h <= 12/360 or h >= 355/360:
                if s < 0.3:
                    return colorama.Fore.LIGHTRED_EX
                else:
                    return colorama.Fore.RED

            elif h <= 30/360 and h > 12/360 and s < 0.7:
                beige = '\033[38;5;223m'
                return beige 

            elif h <= 30/360 and h > 12/360:
                if s < 0.6:
                    light_orange = '\033[38;5;208m'
                    return light_orange
                else:
                    orange = '\033[38;5;202m'
                    return orange

            elif h <= 75/360 and h > 30/360:
                if s < 0.4:
                    return colorama.Fore.LIGHTYELLOW_EX
                else:
                    return colorama.Fore.YELLOW

            elif h <= 140/360 and h > 75/360:
                if s < 0.6:
                    return colorama.Fore.LIGHTGREEN_EX
                else:
                    return colorama.Fore.GREEN

            elif h <= 170/360 and h > 140/360:
                if s < 0.5:
                    return colorama.Fore.LIGHTCYAN_EX
                else:
                    return colorama.Fore.CYAN
            
            elif h <= 270/360 and h > 170/360:
                if s < 0.7:
                    return colorama.Fore.LIGHTBLUE_EX 
                else:
                    return colorama.Fore.BLUE

            elif h <= 350/360 and h > 270/360:
                if s < 0.8:
                    return colorama.Fore.LIGHTMAGENTA_EX
                else:
                    return colorama.Fore.MAGENTA

            else:
                return colorama.Fore.RESET


def generate_pdf(asciiart):
    pdf = fpdf.FPDF()
    pdf.compress = False
    pdf.add_page()
    pdf.set_font('Courier', size=3)
    pdf.write(1.5, txt=asciiart)
    pdf.output(args.output)


args = parse_arguments()
main()
