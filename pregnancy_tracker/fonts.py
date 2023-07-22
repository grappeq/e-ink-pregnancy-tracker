import os
from PIL import ImageFont

fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'res/fonts')

font_file_name = 'Merriweather-Black.ttf'
font_file_path = os.path.join(fonts_dir, font_file_name)


def create_font(pt):
    return ImageFont.truetype(font_file_path, pt)
