import os
from PIL import ImageFont

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')

font_file_name = 'Merriweather-Black.ttf'
font_file_path = os.path.join(picdir, font_file_name)

font24 = ImageFont.truetype(font_file_path, 24)
font30 = ImageFont.truetype(font_file_path, 30)
font36 = ImageFont.truetype(font_file_path, 36)


def create_font(pt):
    return ImageFont.truetype(font_file_path, pt)
