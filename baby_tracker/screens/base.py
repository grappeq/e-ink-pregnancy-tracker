from datetime import datetime

from PIL import Image, ImageDraw

from ..fonts import create_font, BLACK_WEIGHT, BOLD_WEIGHT, SEMI_BOLD_WEIGHT
from ..gray_scale import WHITE, LIGHT_GRAY, DARK_GRAY, BLACK, quantize
from ..locales import get_locale

# Supersampling keeps curves smooth once quantized down to the panel's 4 gray levels.
SCALE = 4

NORMAL = 'normal'
COUNTDOWN = 'countdown'
WELCOME = 'welcome'
BIRTHDAY = 'birthday'
PREGNANCY = 'pregnancy'


def title_candidates(name, birth_date, born, locale):
    """(text, pt) pairs to try in order; the caller truncates the last one if nothing fits."""
    if name:
        return [(name, 17), (name, 15)]
    prefix = locale.BORN_PREFIX if born else ''
    long_form = prefix + locale.format_date(birth_date)
    return [(long_form, 17), (long_form, 15), (prefix + locale.format_short_date(birth_date), 15)]


class Screen:
    """Shared layout and drawing helpers; subclasses draw their content between the title and timestamp."""
    STATE = None
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
    STAMP_PT = 12
    STAMP_BASELINE = 170
    WISH_MIN_PT = 16

    def __init__(self, width, height, age=None, pregnancy=None, name=None, now=None, locale=None):
        if age is None and pregnancy is None:
            raise ValueError('A screen needs an age, a pregnancy or both')
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

    def _draw_content(self):
        raise NotImplementedError

    def draw(self):
        self._img = Image.new('L', (self.width * SCALE, self.height * SCALE), WHITE)
        self._draw = ImageDraw.Draw(self._img)
        # (text, pt, fill, (left, top, right, bottom)) for every text drawn, in screen pixels.
        self.drawn = []
        self._icons = []
        self._title_bottom = self._draw_title()
        self._draw_content()
        self._draw_timestamp()
        img = quantize(self._img.resize((self.width, self.height), Image.LANCZOS))
        for mask, xy in self._icons:
            img.paste(BLACK, xy + (xy[0] + mask.width, xy[1] + mask.height), mask)
        return img
