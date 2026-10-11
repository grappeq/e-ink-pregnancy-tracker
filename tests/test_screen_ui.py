import math
import re
import unittest
from datetime import date, datetime, timedelta

from baby_tracker.age import Age
from baby_tracker.fonts import BLACK_WEIGHT
from baby_tracker.gray_scale import BLACK, DARK_GRAY, LIGHT_GRAY
from baby_tracker.screen_ui import (
    ScreenUI, select_state, hero_parts, title_candidates, NORMAL, COUNTDOWN, WELCOME, BIRTHDAY,
)

WIDTH, HEIGHT = 264, 176
MARGIN = 12
NOW = datetime(2026, 10, 11, 20, 31)
TODAY = NOW.date()
DEVICE_LEVELS = {0x00, 0x80, 0xC0, 0xFF}
WHITE_OUT = 0xFF
LIGHT_GRAY_OUT = 0xC0
STAMP = '11.10, 20:31'
# Sub-pixel slack for comparing float text boxes against pixel targets.
EPS = 1.0

LONG_NAME = 'Bartłomiej Maksymilian Brzęczyszczykiewicz'
# Too wide for the title at 17 pt, fits at 15 pt (checked in the test itself).
MEDIUM_NAME = 'Aleksandra Maria Kowalska'
# Descenders (ł, j, g, ń) push the title ink lower.
DESCENDER_NAME = 'Aleksandra Małgorzata Jagiellończyk'


def iso(d):
    return d.strftime('%Y-%m-%d')


def render(birth_date, name='Zosia', today=TODAY, now=NOW):
    ui = ScreenUI(WIDTH, HEIGHT, Age(birth_date, today=today), name=name, now=now)
    return ui, ui.draw()


def texts(ui):
    return [t for t, _, _, _ in ui.drawn]


def item(ui, text):
    matches = [d for d in ui.drawn if d[0] == text]
    assert len(matches) == 1, (text, texts(ui))
    return matches[0]


def centre_x(box):
    return (box[0] + box[2]) / 2


def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


class SelectStateTest(unittest.TestCase):
    def test_future_birth_is_countdown(self):
        self.assertEqual(select_state(Age('2026-10-25', today=TODAY)), COUNTDOWN)
        self.assertEqual(select_state(Age('2026-10-12', today=TODAY)), COUNTDOWN)

    def test_day_zero_is_welcome(self):
        self.assertEqual(select_state(Age('2026-10-11', today=TODAY)), WELCOME)

    def test_past_birth_is_normal(self):
        self.assertEqual(select_state(Age('2024-01-01', today=TODAY)), NORMAL)

    def test_day_one_is_normal(self):
        self.assertEqual(select_state(Age('2026-10-10', today=TODAY)), NORMAL)

    def test_birthdays(self):
        self.assertEqual(select_state(Age('2025-10-11', today=TODAY)), BIRTHDAY)
        self.assertEqual(select_state(Age('2021-10-11', today=TODAY)), BIRTHDAY)

    def test_day_after_birthday_is_normal(self):
        age = Age('2025-10-10', today=TODAY)
        self.assertEqual(age.get_parts(), [(1, 'y'), (0, 'm'), (0, 'w'), (1, 'd')])
        self.assertEqual(select_state(age), NORMAL)

    def test_month_iversary_is_normal(self):
        age = Age('2026-09-11', today=TODAY)
        self.assertEqual(age.get_parts(), [(0, 'y'), (1, 'm'), (0, 'w'), (0, 'd')])
        self.assertEqual(select_state(age), NORMAL)

    def test_leap_day_birth(self):
        self.assertEqual(select_state(Age('2024-02-29', today=date(2025, 2, 28))), BIRTHDAY)
        self.assertEqual(select_state(Age('2024-02-29', today=date(2025, 3, 1))), NORMAL)
        self.assertEqual(select_state(Age('2024-02-29', today=date(2028, 2, 29))), BIRTHDAY)

    def test_feb_28_birth_in_leap_year(self):
        self.assertEqual(select_state(Age('2023-02-28', today=date(2024, 2, 28))), BIRTHDAY)
        self.assertEqual(select_state(Age('2023-02-28', today=date(2024, 2, 29))), NORMAL)


