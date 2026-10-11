"""Layout checks for the pregnancy screen and for every screen in English.

test_screen_ui.py covers the age screens in Polish in detail; these are the
language-independent rules applied to the rest.
"""
import math
import unittest
from datetime import date, datetime, timedelta

from baby_tracker.config import create_models
from baby_tracker.gray_scale import BLACK, DARK_GRAY, LIGHT_GRAY
from baby_tracker.icons import load_icon, moon_icon_path, carriage_icon_path
from baby_tracker.locales import en, pl
from baby_tracker.screen_ui import ScreenUI, select_state, PREGNANCY, COUNTDOWN, WELCOME, BIRTHDAY, NORMAL

WIDTH, HEIGHT = 264, 176
MARGIN = 12
NOW = datetime(2026, 10, 11, 20, 31)
TODAY = NOW.date()
DEVICE_LEVELS = {0x00, 0x80, 0xC0, 0xFF}
WHITE_OUT = 0xFF
LIGHT_GRAY_OUT = 0xC0
EPS = 1.0

LONG_NAME = 'Bartłomiej Maksymilian Brzęczyszczykiewicz'
DESCENDER_NAME = 'Aleksandra Małgorzata Jagiellończyk'
BAR_MID = sum(ScreenUI.PREGNANCY_BAR) // 2


def iso(d):
    return d.isoformat()


def due_in(days):
    return iso(TODAY + timedelta(days=days))


def render(config, locale=en, today=TODAY):
    config = {'name': 'Zosia', **config}
    age, pregnancy = create_models(config, today=today)
    ui = ScreenUI(WIDTH, HEIGHT, age, pregnancy, name=config['name'], now=NOW, locale=locale)
    return ui, ui.draw()


def texts(ui):
    return [t for t, _, _, _ in ui.drawn]


def item(ui, text):
    matches = [d for d in ui.drawn if d[0] == text]
    assert len(matches) == 1, (text, texts(ui))
    return matches[0]


def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


# (label, config, state)
PREGNANCY_CASES = [
    ('mid', {'expected_birth_date': due_in(101)}, PREGNANCY),
    ('first week', {'expected_birth_date': due_in(275)}, PREGNANCY),
    ('whole weeks', {'expected_birth_date': due_in(112)}, PREGNANCY),
    ('tomorrow', {'expected_birth_date': due_in(1)}, PREGNANCY),
    ('due today', {'expected_birth_date': due_in(0)}, PREGNANCY),
    ('overdue', {'expected_birth_date': due_in(-15)}, PREGNANCY),
    ('no name', {'expected_birth_date': due_in(101), 'name': None}, PREGNANCY),
    ('long name', {'expected_birth_date': due_in(101), 'name': LONG_NAME}, PREGNANCY),
    ('descender name', {'expected_birth_date': due_in(101), 'name': DESCENDER_NAME}, PREGNANCY),
    ('baby tracker config', {'birth_date': due_in(101)}, PREGNANCY),
]
OTHER_CASES = [
    ('countdown', {'expected_birth_date': due_in(400)}, COUNTDOWN),
    ('countdown no name', {'expected_birth_date': due_in(400), 'name': None}, COUNTDOWN),
    ('countdown absurd', {'expected_birth_date': '2100-01-01'}, COUNTDOWN),
    ('welcome', {'birth_date': iso(TODAY)}, WELCOME),
    ('welcome no name', {'birth_date': iso(TODAY), 'name': None}, WELCOME),
    ('welcome long name', {'birth_date': iso(TODAY), 'name': LONG_NAME}, WELCOME),
    ('birthday 2nd', {'birth_date': '2024-10-11'}, BIRTHDAY),
    ('birthday 11th', {'birth_date': '2015-10-11'}, BIRTHDAY),
    ('birthday 100th', {'birth_date': '1926-10-11'}, BIRTHDAY),
    ('birthday descender name', {'birth_date': '2024-10-11', 'name': DESCENDER_NAME}, BIRTHDAY),
    ('typical', {'birth_date': '2024-01-01'}, NORMAL),
    ('three-part remainder', {'birth_date': '2025-08-20'}, NORMAL),
    ('no name', {'birth_date': '2024-01-01', 'name': None}, NORMAL),
    ('descender name', {'birth_date': '2024-01-01', 'name': DESCENDER_NAME}, NORMAL),
    ('stale pregnancy config', {'expected_birth_date': '2024-01-01'}, NORMAL),
]
CASES = [(f'{locale.__name__[-2:]} {label}', config, state, locale)
         for locale in (en, pl) for label, config, state in PREGNANCY_CASES] + \
        [(f'en {label}', config, state, en) for label, config, state in OTHER_CASES]


class LayoutMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = [(label, state, locale) + render(config, locale) for label, config, state, locale in CASES]

    def test_states(self):
        for label, state, _, ui, _ in self.rendered:
            with self.subTest(label):
                self.assertEqual(select_state(ui.age, ui.pregnancy), state)

    def test_image_size_mode_and_palette(self):
        for label, _, _, _, img in self.rendered:
            with self.subTest(label):
                self.assertEqual(img.size, (WIDTH, HEIGHT))
                self.assertEqual(img.mode, 'L')
                self.assertLessEqual({v for _, v in img.getcolors()}, DEVICE_LEVELS)

    def test_text_inside_canvas_and_margins(self):
        for label, _, _, ui, _ in self.rendered:
            with self.subTest(label):
                for text, _, _, (l, t, r, b) in ui.drawn:
                    self.assertGreaterEqual(l, MARGIN - EPS, text)
                    self.assertLessEqual(r, WIDTH - MARGIN + EPS, text)
                    self.assertGreaterEqual(t, 0, text)
                    self.assertLessEqual(b, HEIGHT, text)

    def test_no_ink_in_side_margins(self):
        for label, _, _, _, img in self.rendered:
            with self.subTest(label):
                for y in range(HEIGHT):
                    for x in list(range(MARGIN - 1)) + list(range(WIDTH - MARGIN + 1, WIDTH)):
                        self.assertEqual(img.getpixel((x, y)), WHITE_OUT, (label, x, y))

    def test_no_text_overlap(self):
        for label, _, _, ui, _ in self.rendered:
            with self.subTest(label):
                for i, a in enumerate(ui.drawn):
                    for b in ui.drawn[i + 1:]:
                        self.assertFalse(intersects(a[3], b[3]), (a, b))

    def test_minimum_text_size(self):
        for label, _, _, ui, _ in self.rendered:
            with self.subTest(label):
                self.assertGreaterEqual(min(pt for _, pt, _, _ in ui.drawn), 12)

    def test_no_minus_sign(self):
        for label, _, _, ui, _ in self.rendered:
            with self.subTest(label):
                for text in texts(ui):
                    self.assertNotIn('-', text)

    def test_gap_below_title(self):
        for label, _, _, ui, img in self.rendered:
            with self.subTest(label):
                title_bottom = ui.drawn[0][3][3]
                content_top = min(d[3][1] for d in ui.drawn[1:])
                self.assertGreaterEqual(content_top - title_bottom, 8, (title_bottom, content_top))
                for y in range(math.ceil(title_bottom) + 1, math.floor(title_bottom) + 8):
                    self.assertEqual({img.getpixel((x, y)) for x in range(WIDTH)}, {WHITE_OUT}, y)

    def test_timestamp_alone_at_the_bottom(self):
        for label, _, locale, ui, img in self.rendered:
            with self.subTest(label):
                stamp = item(ui, locale.format_timestamp(NOW))
                t = stamp[3][1]
                self.assertTrue(all(d[3][3] <= t for d in ui.drawn if d is not stamp))
                for y in range(math.ceil(t) - 8, math.floor(t)):
                    self.assertEqual({img.getpixel((x, y)) for x in range(WIDTH)}, {WHITE_OUT}, y)

    def test_pregnancy_hero_is_weeks_and_days(self):
        for label, state, locale, ui, _ in self.rendered:
            if state != PREGNANCY:
                continue
            with self.subTest(label):
                digits = [t for t, pt, _, _ in ui.drawn if pt == ScreenUI.HERO_DIGIT_PT]
                expected = [str(v) for v, _ in ui.pregnancy.get_parts() if v]
                self.assertEqual(digits, expected)
                self.assertNotIn('0', digits)

    def test_pregnancy_icons_flank_the_bar(self):
        moon, carriage = load_icon(moon_icon_path), load_icon(carriage_icon_path)
        for label, state, _, _, img in self.rendered:
            if state != PREGNANCY:
                continue
            with self.subTest(label):
                left = [img.getpixel((x, y)) for x in range(MARGIN, MARGIN + moon.width)
                        for y in range(BAR_MID - 10, BAR_MID + 10)]
                right = [img.getpixel((x, y)) for x in range(WIDTH - MARGIN - carriage.width, WIDTH - MARGIN)
                         for y in range(BAR_MID - 10, BAR_MID + 10)]
                self.assertIn(0x00, left)
                self.assertIn(0x00, right)
                # Icons are pasted crisp: black or white only.
                self.assertLessEqual(set(left) | set(right), {0x00, WHITE_OUT})

    def test_english_has_no_polish(self):
        for label, _, locale, ui, _ in self.rendered:
            if locale is not en:
                continue
            with self.subTest(label):
                joined = ' '.join(texts(ui)[1:])  # The name may be Polish.
                for word in ('za ', 'dni', 'ur. ', 'urodziny', 'tygod', 'oraz'):
                    self.assertNotIn(word, joined)


