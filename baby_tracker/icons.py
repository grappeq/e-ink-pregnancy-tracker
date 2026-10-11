import os
from functools import lru_cache

from PIL import Image

icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'res/icons')

carriage_icon_path = os.path.join(icons_dir, 'carriage.png')
moon_icon_path = os.path.join(icons_dir, 'moon.png')


@lru_cache(maxsize=None)
def load_icon(path):
    """The icon's shape as a 1-bit mask ('L', 0 or 255), cropped to its ink."""
    alpha = Image.open(path).convert('RGBA').getchannel('A')
    mask = alpha.point(lambda a: 255 if a > 127 else 0)
    return mask.crop(mask.getbbox())
