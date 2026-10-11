import json
from datetime import datetime

from .age import Age
from .locales import get_locale
from .pregnancy import Pregnancy


class ConfigError(ValueError):
    pass


def load_config(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def create_models(config, today=None):
    """(age, pregnancy) for the screen; age is None until a birth date is known.

    `expected_birth_date` is the due date, `birth_date` the actual one. Either is
    enough: a lone birth_date also serves as the due date, and a lone due date
    long past is taken as the birth date (for configs never updated after birth).
    """
    if not isinstance(config, dict):
        raise ConfigError('config.json must be a JSON object')
    birth_date = _date_setting(config, 'birth_date')
    due_date = _date_setting(config, 'expected_birth_date') or birth_date
    if not due_date:
        raise ConfigError('config.json needs "expected_birth_date" or "birth_date" (YYYY-MM-DD)')
    pregnancy = Pregnancy(due_date, today=today)
    if birth_date:
        age = Age(birth_date, today=today)
    elif pregnancy.is_long_overdue():
        age = Age(due_date, today=today)
    else:
        age = None
    return age, pregnancy


def _date_setting(config, key):
    """The key's date string, or None when unset. Errors name the key, never the value: they end up in the log."""
    value = config.get(key)
    if not value:
        return None
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except (ValueError, TypeError) as e:
        raise ConfigError(f'"{key}" in config.json must be a date as YYYY-MM-DD') from e
    return value


def screen_options(config):
    """Keyword arguments for create_screen besides the models."""
    return {'name': config.get('name'), 'locale': get_locale(config.get('language'))}
