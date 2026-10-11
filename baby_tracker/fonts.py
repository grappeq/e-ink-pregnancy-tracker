import os
from PIL import ImageFont

fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'res/fonts')

BLACK_WEIGHT = 'Nunito-Black.ttf'
BOLD_WEIGHT = 'Nunito-Bold.ttf'
SEMI_BOLD_WEIGHT = 'Nunito-SemiBold.ttf'


def create_font(pt, weight=BLACK_WEIGHT):
    return ImageFont.truetype(os.path.join(fonts_dir, weight), pt)
