from ..fonts import BLACK_WEIGHT
from ..gray_scale import LIGHT_GRAY, DARK_GRAY, BLACK
from .base import Screen, NORMAL


def hero_parts(parts):
    """Split age parts into the hero (up to two largest non-zero units) and the remainder.

    Needs at least one non-zero part: day 0 is the WELCOME screen, never this one.
    """
    non_zero = [p for p in parts if p[0]]
    return non_zero[:2], non_zero[2:]


class AgeScreen(Screen):
    """The everyday screen: the baby's age and a bar counting down to the next birthday."""
    STATE = NORMAL
    PROGRESS_LABEL_BASELINE = 140
    PROGRESS_BAR = (145, 153)

    def _draw_progress(self):
        """Draws the next-birthday row and returns the top of its label."""
        left, right = self.MARGIN, self.width - self.MARGIN
        baseline = self.PROGRESS_LABEL_BASELINE
        label_font = self._font(self.PROGRESS_LABEL_PT, BLACK_WEIGHT)
        days_left = self.age.get_days_to_next_birthday()
        boxes = [
            self._text((left, baseline), self.locale.next_birthday(self.age.get_next_birthday_number()), label_font,
                       DARK_GRAY),
            self._text((right, baseline), self.locale.in_days(days_left), label_font, BLACK, anchor='rs'),
        ]

        bar_top, bar_bottom = self.PROGRESS_BAR
        height = bar_bottom - bar_top
        self._rounded_rect([left, bar_top, right, bar_bottom], height / 2, LIGHT_GRAY)
        # A fill of 2h reads as a started bar; h alone would look like a stray dot.
        filled = left + max(2 * height, (right - left) * self.age.get_progress_to_next_birthday())
        self._rounded_rect([left, bar_top, filled, bar_bottom], height / 2, BLACK)
        return min(box[1] for box in boxes)

    def _draw_content(self):
        hero, rest = hero_parts(self.age.get_parts())
        self._draw_hero(hero, rest, self._draw_progress() - self.CONTENT_GAP)
