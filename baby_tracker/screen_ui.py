from datetime import datetime

from PIL import Image, ImageDraw

from .fonts import create_font, BLACK_WEIGHT, BOLD_WEIGHT, SEMI_BOLD_WEIGHT
from .gray_scale import WHITE, LIGHT_GRAY, DARK_GRAY, BLACK, quantize
from .icons import load_icon, moon_icon_path, carriage_icon_path
from .locales import get_locale

# Supersampling keeps curves smooth once quantized down to the panel's 4 gray levels.
SCALE = 4

NORMAL = 'normal'
COUNTDOWN = 'countdown'
WELCOME = 'welcome'
BIRTHDAY = 'birthday'
PREGNANCY = 'pregnancy'


def select_state(age, pregnancy=None):
    if age is not None and age.is_born():
        if age.get_total_days() == 0:
            return WELCOME
        if age.is_birthday():
            return BIRTHDAY
        return NORMAL
    if pregnancy is not None and pregnancy.get_day() >= 1:
        return PREGNANCY
    return COUNTDOWN


def hero_parts(parts):
    """Split age parts into the hero (up to two largest non-zero units) and the remainder."""
    non_zero = [p for p in parts if p[0]]
    if not non_zero:
        # Day of birth; only reachable if a caller skips select_state().
        return [(0, 'd')], []
    return non_zero[:2], non_zero[2:]


def title_candidates(name, birth_date, born, locale):
    """(text, pt) pairs to try in order; the caller truncates the last one if nothing fits."""
    if name:
        return [(name, 17), (name, 15)]
    prefix = locale.BORN_PREFIX if born else ''
    long_form = prefix + locale.format_date(birth_date)
    return [(long_form, 17), (long_form, 15), (prefix + locale.format_short_date(birth_date), 15)]


