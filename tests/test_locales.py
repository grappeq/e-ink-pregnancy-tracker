import unittest
from datetime import date, datetime

from baby_tracker.locales import en, pl


class InterfaceTest(unittest.TestCase):
    def test_locales_expose_what_the_screen_uses(self):
        used = {'BORN_PREFIX', 'REMAINDER_PREFIX', 'COUNTDOWN_PREFIX', 'COUNTDOWN_NOTE', 'WELCOME', 'FIRST_DAY',
                'BIRTHDAY_WORD', 'BIRTHDAY_WISH', 'DUE_TODAY', 'unit_word', 'format_quantity', 'join_words',
                'format_date', 'format_short_date', 'format_timestamp', 'format_percent', 'birthday_ordinal',
                'next_birthday', 'in_days', 'overdue'}
        for locale in (en, pl):
            self.assertLessEqual(used, set(dir(locale)), locale.__name__)


class EnglishTest(unittest.TestCase):
    def test_plurals(self):
        self.assertEqual(en.format_quantity(1, 'y'), '1 year')
        self.assertEqual(en.format_quantity(2, 'y'), '2 years')
        self.assertEqual(en.format_quantity(1, 'w'), '1 week')
        self.assertEqual(en.format_quantity(0, 'd'), '0 days')
        self.assertEqual(en.format_quantity(21, 'd'), '21 days')

    def test_ordinals(self):
        expected = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 11: '11th', 12: '12th', 13: '13th', 21: '21st',
                    22: '22nd', 23: '23rd', 100: '100th', 101: '101st', 111: '111th', 112: '112th'}
        for n, text in expected.items():
            self.assertEqual(en.birthday_ordinal(n), text)

    def test_join(self):
        self.assertEqual(en.join_words(['1 week', '3 days']), '1 week and 3 days')
        self.assertEqual(en.join_words(['1 month', '1 week', '3 days']), '1 month, 1 week and 3 days')
        self.assertEqual(en.join_words(['3 days']), '3 days')

    def test_dates(self):
        self.assertEqual(en.format_date(date(2026, 4, 30)), '30 April 2026')
        self.assertEqual(en.format_short_date(date(2026, 9, 3)), '3 Sep 2026')
        self.assertEqual(en.format_timestamp(datetime(2026, 1, 2, 3, 4)), '02 Jan, 03:04')

    def test_phrases(self):
        self.assertEqual(en.format_percent(0.639), '63.9%')
        self.assertEqual(en.next_birthday(3), '3rd birthday')
        self.assertEqual(en.in_days(1), 'in 1 day')
        self.assertEqual(en.overdue(2), '2 days overdue')


class PolishTest(unittest.TestCase):
    def test_phrases(self):
        self.assertEqual(pl.format_percent(0.639), '63,9%')
        self.assertEqual(pl.next_birthday(3), '3. urodziny')
        self.assertEqual(pl.in_days(1), 'za 1 dzień')
        self.assertEqual(pl.overdue(2), '2 dni po terminie')
        self.assertEqual(pl.format_timestamp(datetime(2026, 1, 2, 3, 4)), '02.01, 03:04')

    def test_pregnancy_weeks(self):
        self.assertEqual(pl.unit_word(22, 'w'), 'tygodnie')
        self.assertEqual(pl.unit_word(25, 'w'), 'tygodni')


if __name__ == '__main__':
    unittest.main()
