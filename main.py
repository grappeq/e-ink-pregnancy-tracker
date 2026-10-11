#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Draws today's screen on the e-paper panel. Run from cron; exits 0 on success, 1 on any failure.

Each run appends one record to baby-tracker.log next to this file (size-capped, rotated);
failures also go to stderr.
"""
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

HERE = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(HERE, 'config.json')
LOG_PATH = os.path.join(HERE, 'baby-tracker.log')
LOG_MAX_BYTES = 256 * 1024
LOG_BACKUPS = 1

log = logging.getLogger('baby_tracker.run')


def _setup_logging(path):
    log.setLevel(logging.INFO)
    log.propagate = False
    for handler in list(log.handlers):
        log.removeHandler(handler)
        handler.close()
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(logging.ERROR)
    stderr.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log.addHandler(stderr)
    try:
        file_handler = RotatingFileHandler(path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUPS, encoding='utf-8')
    except OSError as e:
        # The display matters more than the log: keep going.
        print(f'WARNING: cannot write {path}: {e}', file=sys.stderr)
        return
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    log.addHandler(file_handler)


def _close_logging():
    for handler in list(log.handlers):
        log.removeHandler(handler)
        handler.close()


def _open_display():
    import epaper
    return epaper.epaper('epd2in7').EPD()


def _show(epd, image, pause):
    """Sends the image to the panel; the panel is put to sleep whatever happens once it is initialised."""
    # A failing Init_4Gray leaves nothing powered to put to sleep, and the process exits right after.
    if epd.Init_4Gray() == -1:
        raise RuntimeError('cannot initialise the e-paper panel (GPIO/SPI)')
    try:
        epd.display_4Gray(epd.getbuffer_4Gray(image))
        pause(2)
    except BaseException as error:
        try:
            epd.sleep()
        except Exception as sleep_error:
            if not isinstance(error, Exception):
                # Ctrl-C or SystemExit must still stop the run as such.
                log.error('putting the panel to sleep failed: %r', sleep_error)
                raise error
            # One record per run: the display error travels along as the cause.
            raise RuntimeError(f'putting the panel to sleep failed too: {sleep_error!r}') from error
        raise
    epd.sleep()


def main(config_path=CONFIG_PATH, log_path=LOG_PATH, open_display=_open_display, pause=time.sleep):
    _setup_logging(log_path)
    try:
        # Imported here so a missing dependency is logged like any other failure.
        from baby_tracker import create_screen
        from baby_tracker.config import load_config, create_models, screen_options
        try:
            config = load_config(config_path)
            age, pregnancy = create_models(config)
            options = screen_options(config)
        except (OSError, ValueError) as e:
            log.error('Cannot read %s: %s', config_path, e)
            return 1
        epd = open_display()
        # Drawn before Init_4Gray powers the panel, so a drawing bug never leaves it powered.
        screen = create_screen(epd.height, epd.width, age, pregnancy, **options)
        image = screen.draw()
        _show(epd, image, pause)
        log.info('OK state=%s', screen.STATE)
        return 0
    except ImportError as e:
        log.error('%s. After updating, reinstall the dependencies: pip3 install -r requirements.txt', e,
                  exc_info=True)
        return 1
    except Exception:
        log.exception('FAILED')
        return 1
    finally:
        _close_logging()


if __name__ == '__main__':
    sys.exit(main())
