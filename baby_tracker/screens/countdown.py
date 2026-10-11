from ..fonts import BLACK_WEIGHT, BOLD_WEIGHT
from ..gray_scale import DARK_GRAY, BLACK
from .base import Screen, COUNTDOWN


class CountdownScreen(Screen):
    """Birth date more than 40 weeks ahead: the days left."""
    STATE = COUNTDOWN
    COUNTDOWN_BASELINE = 92
    COUNTDOWN_RUN_GAP = 6
    COUNTDOWN_MIN_DIGIT_PT = 36
    COUNTDOWN_NOTE_BASELINE = 118
    COUNTDOWN_DATE_BASELINE = 140

    def _draw_content(self):
        days = self._days_until_birth()
        max_width = self.width - 2 * self.MARGIN
        for pt in range(self.HERO_DIGIT_PT, self.COUNTDOWN_MIN_DIGIT_PT - 1, -4):
            runs = [(self.locale.COUNTDOWN_PREFIX, self._font(20, BLACK_WEIGHT), DARK_GRAY),
                    (str(days), self._font(pt, BLACK_WEIGHT), BLACK),
                    (self.locale.unit_word(days, 'd'), self._font(22, BLACK_WEIGHT), DARK_GRAY)]
            runs = [run for run in runs if run[0]]
            width = sum(self._text_size(t, f)[0] for t, f, _ in runs) + (len(runs) - 1) * self.COUNTDOWN_RUN_GAP
            if width <= max_width:
                break
        # Without a name the date is already the title, so drop its line and re-centre the rest.
        shift = 0 if self.name else (self.COUNTDOWN_DATE_BASELINE - self.COUNTDOWN_NOTE_BASELINE) / 2
        self._text_runs(runs, self.width / 2, self.COUNTDOWN_BASELINE + shift, gap=self.COUNTDOWN_RUN_GAP)
        self._text((self.width / 2, self.COUNTDOWN_NOTE_BASELINE + shift), self.locale.COUNTDOWN_NOTE,
                   self._font(15, BOLD_WEIGHT), DARK_GRAY, anchor='ms')
        if self.name:
            self._text((self.width / 2, self.COUNTDOWN_DATE_BASELINE), self.locale.format_date(self._birth_date()),
                       self._font(14, BOLD_WEIGHT), BLACK, anchor='ms')
