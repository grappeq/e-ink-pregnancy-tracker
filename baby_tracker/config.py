import json

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
    birth_date = config.get('birth_date')
    due_date = config.get('expected_birth_date') or birth_date
    if not due_date:
        raise ConfigError('config.json needs "expected_birth_date" or "birth_date" (YYYY-MM-DD)')
    try:
        pregnancy = Pregnancy(due_date, today=today)
        if birth_date:
            age = Age(birth_date, today=today)
        elif pregnancy.is_long_overdue():
            age = Age(due_date, today=today)
        else:
            age = None
    except ValueError as e:
        raise ConfigError(f'Dates in config.json must be YYYY-MM-DD: {e}') from e
    return age, pregnancy


def screen_options(config):
    """Keyword arguments for ScreenUI besides the models."""
    return {'name': config.get('name'), 'locale': get_locale(config.get('language'))}
