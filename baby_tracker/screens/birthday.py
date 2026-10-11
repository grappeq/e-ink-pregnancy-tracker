from ..fonts import BLACK_WEIGHT
from ..gray_scale import DARK_GRAY, BLACK
from .base import Screen, BIRTHDAY


class BirthdayScreen(Screen):
    """Every birthday from the first one on."""
    STATE = BIRTHDAY
    BIRTHDAY_BASELINE = 86
    BIRTHDAY_MIN_PT = 48
    BIRTHDAY_HEART_RADIUS = 7
    BIRTHDAY_HEART_CY = 64
    BIRTHDAY_HEART_GAP = 18
    BIRTHDAY_WORD_BASELINE = 104
    BIRTHDAY_WISH_BASELINE = 136

    def _draw_content(self):
        ordinal = self.locale.birthday_ordinal(self.age.get_years())
        heart_room = 2 * (self.BIRTHDAY_HEART_GAP + 2 * self.BIRTHDAY_HEART_RADIUS)
        max_width = self.width - 2 * self.MARGIN - 12
        for pt in range(self.HERO_DIGIT_PT, self.BIRTHDAY_MIN_PT - 1, -4):
            font = self._font(pt, BLACK_WEIGHT)
            width, _ = self._text_size(ordinal, font)
            if width + heart_room <= max_width:
                break
        cx = self.width / 2
        self._text((cx, self.BIRTHDAY_BASELINE), ordinal, font, BLACK, anchor='ms')
        if width + heart_room <= max_width:
            offset = width / 2 + self.BIRTHDAY_HEART_GAP
            for x in (cx - offset, cx + offset):
                self._draw_heart(x, self.BIRTHDAY_HEART_CY, self.BIRTHDAY_HEART_RADIUS, BLACK)
        self._text((cx, self.BIRTHDAY_WORD_BASELINE), self.locale.BIRTHDAY_WORD,
                   self._font(self.HERO_UNIT_PT, BLACK_WEIGHT), DARK_GRAY, anchor='ms')
        wish = self.locale.BIRTHDAY_WISH
        wish_font = self._fit_font(wish, self.width - 2 * self.MARGIN, range(22, self.WISH_MIN_PT - 1, -2))
        self._text((cx, self.BIRTHDAY_WISH_BASELINE), wish, wish_font, BLACK, anchor='ms')
