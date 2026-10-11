from datetime import date, datetime

from dateutil.relativedelta import relativedelta


class Age:
    def __init__(self, birth_date, today=None):
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        self.today = today or date.today()
        self._calculate()

    def _calculate(self):
        # relativedelta clamps to the end of shorter months (e.g. born on the 31st),
        # which rrule-based counting silently skipped.
        delta = relativedelta(self.today, self.birth_date)
        self._years = delta.years
        self._months = delta.months
        self._weeks = delta.days // 7
        self._days = delta.days % 7

    def get_years(self):
        return self._years

    def get_months(self):
        return self._months

    def get_weeks(self):
        return self._weeks

    def get_days(self):
        return self._days

    def get_total_days(self):
        return (self.today - self.birth_date).days

    def is_born(self):
        return self.today >= self.birth_date

    def is_birthday(self):
        """True on every birthday from the first one on (Feb 29 births: Feb 28 in common years)."""
        return self._years >= 1 and not (self._months or self._weeks or self._days)

    def get_days_until_birth(self):
        """Days left until a birth date that is still in the future, else 0."""
        return max(0, (self.birth_date - self.today).days)

    def get_parts(self):
        """(value, unit) pairs, largest unit first. Units: 'y', 'm', 'w', 'd'.

        Like the birthday getters below, only meaningful once is_born().
        """
        return [
            (self._years, 'y'),
            (self._months, 'm'),
            (self._weeks, 'w'),
            (self._days, 'd'),
        ]

    def _birthday(self, years):
        return self.birth_date + relativedelta(years=years)

    def get_next_birthday_number(self):
        return self._years + 1

    def get_days_to_next_birthday(self):
        return (self._birthday(self._years + 1) - self.today).days

    def get_progress_to_next_birthday(self):
        last = self._birthday(self._years)
        nxt = self._birthday(self._years + 1)
        return (self.today - last).days / (nxt - last).days

    def get_age_strings(self):
        short_units = {'y': 'l', 'm': 'm', 'w': 't', 'd': 'd'}
        return [f'{value}{short_units[unit]}' for value, unit in self.get_parts() if value]
