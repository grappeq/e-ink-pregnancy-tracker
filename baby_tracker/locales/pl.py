UNIT_FORMS = {
    'y': ('rok', 'lata', 'lat'),
    'm': ('miesiąc', 'miesiące', 'miesięcy'),
    'w': ('tydzień', 'tygodnie', 'tygodni'),
    'd': ('dzień', 'dni', 'dni'),
}

MONTHS_GENITIVE = [
    'stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
    'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia',
]

BORN_PREFIX = 'ur. '
REMAINDER_PREFIX = 'oraz '
COUNTDOWN_PREFIX = 'za'
COUNTDOWN_NOTE = 'do narodzin'
WELCOME = 'Witaj na świecie!'
FIRST_DAY = 'pierwszy dzień'
BIRTHDAY_WORD = 'urodziny'
BIRTHDAY_WISH = 'Sto lat!'
DUE_TODAY = 'termin dziś'


def plural(n, forms):
    one, few, many = forms
    if n == 1:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many


def unit_word(n, unit):
    return plural(n, UNIT_FORMS[unit])


def format_quantity(n, unit):
    return f'{n} {unit_word(n, unit)}'


def join_words(items):
    if len(items) <= 1:
        return ''.join(items)
    return ', '.join(items[:-1]) + ' i ' + items[-1]


def format_date(d):
    return f'{d.day} {MONTHS_GENITIVE[d.month - 1]} {d.year}'


def format_short_date(d):
    return f'{d.day:02d}.{d.month:02d}.{d.year}'


def format_timestamp(dt):
    return dt.strftime('%d.%m, %H:%M')


def format_percent(fraction):
    return f'{fraction * 100:.1f}%'.replace('.', ',')


def birthday_ordinal(n):
    return f'{n}.'


def next_birthday(n):
    return f'{birthday_ordinal(n)} {BIRTHDAY_WORD}'


def in_days(n):
    return f'za {format_quantity(n, "d")}'


def overdue(n):
    return f'{format_quantity(n, "d")} po terminie'