class HeroPartsTest(unittest.TestCase):
    def test_two_units_with_remainder(self):
        parts = [(2, 'y'), (9, 'm'), (1, 'w'), (3, 'd')]
        self.assertEqual(hero_parts(parts), ([(2, 'y'), (9, 'm')], [(1, 'w'), (3, 'd')]))

    def test_zero_month_skipped(self):
        parts = [(1, 'y'), (0, 'm'), (2, 'w'), (1, 'd')]
        self.assertEqual(hero_parts(parts), ([(1, 'y'), (2, 'w')], [(1, 'd')]))

    def test_two_zeros_skipped_no_remainder(self):
        parts = [(1, 'y'), (0, 'm'), (0, 'w'), (3, 'd')]
        self.assertEqual(hero_parts(parts), ([(1, 'y'), (3, 'd')], []))

    def test_single_unit(self):
        parts = [(0, 'y'), (0, 'm'), (0, 'w'), (5, 'd')]
        self.assertEqual(hero_parts(parts), ([(5, 'd')], []))

    def test_day_zero_fallback(self):
        # Only reachable when a caller skips select_state() (day 0 is WELCOME).
        parts = [(0, 'y'), (0, 'm'), (0, 'w'), (0, 'd')]
        self.assertEqual(hero_parts(parts), ([(0, 'd')], []))

    def test_every_day_has_one_or_two_non_zero_hero_units(self):
        for birth in (date(2024, 1, 31), date(2024, 2, 29), date(2025, 3, 15)):
            for offset in range(1, 801):
                today = birth + timedelta(days=offset)
                parts = Age(iso(birth), today=today).get_parts()
                hero, rest = hero_parts(parts)
                msg = (iso(birth), iso(today), parts)
                self.assertTrue(1 <= len(hero) <= 2, msg)
                self.assertTrue(all(v > 0 for v, _ in hero + rest), msg)
                self.assertEqual(hero + rest, [p for p in parts if p[0]], msg)


class TitleCandidatesTest(unittest.TestCase):
    BIRTH = date(2026, 4, 30)

    def test_name(self):
        self.assertEqual(title_candidates('Zosia', self.BIRTH, True), [('Zosia', 17), ('Zosia', 15)])

    def test_no_name_born(self):
        self.assertEqual(title_candidates(None, self.BIRTH, True), [
            ('ur. 30 kwietnia 2026', 17), ('ur. 30 kwietnia 2026', 15), ('ur. 30.04.2026', 15)])

    def test_no_name_future(self):
        self.assertEqual(title_candidates(None, self.BIRTH, False), [
            ('30 kwietnia 2026', 17), ('30 kwietnia 2026', 15), ('30.04.2026', 15)])


