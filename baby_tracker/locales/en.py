UNIT_FORMS = {
    'y': ('year', 'years'),
    'm': ('month', 'months'),
    'w': ('week', 'weeks'),
    'd': ('day', 'days'),
}

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]

BORN_PREFIX = 'born '
REMAINDER_PREFIX = 'plus '
COUNTDOWN_PREFIX = ''
COUNTDOWN_NOTE = 'until birth'
WELCOME = 'Welcome to the world!'
FIRST_DAY = 'day one'
BIRTHDAY_WORD = 'birthday'
BIRTHDAY_WISH = 'Hip hip hooray!'
DUE_TODAY = 'due today'


def unit_word(n, unit):
    one, many = UNIT_FORMS[unit]
    return one if n == 1 else many


def format_quantity(n, unit):
    return f'{n} {unit_word(n, unit)}'


def join_words(items):
    if len(items) <= 1:
        return ''.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def format_date(d):
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


def format_short_date(d):
    return f'{d.day} {MONTHS[d.month - 1][:3]} {d.year}'


def format_timestamp(dt):
    # Spelled out rather than strftime('%b'), which follows the system locale.
    return f'{dt.day:02d} {MONTHS[dt.month - 1][:3]}, {dt:%H:%M}'


def format_percent(fraction):
    return f'{fraction * 100:.1f}%'


def birthday_ordinal(n):
    if n % 100 in (11, 12, 13):
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f'{n}{suffix}'


def next_birthday(n):
    return f'{birthday_ordinal(n)} {BIRTHDAY_WORD}'


def in_days(n):
    return f'in {format_quantity(n, "d")}'


def overdue(n):
    return f'{format_quantity(n, "d")} overdue'
