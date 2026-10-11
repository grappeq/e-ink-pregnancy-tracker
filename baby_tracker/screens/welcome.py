from ..fonts import BOLD_WEIGHT
from ..gray_scale import LIGHT_GRAY, DARK_GRAY, BLACK
from .base import Screen, WELCOME


class WelcomeScreen(Screen):
    """The day of birth."""
    STATE = WELCOME
    WELCOME_HEART = (132, 58, 20)
    # (x offset from centre, radius, fill) of the dots either side of the welcome heart.
    WELCOME_DOTS = [(38, 3, LIGHT_GRAY), (52, 2, DARK_GRAY)]
    WELCOME_TEXT_BASELINE = 108
    WELCOME_NOTE_BASELINE = 136

    def _draw_content(self):
        cx, cy, r = self.WELCOME_HEART
        self._draw_heart(cx, cy, r, BLACK)
        for offset, radius, fill in self.WELCOME_DOTS:
            for x in (cx - offset, cx + offset):
                self._ellipse([x - radius, cy - radius, x + radius, cy + radius], fill)
        greeting = self.locale.WELCOME
        font = self._fit_font(greeting, self.width - 2 * self.MARGIN - 12, range(22, self.WISH_MIN_PT - 1, -2))
        self._text((self.width / 2, self.WELCOME_TEXT_BASELINE), greeting, font, BLACK, anchor='ms')
        # Without a name the date is already the title.
        note = self.locale.format_date(self.age.birth_date) if self.name else self.locale.FIRST_DAY
        self._text((self.width / 2, self.WELCOME_NOTE_BASELINE), note, self._font(15, BOLD_WEIGHT), DARK_GRAY,
                   anchor='ms')
