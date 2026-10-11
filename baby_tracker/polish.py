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


def format_numeric_date(d):
    return f'{d.day:02d}.{d.month:02d}.{d.year}'
