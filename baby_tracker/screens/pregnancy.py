from ..fonts import BLACK_WEIGHT
from ..gray_scale import LIGHT_GRAY, DARK_GRAY, BLACK
from ..icons import load_icon, moon_icon_path, carriage_icon_path
from .base import Screen, PREGNANCY


class PregnancyScreen(Screen):
    """Birth date still ahead, within the 40 weeks: weeks and days, and the moon-to-carriage bar."""
    STATE = PREGNANCY
    PREGNANCY_LABEL_BASELINE = 123
    PREGNANCY_BAR = (136, 144)
    ICON_GAP = 6

    def _draw_pregnancy_progress(self):
        """Draws the moon-to-carriage bar with its labels and returns the top of the labels."""
        left, right = self.MARGIN, self.width - self.MARGIN
        bar_top, bar_bottom = self.PREGNANCY_BAR
        bar_mid = (bar_top + bar_bottom) / 2
        moon, carriage = load_icon(moon_icon_path), load_icon(carriage_icon_path)
        self._icon(moon, left + moon.width / 2, bar_mid)
        self._icon(carriage, right - carriage.width / 2, bar_mid)
        bar_left, bar_right = left + moon.width + self.ICON_GAP, right - carriage.width - self.ICON_GAP

        height = bar_bottom - bar_top
        self._rounded_rect([bar_left, bar_top, bar_right, bar_bottom], height / 2, LIGHT_GRAY)
        filled = bar_left + max(2 * height, (bar_right - bar_left) * self.pregnancy.get_progress())
        self._rounded_rect([bar_left, bar_top, filled, bar_bottom], height / 2, BLACK)

        days = self.pregnancy.get_days_until_due()
        if days > 0:
            remaining = self.locale.in_days(days)
        elif days == 0:
            remaining = self.locale.DUE_TODAY
        else:
            remaining = self.locale.overdue(-days)
        baseline = self.PREGNANCY_LABEL_BASELINE
        label_font = self._font(self.PROGRESS_LABEL_PT, BLACK_WEIGHT)
        boxes = [
            self._text((left, baseline), self.locale.format_percent(self.pregnancy.get_progress()), label_font, BLACK),
            self._text((right, baseline), remaining, label_font, DARK_GRAY, anchor='rs'),
        ]
        return min(box[1] for box in boxes)

    def _draw_content(self):
        # get_day() >= 1 in this state, so at least one part is non-zero.
        hero = [p for p in self.pregnancy.get_parts() if p[0]]
        self._draw_hero(hero, [], self._draw_pregnancy_progress() - self.CONTENT_GAP)