class TitleFittingTest(unittest.TestCase):
    def assert_title_group_in_margins(self, img):
        # The heart is not text, so check the title rows' pixels directly.
        for y in range(0, 32):
            for x in list(range(MARGIN)) + list(range(WIDTH - MARGIN, WIDTH)):
                self.assertEqual(img.getpixel((x, y)), WHITE_OUT, (x, y))

    def test_short_name_at_17(self):
        ui, img = render('2024-01-01', name='Zosia')
        self.assertEqual(ui.drawn[0][:3], ('Zosia', 17, BLACK))
        self.assert_title_group_in_margins(img)

    def test_name_that_only_fits_at_15(self):
        ui, img = render('2024-01-01', name=MEDIUM_NAME)
        max_width = WIDTH - 2 * MARGIN - 2 * ScreenUI.HEART_RADIUS - ScreenUI.HEART_GAP
        self.assertGreater(ui._text_size(MEDIUM_NAME, ui._font(17, BLACK_WEIGHT))[0], max_width)
        self.assertEqual(ui.drawn[0][:2], (MEDIUM_NAME, 15))
        self.assert_title_group_in_margins(img)

    def test_long_name_truncated_with_ellipsis(self):
        ui, img = render('2024-01-01', name=LONG_NAME)
        text, pt, _, box = ui.drawn[0]
        self.assertEqual(pt, 15)
        self.assertTrue(text.endswith('…'), text)
        self.assertTrue(LONG_NAME.startswith(text[:-1]), text)
        self.assertLess(len(text), len(LONG_NAME))
        self.assertGreaterEqual(box[0], MARGIN)
        self.assertLessEqual(box[2], WIDTH - MARGIN)
        self.assert_title_group_in_margins(img)

    def test_no_name_shows_birth_date(self):
        ui, _ = render('2026-04-30', name=None)
        self.assertEqual(ui.drawn[0][:2], ('ur. 30 kwietnia 2026', 17))

    def test_whitespace_name_treated_as_no_name(self):
        ui, _ = render('2026-04-30', name='   \t ')
        self.assertEqual(ui.drawn[0][:2], ('ur. 30 kwietnia 2026', 17))

    def test_name_is_stripped(self):
        ui, _ = render('2024-01-01', name='  Zosia  ')
        self.assertEqual(ui.drawn[0][0], 'Zosia')

    def test_no_name_future_drops_prefix_and_date_line(self):
        ui, _ = render('2026-10-25', name=None)
        self.assertEqual(ui.drawn[0][:2], ('25 października 2026', 17))
        self.assertNotIn('ur.', ' '.join(texts(ui)))
        self.assertEqual(texts(ui).count('25 października 2026'), 1)
        self.assertIn('do narodzin', texts(ui))

    def test_hostile_name_drawn_verbatim_and_contained(self):
        name = '<script>alert(1)</script>‮%s{0}'
        ui, img = render('2024-01-01', name=name)
        text = ui.drawn[0][0]
        self.assertTrue(text == name or (text.endswith('…') and name.startswith(text[:-1])), text)
        self.assert_title_group_in_margins(img)


# (label, birth_date, name)
NORMAL_CASES = [
    ('typical', '2024-01-01', 'Zosia'),
    ('young', '2026-09-01', 'Zosia'),
    ('day 1', '2026-10-10', 'Zosia'),
    ('zero-skip', '2025-09-26', 'Zosia'),
    ('two-unit no remainder', '2024-01-11', 'Zosia'),
    ('month-iversary', '2026-09-11', 'Zosia'),
    ('day after birthday', '2025-10-10', 'Zosia'),
    ('born on the 31st', '2025-08-31', 'Zosia'),
    ('leap day', '2024-02-29', 'Zosia'),
    ('no name', '2024-01-01', None),
    ('long name', '2024-01-01', LONG_NAME),
    ('descender name', '2024-01-01', DESCENDER_NAME),
]
COUNTDOWN_CASES = [
    ('countdown N=14', '2026-10-25', 'Zosia'),
    ('countdown N=1', '2026-10-12', 'Zosia'),
    ('countdown ~1200', iso(TODAY + timedelta(days=1200)), 'Zosia'),
    ('countdown absurd', '2100-01-01', 'Zosia'),
    ('countdown no name', '2026-10-25', None),
    ('countdown long name', '2026-10-25', LONG_NAME),
    ('countdown descender name', '2026-10-25', DESCENDER_NAME),
]
WELCOME_CASES = [
    ('welcome', '2026-10-11', 'Zosia'),
    ('welcome no name', '2026-10-11', None),
    ('welcome long name', '2026-10-11', LONG_NAME),
    ('welcome descender name', '2026-10-11', DESCENDER_NAME),
]
BIRTHDAY_CASES = [
    ('birthday 1st', '2025-10-11', 'Zosia'),
    ('birthday 2nd', '2024-10-11', 'Zosia'),
    ('birthday 10th', '2016-10-11', 'Zosia'),
    ('birthday 100th', '1926-10-11', 'Zosia'),
    ('birthday no name', '2024-10-11', None),
    ('birthday long name', '2024-10-11', LONG_NAME),
    ('birthday descender name', '2024-10-11', DESCENDER_NAME),
]
ALL_CASES = NORMAL_CASES + COUNTDOWN_CASES + WELCOME_CASES + BIRTHDAY_CASES
STATE_OF_GROUP = [(NORMAL_CASES, NORMAL), (COUNTDOWN_CASES, COUNTDOWN),
                  (WELCOME_CASES, WELCOME), (BIRTHDAY_CASES, BIRTHDAY)]