class PregnancyScreenTest(unittest.TestCase):
    def test_typical_en(self):
        ui, img = render({'expected_birth_date': due_in(101)})
        self.assertCountEqual(texts(ui), ['Zosia', '25', 'weeks', '4', 'days', '63.9%', 'in 101 days',
                                          '11 Oct, 20:31'])
        self.assertEqual(item(ui, '25')[1:3], (64, BLACK))
        self.assertEqual(item(ui, 'weeks')[1:3], (16, DARK_GRAY))
        self.assertEqual(item(ui, '63.9%')[1:3], (13, BLACK))
        self.assertEqual(item(ui, 'in 101 days')[1:3], (13, DARK_GRAY))
        self.assertAlmostEqual(item(ui, '63.9%')[3][0], MARGIN, delta=2)
        self.assertAlmostEqual(item(ui, 'in 101 days')[3][2], WIDTH - MARGIN, delta=EPS)
        # Bar: filled up to ~64% of its length, track after that.
        moon, carriage = load_icon(moon_icon_path), load_icon(carriage_icon_path)
        bar_left = MARGIN + moon.width + ScreenUI.ICON_GAP
        bar_right = WIDTH - MARGIN - carriage.width - ScreenUI.ICON_GAP
        split = bar_left + (bar_right - bar_left) * 179 / 280
        self.assertEqual(img.getpixel((round(split) - 3, BAR_MID)), 0x00)
        self.assertEqual(img.getpixel((round(split) + 3, BAR_MID)), LIGHT_GRAY_OUT)

    def test_typical_pl(self):
        ui, _ = render({'expected_birth_date': due_in(101)}, locale=pl)
        self.assertCountEqual(texts(ui), ['Zosia', '25', 'tygodni', '4', 'dni', '63,9%', 'za 101 dni',
                                          '11.10, 20:31'])

    def test_whole_weeks_single_column(self):
        ui, _ = render({'expected_birth_date': due_in(112)})
        self.assertIn('24', texts(ui))
        self.assertIn('weeks', texts(ui))
        self.assertNotIn('days', texts(ui))
        self.assertAlmostEqual((item(ui, '24')[3][0] + item(ui, '24')[3][2]) / 2, WIDTH / 2, delta=2)

    def test_first_week_days_only(self):
        ui, _ = render({'expected_birth_date': due_in(275)})
        self.assertCountEqual(texts(ui), ['Zosia', '5', 'days', '1.8%', 'in 275 days', '11 Oct, 20:31'])

    def test_due_today_and_overdue(self):
        ui, _ = render({'expected_birth_date': due_in(0)})
        self.assertIn('due today', texts(ui))
        self.assertIn('100.0%', texts(ui))
        ui, _ = render({'expected_birth_date': due_in(-1)}, locale=pl)
        self.assertIn('1 dzień po terminie', texts(ui))

    def test_no_name_title_is_the_due_date_without_born(self):
        ui, _ = render({'expected_birth_date': '2027-01-20', 'name': None})
        self.assertEqual(ui.drawn[0][0], '20 January 2027')

    def test_birth_before_due_date(self):
        ui, _ = render({'expected_birth_date': due_in(10), 'birth_date': due_in(-3)})
        self.assertIn('days', texts(ui))
        self.assertIn('1st birthday', texts(ui))


class EnglishScreensTest(unittest.TestCase):
    def test_everyday(self):
        ui, _ = render({'birth_date': '2024-01-01'})
        self.assertCountEqual(texts(ui), ['Zosia', '2', 'years', '9', 'months', 'plus ', '1 week and 3 days',
                                          '3rd birthday', 'in 82 days', '11 Oct, 20:31'])

    def test_no_name_title(self):
        ui, _ = render({'birth_date': '2026-04-30', 'name': None})
        self.assertEqual(ui.drawn[0][0], 'born 30 April 2026')

    def test_countdown_has_no_prefix_run(self):
        ui, _ = render({'expected_birth_date': due_in(400)})
        self.assertCountEqual(texts(ui), ['Zosia', '400', 'days', 'until birth', '15 November 2027',
                                          '11 Oct, 20:31'])

    def test_welcome(self):
        ui, _ = render({'birth_date': iso(TODAY)})
        self.assertIn('Welcome to the world!', texts(ui))
        ui, _ = render({'birth_date': iso(TODAY), 'name': None})
        self.assertIn('day one', texts(ui))

    def test_birthday(self):
        ui, _ = render({'birth_date': '2024-10-11'})
        self.assertCountEqual(texts(ui), ['Zosia', '2nd', 'birthday', 'Hip hip hooray!', '11 Oct, 20:31'])


if __name__ == '__main__':
    unittest.main()
