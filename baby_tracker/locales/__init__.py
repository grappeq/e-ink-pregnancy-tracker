"""Screen copy per language. Each module exposes the same functions and constants."""
import logging

from . import en, pl

LOCALES = {'en': en, 'pl': pl}
DEFAULT = 'en'


def get_locale(code=None):
    if code is None:
        return LOCALES[DEFAULT]
    locale = LOCALES.get(str(code).strip().lower())
    if locale is None:
        logging.warning('Unknown language %r, falling back to %r', code, DEFAULT)
        return LOCALES[DEFAULT]
    return locale