BAR_MID = (ScreenUI.PROGRESS_BAR[0] + ScreenUI.PROGRESS_BAR[1]) // 2


def is_progress_label(d):
    return d[1] == ScreenUI.PROGRESS_LABEL_PT and (d[0].endswith('. urodziny') or d[0].startswith('za '))


def assert_bar_absent(test, img):
    for y in range(ScreenUI.PROGRESS_BAR[0] + 1, ScreenUI.PROGRESS_BAR[1] + 1):
        test.assertEqual({img.getpixel((x, y)) for x in range(WIDTH)}, {WHITE_OUT}, y)


class RenderMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = {label: render(birth, name) for label, birth, name in ALL_CASES}

    def each(self, *groups):
        cases = [c for g in groups for c in g] if groups else ALL_CASES
        return [(label,) + self.rendered[label] for label, _, _ in cases]

    def test_image_size_mode_and_palette(self):
        for label, _, img in self.each():
            with self.subTest(label):
                self.assertEqual(img.size, (WIDTH, HEIGHT))
                self.assertEqual(img.mode, 'L')
                self.assertLessEqual({v for _, v in img.getcolors()}, DEVICE_LEVELS)

    def test_states(self):
        for group, state in STATE_OF_GROUP:
            for label, ui, _ in self.each(group):
                with self.subTest(label):
                    self.assertEqual(select_state(ui.age), state)

    def test_no_minus_sign(self):
        for label, ui, _ in self.each():
            with self.subTest(label):
                for text in texts(ui):
                    self.assertNotIn('-', text)
                    self.assertNotIn('\u2212', text)

    def test_no_zero_quantity_anywhere(self):
        for label, ui, _ in self.each():
            with self.subTest(label):
                for text in texts(ui):
                    self.assertNotRegex(text, r'(^|\D)0( |$)')

    def test_hero_has_one_or_two_digits(self):
        for label, ui, _ in self.each(NORMAL_CASES):
            with self.subTest(label):
                digits = [t for t, pt, _, _ in ui.drawn if pt == ScreenUI.HERO_DIGIT_PT]
                self.assertTrue(1 <= len(digits) <= 2, digits)

    def test_no_progress_row_outside_everyday(self):
        for label, ui, img in self.each(COUNTDOWN_CASES, WELCOME_CASES, BIRTHDAY_CASES):
            with self.subTest(label):
                self.assertFalse([d for d in ui.drawn if is_progress_label(d)])
                self.assertFalse([t for t in texts(ui) if t.startswith('za ')])
                assert_bar_absent(self, img)

    def test_countdown_never_mentions_birthdays(self):
        for label, ui, _ in self.each(COUNTDOWN_CASES):
            with self.subTest(label):
                self.assertNotIn('urodziny', ' '.join(texts(ui)))

    def test_text_inside_canvas_and_margins(self):
        for label, ui, _ in self.each():
            with self.subTest(label):
                for text, _, _, (l, t, r, b) in ui.drawn:
                    self.assertGreaterEqual(l, MARGIN - EPS, text)
                    self.assertLessEqual(r, WIDTH - MARGIN + EPS, text)
                    self.assertGreaterEqual(t, 0, text)
                    self.assertLessEqual(b, HEIGHT, text)

    def test_no_ink_in_side_margins(self):
        # Covers the shapes (title heart, welcome heart and dots, birthday hearts, bar) too.
        for label, _, img in self.each():
            with self.subTest(label):
                for y in range(HEIGHT):
                    for x in list(range(MARGIN - 1)) + list(range(WIDTH - MARGIN + 1, WIDTH)):
                        self.assertEqual(img.getpixel((x, y)), WHITE_OUT, (x, y))

    def test_no_text_overlap(self):
        for label, ui, _ in self.each():
            with self.subTest(label):
                for i, a in enumerate(ui.drawn):
                    for b in ui.drawn[i + 1:]:
                        self.assertFalse(intersects(a[3], b[3]), (a, b))

    def test_timestamp_postmark(self):
        for label, ui, img in self.each():
            with self.subTest(label):
                stamp = item(ui, STAMP)
                _, pt, fill, (l, t, r, b) = stamp
                self.assertEqual(pt, ScreenUI.STAMP_PT)
                self.assertEqual(fill, LIGHT_GRAY)
                self.assertAlmostEqual(r, WIDTH - MARGIN, delta=EPS)
                others = [d for d in ui.drawn if d is not stamp]
                self.assertTrue(all(d[1] > pt for d in others), [d[:2] for d in others])
                # Alone on its row, at the bottom, with >= 8 px of clear ink above it.
                self.assertTrue(all(d[3][3] <= t for d in others), [d for d in others if d[3][3] > t])
                for y in range(math.ceil(t) - 8, math.floor(t)):
                    self.assertEqual({img.getpixel((x, y)) for x in range(WIDTH)}, {WHITE_OUT}, y)

    def test_minimum_text_size(self):
        for label, ui, _ in self.each():
            with self.subTest(label):
                self.assertGreaterEqual(min(pt for _, pt, _, _ in ui.drawn), 12)

    def test_gap_above_progress_label(self):
        for label, ui, _ in self.each(NORMAL_CASES):
            with self.subTest(label):
                labels = [d for d in ui.drawn if is_progress_label(d)]
                self.assertEqual(len(labels), 2, texts(ui))
                label_top = min(d[3][1] for d in labels)
                content = [d for d in ui.drawn[1:] if d not in labels and d[0] != STAMP]
                content_bottom = max(d[3][3] for d in content)
                self.assertGreaterEqual(label_top - content_bottom, 8, (content_bottom, label_top))

    def test_gap_below_title(self):
        # Ink-to-ink >= 8 px from the title to whatever comes next, text or shape.
        for label, ui, img in self.each():
            with self.subTest(label):
                title_bottom = ui.drawn[0][3][3]
                content_top = min(d[3][1] for d in ui.drawn[1:])
                self.assertGreaterEqual(content_top - title_bottom, 8, (title_bottom, content_top))
                for y in range(math.ceil(title_bottom) + 1, math.floor(title_bottom) + 8):
                    self.assertEqual({img.getpixel((x, y)) for x in range(WIDTH)}, {WHITE_OUT}, y)

    def test_heart_present_in_every_state(self):
        # The heart is drawn just left of the title text in BLACK.
        for label, ui, img in self.each():
            with self.subTest(label):
                l, t, r, b = ui.drawn[0][3]
                heart = [img.getpixel((x, y)) for x in range(int(l) - 18, int(l) - 2)
                         for y in range(8, 24)]
                self.assertIn(0x00, heart)

    def test_no_date_repeated(self):
        for label, ui, _ in self.each():
            with self.subTest(label):
                dates = [t for t in texts(ui) if re.search(r'\d{4}', t)]
                stripped = [t.replace('ur. ', '') for t in dates]
                self.assertEqual(len(stripped), len(set(stripped)), dates)


