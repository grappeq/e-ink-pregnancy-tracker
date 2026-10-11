import unittest
from datetime import date

from baby_tracker.age import Age
from baby_tracker.polish import format_quantity, join_words, format_date, format_numeric_date


class AgeTest(unittest.TestCase):
    def test_breakdown(self):
        age = Age('2024-01-01', today=date(2026, 10, 11))
        self.assertEqual(age.get_parts(), [(2, 'y'), (9, 'm'), (1, 'w'), (3, 'd')])
        self.assertEqual(age.get_age_strings(), ['2l', '9m', '1t', '3d'])

    def test_born_on_31st_counts_short_months(self):
        # rrule-based counting skipped months without a 31st day.
        age = Age('2026-01-31', today=date(2026, 3, 1))
        self.assertEqual((age.get_months(), age.get_weeks(), age.get_days()), (1, 0, 1))

    def test_birth_day(self):
        age = Age('2026-10-11', today=date(2026, 10, 11))
        self.assertEqual([v for v, _ in age.get_parts()], [0, 0, 0, 0])
        self.assertEqual(age.get_days_to_next_birthday(), 365)
        self.assertEqual(age.get_progress_to_next_birthday(), 0)

    def test_next_birthday(self):
        age = Age('2024-01-01', today=date(2026, 10, 11))
        self.assertEqual(age.get_next_birthday_number(), 3)
        self.assertEqual(age.get_days_to_next_birthday(), 82)
        self.assertAlmostEqual(age.get_progress_to_next_birthday(), 283 / 365)

    def test_leap_day_birthday(self):
        age = Age('2024-02-29', today=date(2025, 2, 28))
        self.assertEqual(age.get_years(), 1)


class BirthTest(unittest.TestCase):
    TODAY = date(2026, 10, 11)

    def age(self, birth_date, today=TODAY):
        return Age(birth_date, today=today)

    def test_future_birth(self):
        age = self.age('2026-10-25')
        self.assertFalse(age.is_born())
        self.assertEqual(age.get_days_until_birth(), 14)

    def test_born_tomorrow(self):
        age = self.age('2026-10-12')
        self.assertFalse(age.is_born())
        self.assertEqual(age.get_days_until_birth(), 1)

    def test_born_today(self):
        age = self.age('2026-10-11')
        self.assertTrue(age.is_born())
        self.assertEqual(age.get_days_until_birth(), 0)

    def test_born_in_the_past_never_negative(self):
        for birth in ('2026-10-10', '2024-01-01', '1990-05-05'):
            age = self.age(birth)
            self.assertTrue(age.is_born(), birth)
            self.assertEqual(age.get_days_until_birth(), 0, birth)

    def test_days_until_birth_across_year_boundary(self):
        age = self.age('2027-01-05', today=date(2026, 12, 28))
        self.assertFalse(age.is_born())
        self.assertEqual(age.get_days_until_birth(), 8)

    def test_days_until_birth_across_leap_february(self):
        age = self.age('2028-03-01', today=date(2028, 2, 1))
        self.assertEqual(age.get_days_until_birth(), 29)



class BirthdayTest(unittest.TestCase):
    def is_birthday(self, birth_date, today):
        return Age(birth_date, today=today).is_birthday()

    def test_birth_day_is_not_a_birthday(self):
        self.assertFalse(self.is_birthday('2026-10-11', date(2026, 10, 11)))

    def test_yearly_birthdays(self):
        for years in (1, 2, 5, 10, 100):
            self.assertTrue(self.is_birthday(f'{2026 - years}-10-11', date(2026, 10, 11)), years)

    def test_near_misses(self):
        today = date(2026, 10, 11)
        self.assertFalse(self.is_birthday('2025-10-10', today))  # 1y 0m 0w 1d
        self.assertFalse(self.is_birthday('2025-10-12', today))  # day before 1st birthday
        self.assertFalse(self.is_birthday('2026-09-11', today))  # month-iversary
        self.assertFalse(self.is_birthday('2025-09-11', today))  # 1y 1m
        self.assertFalse(self.is_birthday('2025-10-04', today))  # 1y 1w
        self.assertFalse(self.is_birthday('2026-10-25', today))  # not born yet

    def test_leap_day_birth(self):
        self.assertTrue(self.is_birthday('2024-02-29', date(2025, 2, 28)))
        self.assertFalse(self.is_birthday('2024-02-29', date(2025, 3, 1)))
        self.assertTrue(self.is_birthday('2024-02-29', date(2028, 2, 29)))
        self.assertFalse(self.is_birthday('2024-02-29', date(2028, 2, 28)))

    def test_feb_28_birth_in_leap_year(self):
        self.assertTrue(self.is_birthday('2023-02-28', date(2024, 2, 28)))
        self.assertFalse(self.is_birthday('2023-02-28', date(2024, 2, 29)))

    def test_born_on_31st(self):
        self.assertTrue(self.is_birthday('2025-01-31', date(2026, 1, 31)))
        self.assertFalse(self.is_birthday('2025-01-31', date(2026, 2, 28)))

class PolishTest(unittest.TestCase):
    def test_plurals(self):
        self.assertEqual(format_quantity(1, 'y'), '1 rok')
        self.assertEqual(format_quantity(2, 'y'), '2 lata')
        self.assertEqual(format_quantity(5, 'y'), '5 lat')
        self.assertEqual(format_quantity(12, 'y'), '12 lat')
        self.assertEqual(format_quantity(22, 'm'), '22 miesiące')
        self.assertEqual(format_quantity(1, 'w'), '1 tydzień')
        self.assertEqual(format_quantity(3, 'w'), '3 tygodnie')
        self.assertEqual(format_quantity(1, 'd'), '1 dzień')
        self.assertEqual(format_quantity(4, 'd'), '4 dni')

    def test_join(self):
        self.assertEqual(join_words(['1 tydzień', '3 dni']), '1 tydzień i 3 dni')
        self.assertEqual(join_words(['3 dni']), '3 dni')

    def test_format_date(self):
        self.assertEqual(format_date(date(2026, 4, 30)), '30 kwietnia 2026')
        self.assertEqual(format_date(date(2026, 10, 25)), '25 października 2026')

    def test_format_numeric_date_zero_pads(self):
        self.assertEqual(format_numeric_date(date(2026, 4, 3)), '03.04.2026')
        self.assertEqual(format_numeric_date(date(2026, 12, 31)), '31.12.2026')
        self.assertEqual(format_numeric_date(date(2026, 1, 1)), '01.01.2026')


if __name__ == '__main__':
    unittest.main()
