# Drawing values: the panel's 4 levels, evenly spaced, so antialiased edges
# land on the nearest level when quantized.
WHITE = 0xff
LIGHT_GRAY = 0xaa
DARK_GRAY = 0x55
BLACK = 0x00

# Values the Waveshare 2.7" driver (getbuffer_4Gray) maps to each level.
_DEVICE_LEVELS = [0x00, 0x80, 0xC0, 0xFF]


def quantize(img):
    """Snap an 'L' image to exactly the 4 values the e-paper driver understands."""
    return img.point(lambda v: _DEVICE_LEVELS[min(3, (v + 42) // 85)])