class ApprovedExamplesTest(unittest.TestCase):
    def test_typical_everyday(self):
        ui, img = render('2024-01-01', name='Zosia')
        self.assertCountEqual(texts(ui), [
            'Zosia', '2', 'lata', '9', 'miesięcy', 'oraz ', '1 tydzień i 3 dni',
            '3. urodziny', 'za 82 dni', STAMP])
        self.assertEqual(item(ui, '2')[1:3], (64, BLACK))
        self.assertEqual(item(ui, '9')[1:3], (64, BLACK))
        self.assertEqual(item(ui, 'lata')[1:3], (16, DARK_GRAY))
        self.assertEqual(item(ui, 'miesięcy')[1:3], (16, DARK_GRAY))
        self.assertAlmostEqual(centre_x(item(ui, '2')[3]), 66, delta=2)
        self.assertAlmostEqual(centre_x(item(ui, '9')[3]), 198, delta=2)
        self.assertAlmostEqual(centre_x(item(ui, 'lata')[3]), 66, delta=2)
        self.assertAlmostEqual(centre_x(item(ui, 'miesięcy')[3]), 198, delta=2)
        # Unit words sit under their digits.
        self.assertGreaterEqual(item(ui, 'lata')[3][1], item(ui, '2')[3][3])

        oraz, rest = item(ui, 'oraz '), item(ui, '1 tydzień i 3 dni')
        self.assertEqual(oraz[1:3], (15, DARK_GRAY))
        self.assertEqual(rest[1:3], (15, BLACK))
        self.assertAlmostEqual((oraz[3][0] + rest[3][2]) / 2, 132, delta=2)
        self.assertGreater(oraz[3][1], item(ui, 'lata')[3][3])

        label, days = item(ui, '3. urodziny'), item(ui, 'za 82 dni')
        self.assertEqual(label[1:3], (13, DARK_GRAY))
        self.assertEqual(days[1:3], (13, BLACK))
        self.assertAlmostEqual(label[3][0], MARGIN, delta=2)
        self.assertAlmostEqual(days[3][2], WIDTH - MARGIN, delta=EPS)

        # Divider between the two hero columns.
        digit_box = item(ui, '2')[3]
        column = [img.getpixel((x, y)) for x in (131, 132)
                  for y in range(int(digit_box[1]) + 8, int(digit_box[3]))]
        self.assertIn(LIGHT_GRAY_OUT, column)

        # Bar fill is visible and there is no knob above the bar.
        bar_mid = (ScreenUI.PROGRESS_BAR[0] + ScreenUI.PROGRESS_BAR[1]) // 2
        self.assertEqual(img.getpixel((MARGIN + 6, bar_mid)), 0x00)
        self.assertEqual(img.getpixel((WIDTH - MARGIN - 6, bar_mid)), LIGHT_GRAY_OUT)

    def test_zero_skip(self):
        ui, _ = render('2025-09-26', name='Zosia')
        self.assertCountEqual(texts(ui), [
            'Zosia', '1', 'rok', '2', 'tygodnie', 'oraz ', '1 dzień',
            '2. urodziny', 'za 350 dni', STAMP])

    def test_two_units_without_remainder(self):
        ui, _ = render('2024-01-11', name='Zosia')
        self.assertCountEqual(texts(ui), [
            'Zosia', '2', 'lata', '9', 'miesięcy', '3. urodziny', 'za 92 dni', STAMP])

    def test_single_unit_hero(self):
        ui, img = render('2026-10-06', name='Zosia')
        self.assertIn('5', texts(ui))
        self.assertIn('dni', texts(ui))
        self.assertAlmostEqual(centre_x(item(ui, '5')[3]), 132, delta=2)
        self.assertNotIn('oraz ', texts(ui))

    def test_day_after_birthday_bar_fill_is_at_least_2h(self):
        ui, img = render('2025-10-10', name='Zosia')
        self.assertIn('2. urodziny', texts(ui))
        self.assertIn('za 364 dni', texts(ui))
        h = ScreenUI.PROGRESS_BAR[1] - ScreenUI.PROGRESS_BAR[0]
        black = [x for x in range(WIDTH) if img.getpixel((x, BAR_MID)) == 0x00]
        # One px of antialiasing slack at the rounded right end.
        self.assertGreaterEqual(len(black), 2 * h - 1, black)
        self.assertEqual(black, list(range(black[0], black[-1] + 1)))
        self.assertLessEqual(black[0], MARGIN + 1)
        self.assertEqual(img.getpixel((MARGIN + 2 * h + 4, BAR_MID)), LIGHT_GRAY_OUT)

    def test_welcome(self):
        ui, img = render('2026-10-11', name='Zosia')
        self.assertCountEqual(texts(ui), ['Zosia', 'Witaj na świecie!', '11 października 2026', STAMP])
        greeting, note = item(ui, 'Witaj na świecie!'), item(ui, '11 października 2026')
        self.assertEqual(greeting[1:3], (22, BLACK))
        self.assertEqual(note[1:3], (15, DARK_GRAY))
        self.assertAlmostEqual(centre_x(greeting[3]), 132, delta=2)
        self.assertAlmostEqual(centre_x(note[3]), 132, delta=2)
        self.assertGreaterEqual(note[3][1] - greeting[3][3], 8)
        # Big heart at (132, 58) with garland dots either side.
        self.assertEqual(img.getpixel((132, 58)), 0x00)
        for dx in (-38, 38):
            self.assertEqual(img.getpixel((132 + dx, 58)), LIGHT_GRAY_OUT, dx)
        for dx in (-52, 52):
            self.assertNotEqual(img.getpixel((132 + dx, 58)), WHITE_OUT, dx)
        joined = ' '.join(texts(ui))
        self.assertNotIn('dni', joined)
        self.assertNotIn('dzień', joined)
        self.assertNotIn('0', [t for t in texts(ui)])

    def test_welcome_no_name(self):
        ui, _ = render('2026-10-11', name=None)
        self.assertCountEqual(texts(ui), [
            'ur. 11 października 2026', 'Witaj na świecie!', 'pierwszy dzień', STAMP])
        self.assertEqual(ui.drawn[0][0], 'ur. 11 października 2026')
        self.assertEqual(item(ui, 'pierwszy dzień')[1:3], (15, DARK_GRAY))

    def test_birthday(self):
        ui, img = render('2024-10-11', name='Zosia')
        self.assertCountEqual(texts(ui), ['Zosia', '2.', 'urodziny', 'Sto lat!', STAMP])
        ordinal, word, wish = item(ui, '2.'), item(ui, 'urodziny'), item(ui, 'Sto lat!')
        self.assertEqual(ordinal[1:3], (64, BLACK))
        self.assertEqual(word[1:3], (16, DARK_GRAY))
        self.assertEqual(wish[1:3], (22, BLACK))
        for d in (ordinal, word, wish):
            self.assertAlmostEqual(centre_x(d[3]), 132, delta=3, msg=d)
        self.assertGreaterEqual(word[3][1], ordinal[3][3])
        self.assertGreaterEqual(wish[3][1] - word[3][3], 8)
        # Hearts flank the ordinal at cy=64, cx = 132 +- (ordinal_w / 2 + 18).
        ordinal_w = ui._text_size('2.', ui._font(64, BLACK_WEIGHT))[0]
        offset = ordinal_w / 2 + ScreenUI.BIRTHDAY_HEART_GAP
        for x in (132 - offset, 132 + offset):
            self.assertEqual(img.getpixel((round(x), 64)), 0x00, x)
        self.assertFalse([t for t in texts(ui) if t.startswith('za ')])
        assert_bar_absent(self, img)

    def test_birthday_ordinal_keeps_dot(self):
        for birth, ordinal in (('2025-10-11', '1.'), ('2016-10-11', '10.'), ('1926-10-11', '100.')):
            with self.subTest(ordinal):
                ui, _ = render(birth, name='Zosia')
                self.assertIn(ordinal, texts(ui))

    def test_100th_birthday_fits_at_64(self):
        ui, img = render('1926-10-11', name='Zosia')
        text, pt, _, (l, t, r, b) = item(ui, '100.')
        self.assertEqual(pt, 64)
        self.assertGreaterEqual(l, MARGIN)
        self.assertLessEqual(r, WIDTH - MARGIN)
        for y in range(40, 100):
            for x in list(range(MARGIN)) + list(range(WIDTH - MARGIN, WIDTH)):
                self.assertEqual(img.getpixel((x, y)), WHITE_OUT, (x, y))

    def test_countdown_n14(self):
        ui, img = render('2026-10-25', name='Zosia')
        self.assertCountEqual(texts(ui), [
            'Zosia', 'za', '14', 'dni', 'do narodzin', '25 października 2026', STAMP])
        self.assertEqual(item(ui, 'za')[1:3], (20, DARK_GRAY))
        self.assertEqual(item(ui, '14')[1:3], (64, BLACK))
        self.assertEqual(item(ui, 'dni')[1:3], (22, DARK_GRAY))
        self.assertEqual(item(ui, 'do narodzin')[1:3], (15, DARK_GRAY))
        self.assertEqual(item(ui, '25 października 2026')[1:3], (14, BLACK))
        za, n, unit = item(ui, 'za')[3], item(ui, '14')[3], item(ui, 'dni')[3]
        self.assertTrue(za[2] < n[0] < n[2] < unit[0])
        self.assertAlmostEqual((za[0] + unit[2]) / 2, 132, delta=2)
        self.assertAlmostEqual(centre_x(item(ui, 'do narodzin')[3]), 132, delta=2)

    def test_countdown_n1_uses_singular(self):
        ui, _ = render('2026-10-12', name='Zosia')
        self.assertCountEqual(texts(ui), [
            'Zosia', 'za', '1', 'dzień', 'do narodzin', '12 października 2026', STAMP])

    def test_countdown_absurd_date_still_fits(self):
        ui, _ = render('2100-01-01', name='Zosia')
        days = str((date(2100, 1, 1) - TODAY).days)
        self.assertIn(days, texts(ui))
        self.assertIn('dni', texts(ui))
        self.assertGreaterEqual(item(ui, days)[1], ScreenUI.COUNTDOWN_MIN_DIGIT_PT)

    def test_timestamp_format(self):
        ui, _ = render('2024-01-01', now=datetime(2026, 1, 2, 3, 4))
        self.assertIn('02.01, 03:04', texts(ui))