class ScreenUI:
    MARGIN = 12
    TITLE_BASELINE = 21
    HEART_RADIUS = 5
    HEART_GAP = 6
    HEART_RISE = 6
    NAME_MAX_LENGTH = 64
    HERO_DIGIT_PT = 64
    HERO_UNIT_PT = 16
    HERO_UNIT_GAP = 2
    REMAINDER_PT = 15
    REMAINDER_GAP = 10
    REMAINDER_MIN_GAP = 7
    CONTENT_GAP = 8
    PROGRESS_LABEL_PT = 13
    PROGRESS_LABEL_BASELINE = 140
    PROGRESS_BAR = (145, 153)
    STAMP_PT = 12
    STAMP_BASELINE = 170
    COUNTDOWN_BASELINE = 92
    COUNTDOWN_RUN_GAP = 6
    COUNTDOWN_MIN_DIGIT_PT = 36
    COUNTDOWN_NOTE_BASELINE = 118
    COUNTDOWN_DATE_BASELINE = 140
    WELCOME_HEART = (132, 58, 20)
    # (x offset from centre, radius, fill) of the dots either side of the welcome heart.
    WELCOME_DOTS = [(38, 3, LIGHT_GRAY), (52, 2, DARK_GRAY)]
    WELCOME_TEXT_BASELINE = 108
    WELCOME_NOTE_BASELINE = 136
    BIRTHDAY_BASELINE = 86
    BIRTHDAY_MIN_PT = 48
    BIRTHDAY_HEART_RADIUS = 7
    BIRTHDAY_HEART_CY = 64
    BIRTHDAY_HEART_GAP = 18
    BIRTHDAY_WORD_BASELINE = 104
    BIRTHDAY_WISH_BASELINE = 136
    WISH_MIN_PT = 16
    PREGNANCY_LABEL_BASELINE = 123
    PREGNANCY_BAR = (136, 144)
    ICON_GAP = 6

    def __init__(self, width, height, age=None, pregnancy=None, name=None, now=None, locale=None):
        if age is None and pregnancy is None:
            raise ValueError('ScreenUI needs an age, a pregnancy or both')
        self.width = width
        self.height = height
        self.age = age
        self.pregnancy = pregnancy
        self.name = self._clean_name(name)
        self.now = now or datetime.now()
        self.locale = locale or get_locale()
        self._title_bottom = None

    @classmethod
    def _clean_name(cls, name):
        # Collapses newlines/tabs and bounds the work done by title truncation.
        if not isinstance(name, str):
            return None
        return ' '.join(name.split())[:cls.NAME_MAX_LENGTH] or None

    # Drawing helpers take coordinates in screen pixels and scale them up.

    def _font(self, pt, weight):
        return create_font(pt * SCALE, weight)

    def _text_size(self, text, font):
        left, top, right, bottom = self._draw.textbbox((0, 0), text, font=font, anchor='ls')
        return (right - left) / SCALE, -top / SCALE

    def _descent(self, font):
        return self._draw.textbbox((0, 0), 'ęy', font=font, anchor='ls')[3] / SCALE

    def _text(self, xy, text, font, fill, anchor='ls'):
        x, y = xy
        self._draw.text((x * SCALE, y * SCALE), text, font=font, fill=fill, anchor=anchor)
        box = tuple(v / SCALE for v in self._draw.textbbox((x * SCALE, y * SCALE), text, font=font, anchor=anchor))
        self.drawn.append((text, font.size // SCALE, fill, box))
        return box

    def _text_runs(self, runs, cx, baseline, gap=0):
        """Draw (text, font, fill) runs side by side on one baseline, centred on cx."""
        widths = [self._text_size(text, font)[0] for text, font, _ in runs]
        x = cx - (sum(widths) + gap * (len(runs) - 1)) / 2
        for (text, font, fill), width in zip(runs, widths):
            self._text((x, baseline), text, font, fill)
            x += width + gap

    def _rounded_rect(self, box, radius, fill):
        self._draw.rounded_rectangle([v * SCALE for v in box], radius=radius * SCALE, fill=fill)

    def _ellipse(self, box, fill):
        self._draw.ellipse([v * SCALE for v in box], fill=fill)

    def _draw_heart(self, cx, cy, r, fill):
        lobe = r * 0.55
        self._ellipse([cx - r, cy - r * 0.75, cx - r + 2 * lobe, cy - r * 0.75 + 2 * lobe], fill)
        self._ellipse([cx + r - 2 * lobe, cy - r * 0.75, cx + r, cy - r * 0.75 + 2 * lobe], fill)
        points = [(cx - r * 0.97, cy - r * 0.1), (cx + r * 0.97, cy - r * 0.1), (cx, cy + r * 0.95)]
        self._draw.polygon([(x * SCALE, y * SCALE) for x, y in points], fill=fill)

    def _fit_font(self, text, max_width, pts, weight=BLACK_WEIGHT):
        """The first of pts at which text fits max_width, else the last one."""
        for pt in pts:
            font = self._font(pt, weight)
            if self._text_size(text, font)[0] <= max_width:
                break
        return font

    def _icon(self, mask, cx, cy):
        """Queues a 1-bit icon centred on (cx, cy); pasted after downscaling so it stays crisp."""
        self._icons.append((mask, (round(cx - mask.width / 2), round(cy - mask.height / 2))))

    # The birth date before birth, from whichever model has one.

    def _birth_date(self):
        return self.age.birth_date if self.age is not None else self.pregnancy.due_date

    def _days_until_birth(self):
        if self.age is not None:
            return self.age.get_days_until_birth()
        return max(0, self.pregnancy.get_days_until_due())

    def _is_born(self):
        return self.age is not None and self.age.is_born()

    # Shared parts.

    def _fit_title(self):
        max_width = self.width - 2 * self.MARGIN - 2 * self.HEART_RADIUS - self.HEART_GAP
        candidates = title_candidates(self.name, self._birth_date(), self._is_born(), self.locale)
        for text, pt in candidates:
            font = self._font(pt, BLACK_WEIGHT)
            if self._text_size(text, font)[0] <= max_width:
                return text, font
        # Only names get here: date fallbacks always fit. Each pass drops a character.
        text, pt = candidates[-1]
        font = self._font(pt, BLACK_WEIGHT)
        while text and self._text_size(text.rstrip() + '…', font)[0] > max_width:
            text = text[:-1]
        return text.rstrip() + '…', font

    def _draw_title(self):
        """Draws the heart + title and returns the bottom of the title's ink."""
        text, font = self._fit_title()
        text_width, _ = self._text_size(text, font)
        heart_width = 2 * self.HEART_RADIUS
        left = (self.width - heart_width - self.HEART_GAP - text_width) / 2
        heart_cy = self.TITLE_BASELINE - self.HEART_RISE
        self._draw_heart(left + self.HEART_RADIUS, heart_cy, self.HEART_RADIUS, BLACK)
        return self._text((left + heart_width + self.HEART_GAP, self.TITLE_BASELINE), text, font, BLACK)[3]

    def _draw_timestamp(self):
        stamp = self.locale.format_timestamp(self.now)
        self._text((self.width - self.MARGIN, self.STAMP_BASELINE), stamp,
                   self._font(self.STAMP_PT, SEMI_BOLD_WEIGHT), LIGHT_GRAY, anchor='rs')

    # Normal state.

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

    def _draw_everyday(self):
        hero, rest = hero_parts(self.age.get_parts())
        self._draw_hero(hero, rest, self._draw_progress() - self.CONTENT_GAP)

    def _draw_hero(self, hero, rest, zone_bottom):
        """Draws one or two big numbers with their units, centred between the title and zone_bottom."""
        zone_top = self._title_bottom + self.CONTENT_GAP

        digit_font = self._font(self.HERO_DIGIT_PT, BLACK_WEIGHT)
        unit_font = self._font(self.HERO_UNIT_PT, BLACK_WEIGHT)
        remainder_font = self._font(self.REMAINDER_PT, BOLD_WEIGHT)
        _, digit_ascent = self._text_size('0123456789', digit_font)
        unit_offset = digit_ascent + self.HERO_UNIT_GAP + self.HERO_UNIT_PT
        # Center the group by its bounds with descenders, so layouts don't shift with the copy.
        if rest:
            height = unit_offset + self.REMAINDER_GAP + self.REMAINDER_PT + self._descent(remainder_font)
            # Under a title with descenders the zone is a few px short: tighten the remainder first.
            squeeze = min(self.REMAINDER_GAP - self.REMAINDER_MIN_GAP,
                          max(0, height - (zone_bottom - zone_top)))
            height -= squeeze
            remainder_offset = unit_offset + self.REMAINDER_GAP - squeeze + self.REMAINDER_PT
        else:
            height = unit_offset + self._descent(unit_font)
        top = zone_top + (zone_bottom - zone_top - height) / 2

        columns = [self.width / 2] if len(hero) == 1 else [self.width / 4, self.width * 3 / 4]
        for cx, (value, unit) in zip(columns, hero):
            self._text((cx, top + digit_ascent), str(value), digit_font, BLACK, anchor='ms')
            self._text((cx, top + unit_offset), self.locale.unit_word(value, unit), unit_font, DARK_GRAY, anchor='ms')
        if len(hero) > 1:
            x = self.width / 2
            self._rounded_rect([x - 1, top + 6, x + 1, top + unit_offset - 2], 1, LIGHT_GRAY)
        if rest:
            quantities = self.locale.join_words([self.locale.format_quantity(v, u) for v, u in rest])
            self._text_runs([(self.locale.REMAINDER_PREFIX, remainder_font, DARK_GRAY),
                             (quantities, remainder_font, BLACK)],
                            self.width / 2, top + remainder_offset)

    # Pregnancy state (birth date still ahead, within the 40 weeks).

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

    def _draw_pregnancy(self):
        # get_day() >= 1 in this state, so at least one part is non-zero.
        hero = [p for p in self.pregnancy.get_parts() if p[0]]
        self._draw_hero(hero, [], self._draw_pregnancy_progress() - self.CONTENT_GAP)

    # Countdown state (birth date still ahead).

    def _draw_countdown(self):
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

    # Special days.

    def _draw_welcome(self):
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

    def _draw_birthday(self):
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

    def draw(self):
        self._img = Image.new('L', (self.width * SCALE, self.height * SCALE), WHITE)
        self._draw = ImageDraw.Draw(self._img)
        # (text, pt, fill, (left, top, right, bottom)) for every text drawn, in screen pixels.
        self.drawn = []
        self._icons = []
        self._title_bottom = self._draw_title()
        {
            NORMAL: self._draw_everyday,
            COUNTDOWN: self._draw_countdown,
            WELCOME: self._draw_welcome,
            BIRTHDAY: self._draw_birthday,
            PREGNANCY: self._draw_pregnancy,
        }[select_state(self.age, self.pregnancy)]()
        self._draw_timestamp()
        img = quantize(self._img.resize((self.width, self.height), Image.LANCZOS))
        for mask, xy in self._icons:
            img.paste(BLACK, xy + (xy[0] + mask.width, xy[1] + mask.height), mask)
        return img
