"""main.main() with a fake e-paper driver: exit codes, panel sleep, and the run log."""
import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

import main

NAME = 'Zosia'
# More than 40 weeks ahead, so the state is the same whatever day the suite runs.
CONFIG = {'expected_birth_date': '2100-01-01', 'name': NAME, 'language': 'pl'}


class FakeEPD:
    """Records driver calls in order; `fail` maps a method name to the exception it raises."""
    width = 176
    height = 264

    def __init__(self, fail=None, init_result=0):
        self.fail = fail or {}
        self.init_result = init_result
        self.calls = []
        self.image = None

    def _call(self, name):
        self.calls.append(name)
        if name in self.fail:
            raise self.fail[name]

    def Init_4Gray(self):
        self._call('Init_4Gray')
        return self.init_result

    def getbuffer_4Gray(self, image):
        self._call('getbuffer_4Gray')
        self.image = image
        return b'buffer'

    def display_4Gray(self, buffer):
        self._call('display_4Gray')

    def sleep(self):
        self._call('sleep')


class MainTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.config_path = os.path.join(self.dir, 'config.json')
        self.log_path = os.path.join(self.dir, 'baby-tracker.log')
        self.write_config(CONFIG)
        self.opened = 0

    def write_config(self, config):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(config if isinstance(config, str) else json.dumps(config))

    def run_main(self, epd=None, open_display=None):
        self.epd = epd if epd is not None else FakeEPD()

        def default_open():
            self.opened += 1
            return self.epd

        stderr = io.StringIO()
        # main binds sys.stderr when it sets up logging, so redirect around the whole call.
        with contextlib.redirect_stderr(stderr):
            code = main.main(self.config_path, self.log_path, open_display or default_open, lambda s: None)
        self.stderr = stderr.getvalue()
        return code

    def log_text(self):
        with open(self.log_path, encoding='utf-8') as f:
            return f.read()

    def log_lines(self):
        return self.log_text().splitlines()

    def assert_no_name_logged(self):
        self.assertNotIn(NAME, self.log_text())
        self.assertNotIn(NAME, self.stderr)

    # Success.

    def test_success(self):
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.epd.calls, ['Init_4Gray', 'getbuffer_4Gray', 'display_4Gray', 'sleep'])
        # main passes (epd.height, epd.width): the panel is used in landscape.
        self.assertEqual(self.epd.image.size, (264, 176))
        lines = self.log_lines()
        self.assertEqual(len(lines), 1, lines)
        self.assertIn('OK state=countdown', lines[0])
        self.assertEqual(self.stderr, '')
        self.assert_no_name_logged()
        self.assertEqual(main.log.handlers, [])

    # Failures after the config is read.

    def test_render_failure(self):
        with mock.patch('baby_tracker.create_screen', side_effect=RuntimeError('render boom')):
            self.assertEqual(self.run_main(), 1)
        # main() imports create_screen when it runs, so patching the package attribute reaches it.
        self.assertEqual(self.epd.calls, [])
        log = self.log_text()
        self.assertIn('FAILED', log)
        self.assertIn('Traceback', log)
        self.assertIn('render boom', log)
        self.assertIn('render boom', self.stderr)

    def test_display_failure_still_sleeps(self):
        self.assertEqual(self.run_main(FakeEPD(fail={'display_4Gray': OSError('spi boom')})), 1)
        self.assertEqual(self.epd.calls, ['Init_4Gray', 'getbuffer_4Gray', 'display_4Gray', 'sleep'])
        self.assertEqual(self.epd.calls.count('sleep'), 1)
        log = self.log_text()
        self.assertIn('spi boom', log)
        self.assertIn('Traceback', log)
        self.assertNotIn('OK state=', log)
        self.assertIn('spi boom', self.stderr)
        self.assert_no_name_logged()

    def test_getbuffer_failure_still_sleeps(self):
        self.assertEqual(self.run_main(FakeEPD(fail={'getbuffer_4Gray': ValueError('buffer boom')})), 1)
        self.assertEqual(self.epd.calls, ['Init_4Gray', 'getbuffer_4Gray', 'sleep'])
        self.assertIn('buffer boom', self.log_text())

    def test_interrupt_during_display_still_sleeps(self):
        epd = FakeEPD(fail={'display_4Gray': KeyboardInterrupt()})
        with self.assertRaises(KeyboardInterrupt):
            self.run_main(epd)
        self.assertEqual(epd.calls.count('sleep'), 1)
        self.assertEqual(main.log.handlers, [])

    def test_interrupt_survives_a_failing_sleep(self):
        epd = FakeEPD(fail={'display_4Gray': KeyboardInterrupt(), 'sleep': OSError('sleep boom')})
        with self.assertRaises(KeyboardInterrupt):
            self.run_main(epd)
        self.assertEqual(epd.calls.count('sleep'), 1)
        self.assertIn('sleep boom', self.log_text())
        self.assertEqual(main.log.handlers, [])

    def test_init_raises(self):
        self.assertEqual(self.run_main(FakeEPD(fail={'Init_4Gray': OSError('gpio boom')})), 1)
        self.assertEqual(self.epd.calls, ['Init_4Gray'])
        self.assertIn('gpio boom', self.log_text())

    def test_init_returns_minus_one(self):
        self.assertEqual(self.run_main(FakeEPD(init_result=-1)), 1)
        self.assertEqual(self.epd.calls, ['Init_4Gray'])
        self.assertIn('cannot initialise', self.log_text())
        self.assertIn('cannot initialise', self.stderr)

    def test_sleep_failure_on_success_path(self):
        self.assertEqual(self.run_main(FakeEPD(fail={'sleep': OSError('sleep boom')})), 1)
        self.assertEqual(self.epd.calls, ['Init_4Gray', 'getbuffer_4Gray', 'display_4Gray', 'sleep'])
        log = self.log_text()
        self.assertIn('sleep boom', log)
        self.assertNotIn('OK state=', log)

    def test_sleep_failure_after_display_error_keeps_the_original_error(self):
        epd = FakeEPD(fail={'display_4Gray': OSError('spi boom'), 'sleep': OSError('sleep boom')})
        self.assertEqual(self.run_main(epd), 1)
        self.assertEqual(epd.calls.count('sleep'), 1)
        log = self.log_text()
        self.assertIn('spi boom', log)
        self.assertIn('sleep boom', log)
        # One record for the run, carrying the display error as the cause.
        self.assertEqual(len(re.findall(r'^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d ', log, re.M)), 1, log)
        failed = log[log.index('FAILED'):]
        self.assertIn('spi boom', failed)
        self.assertIn('direct cause', failed)

    # Config failures: reported before the display is touched.

    def assert_config_failure(self, *expected):
        self.assertEqual(self.run_main(), 1)
        self.assertEqual(self.opened, 0)
        self.assertIn('ERROR', self.stderr)
        for text in expected:
            self.assertIn(text, self.stderr)
        self.assertNotIn('Traceback', self.stderr)
        self.assertEqual(len(self.log_lines()), 1, self.log_lines())

    def test_config_missing(self):
        os.remove(self.config_path)
        self.assert_config_failure('Cannot read', self.config_path)

    def test_config_invalid_json(self):
        self.write_config('{"birth_date": ')
        self.assert_config_failure('Cannot read')

    def test_config_without_dates(self):
        self.write_config({'name': NAME})
        self.assert_config_failure('Cannot read', 'expected_birth_date')
        self.assert_no_name_logged()

    def test_config_bad_date(self):
        self.write_config({'birth_date': '11.10.2026', 'name': NAME})
        self.assert_config_failure('Cannot read', '"birth_date"', 'YYYY-MM-DD')
        self.assert_no_name_logged()
        self.assertNotIn('11.10.2026', self.log_text())
        self.assertNotIn('11.10.2026', self.stderr)

    def test_config_not_an_object(self):
        self.write_config('["2026-10-11"]')
        self.assert_config_failure('Cannot read', 'JSON object')

    # Imports.

    def test_missing_driver_hints_at_pip(self):
        def open_display():
            raise ModuleNotFoundError("No module named 'epaper'")
        self.assertEqual(self.run_main(open_display=open_display), 1)
        self.assertIn('pip3 install', self.log_text())
        self.assertIn("No module named 'epaper'", self.log_text())
        self.assertIn('pip3 install', self.stderr)

    # The log itself.

    def test_two_runs_two_records(self):
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.run_main(), 0)
        lines = self.log_lines()
        self.assertEqual(len(lines), 2, lines)
        self.assertTrue(all('OK state=' in line for line in lines), lines)
        self.assertEqual(main.log.handlers, [])

    def test_two_failed_runs_report_once_each(self):
        self.write_config({'name': NAME})
        for _ in range(2):
            self.assertEqual(self.run_main(), 1)
            self.assertEqual(self.stderr.count('ERROR'), 1, self.stderr)
        self.assertEqual(len(self.log_lines()), 2, self.log_lines())

    def test_log_is_rotated(self):
        runs = 6
        with mock.patch.object(main, 'LOG_MAX_BYTES', 100):
            for _ in range(runs):
                self.assertEqual(self.run_main(), 0)
        logs = [f for f in os.listdir(self.dir) if f.startswith('baby-tracker.log')]
        self.assertGreater(len(logs), 1, logs)
        self.assertLessEqual(len(logs), main.LOG_BACKUPS + 1, logs)
        records = 0
        for f in logs:
            with open(os.path.join(self.dir, f), encoding='utf-8') as fh:
                records += sum('OK state=' in line for line in fh)
        self.assertLess(records, runs)
        self.assertIn('OK state=', self.log_text())

    def test_unwritable_log_still_draws(self):
        self.log_path = self.dir  # A directory cannot be opened as the log file.
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.epd.calls, ['Init_4Gray', 'getbuffer_4Gray', 'display_4Gray', 'sleep'])
        self.assertIn('cannot write', self.stderr)
        self.assertEqual(main.log.handlers, [])


if __name__ == '__main__':
    unittest.main()