class ReviewFixesTest(unittest.TestCase):
    def test_name_whitespace_is_collapsed(self):
        ui, _ = render('2024-01-01', name='Zo\nsia\t K.')
        self.assertIn('Zo sia K.', texts(ui))

    def test_non_string_name_is_ignored(self):
        ui, _ = render('2026-04-30', name=123)
        self.assertIn('ur. 30 kwietnia 2026', texts(ui))

    def test_huge_name_is_capped_and_truncated(self):
        ui, _ = render('2024-01-01', name='a' * 100000)
        title = ui.drawn[0][0]
        self.assertTrue(title.endswith('…'))
        self.assertLessEqual(len(title), ScreenUI.NAME_MAX_LENGTH + 1)

    def test_draw_twice_records_once(self):
        ui = ScreenUI(WIDTH, HEIGHT, Age('2024-01-01', today=TODAY), name='Zosia', now=NOW)
        first = ui.draw()
        count = len(ui.drawn)
        second = ui.draw()
        self.assertEqual(len(ui.drawn), count)
        self.assertEqual(list(first.getdata()), list(second.getdata()))

    def test_countdown_without_date_line_is_recentred(self):
        named, _ = render('2026-10-25')
        unnamed, _ = render('2026-10-25', name=None)
        shift = item(unnamed, 'do narodzin')[3][1] - item(named, 'do narodzin')[3][1]
        self.assertAlmostEqual(shift, 11, delta=1)
        self.assertAlmostEqual(item(unnamed, '14')[3][1] - item(named, '14')[3][1], shift, delta=0.5)


if __name__ == '__main__':
    unittest.main()
