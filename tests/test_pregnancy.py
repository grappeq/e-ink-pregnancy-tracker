import unittest
from datetime import date, timedelta

from baby_tracker.config import ConfigError, create_models, screen_options
from baby_tracker.locales import en, pl
from baby_tracker.pregnancy import Pregnancy
from baby_tracker.screen_ui import select_state, PREGNANCY, COUNTDOWN, WELCOME, NORMAL

DUE = date(2027, 1, 20)
START = DUE - timedelta(days=280)


def pregnancy_on(day):
    return Pregnancy(DUE.isoformat(), today=START + timedelta(days=day))


class PregnancyTest(unittest.TestCase):
    def test_start_date(self):
        self.assertEqual(pregnancy_on(0).start_date, date(2026, 4, 15))

    def test_weeks_and_days(self):
        p = pregnancy_on(179)
        self.assertEqual((p.get_day(), p.get_weeks(), p.get_weekdays()), (179, 25, 4))
        self.assertEqual(p.get_parts(), [(25, 'w'), (4, 'd')])

    def test_whole_weeks(self):
        self.assertEqual(pregnancy_on(168).get_parts(), [(24, 'w'), (0, 'd')])

    def test_progress(self):
        self.assertEqual(pregnancy_on(0).get_progress(), 0)
        self.assertAlmostEqual(pregnancy_on(140).get_progress(), 0.5)
        self.assertEqual(pregnancy_on(280).get_progress(), 1)

    def test_progress_is_clamped(self):
        self.assertEqual(pregnancy_on(-10).get_progress(), 0)
        self.assertEqual(pregnancy_on(290).get_progress(), 1)

    def test_days_until_due(self):
        self.assertEqual(pregnancy_on(179).get_days_until_due(), 101)
        self.assertEqual(pregnancy_on(280).get_days_until_due(), 0)
        self.assertEqual(pregnancy_on(283).get_days_until_due(), -3)

    def test_long_overdue(self):
        self.assertFalse(pregnancy_on(280 + Pregnancy.MAX_OVERDUE_DAYS).is_long_overdue())
        self.assertTrue(pregnancy_on(281 + Pregnancy.MAX_OVERDUE_DAYS).is_long_overdue())

    def test_whole_days_regardless_of_time_of_day(self):
        # The old model used datetime.now(); days must not depend on the hour.
        self.assertEqual(Pregnancy('2027-01-20', today=date(2027, 1, 19)).get_days_until_due(), 1)


class SelectStateTest(unittest.TestCase):
    def state(self, config, today):
        return select_state(*create_models(config, today=today))

    def test_pregnancy_window(self):
        config = {'expected_birth_date': DUE.isoformat()}
        self.assertEqual(self.state(config, START), COUNTDOWN)
        self.assertEqual(self.state(config, START + timedelta(days=1)), PREGNANCY)
        self.assertEqual(self.state(config, DUE - timedelta(days=1)), PREGNANCY)

    def test_due_date_without_birth_stays_pregnant(self):
        config = {'expected_birth_date': DUE.isoformat()}
        self.assertEqual(self.state(config, DUE), PREGNANCY)
        self.assertEqual(self.state(config, DUE + timedelta(days=Pregnancy.MAX_OVERDUE_DAYS)), PREGNANCY)

    def test_stale_config_falls_back_to_age(self):
        config = {'expected_birth_date': DUE.isoformat()}
        self.assertEqual(self.state(config, DUE + timedelta(days=200)), NORMAL)

    def test_birth_date_switches_to_age(self):
        config = {'expected_birth_date': DUE.isoformat(), 'birth_date': '2027-01-14'}
        self.assertEqual(self.state(config, date(2027, 1, 13)), PREGNANCY)
        self.assertEqual(self.state(config, date(2027, 1, 14)), WELCOME)
        self.assertEqual(self.state(config, date(2027, 1, 15)), NORMAL)

    def test_birth_date_alone_is_the_due_date(self):
        # Configs of e-ink-baby-age-tracker only have birth_date.
        config = {'birth_date': DUE.isoformat()}
        self.assertEqual(self.state(config, START + timedelta(days=100)), PREGNANCY)
        self.assertEqual(self.state(config, DUE), WELCOME)


class ConfigTest(unittest.TestCase):
    TODAY = date(2026, 10, 11)

    def test_old_pregnancy_config(self):
        age, pregnancy = create_models({'expected_birth_date': '2027-01-20'}, today=self.TODAY)
        self.assertIsNone(age)
        self.assertEqual(pregnancy.due_date, DUE)

    def test_both_dates(self):
        age, pregnancy = create_models({'expected_birth_date': '2027-01-20', 'birth_date': '2027-01-14'},
                                       today=self.TODAY)
        self.assertEqual(age.birth_date, date(2027, 1, 14))
        self.assertEqual(pregnancy.due_date, DUE)

    def test_null_birth_date_is_ignored(self):
        age, _ = create_models({'expected_birth_date': '2027-01-20', 'birth_date': None}, today=self.TODAY)
        self.assertIsNone(age)

    def test_missing_dates(self):
        with self.assertRaises(ConfigError):
            create_models({}, today=self.TODAY)

    def test_bad_date(self):
        with self.assertRaises(ConfigError):
            create_models({'expected_birth_date': '20.01.2027'}, today=self.TODAY)

    def test_language(self):
        self.assertIs(screen_options({})['locale'], en)
        self.assertIs(screen_options({'language': 'pl'})['locale'], pl)
        self.assertIs(screen_options({'language': ' PL '})['locale'], pl)
        with self.assertLogs(level='WARNING'):
            self.assertIs(screen_options({'language': 'de'})['locale'], en)

    def test_name(self):
        self.assertEqual(screen_options({'name': 'Zosia'})['name'], 'Zosia')
        self.assertIsNone(screen_options({})['name'])


if __name__ == '__main__':
    unittest.main()
