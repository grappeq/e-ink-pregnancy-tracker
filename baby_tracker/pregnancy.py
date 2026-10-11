from datetime import date, datetime, timedelta


class Pregnancy:
    DURATION_DAYS = 280
    # Past this many days after the due date the baby has certainly been born:
    # a config that was never updated is treated as if the due date was the birth date.
    MAX_OVERDUE_DAYS = 21

    def __init__(self, due_date, today=None):
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        self.start_date = self.due_date - timedelta(days=self.DURATION_DAYS)
        self.today = today or date.today()

    def get_day(self):
        """Days since the start of the pregnancy (the due date is day 280)."""
        return (self.today - self.start_date).days

    def get_weeks(self):
        return self.get_day() // 7

    def get_weekdays(self):
        return self.get_day() % 7

    def get_parts(self):
        """(value, unit) pairs like Age.get_parts(): completed weeks and days."""
        return [(self.get_weeks(), 'w'), (self.get_weekdays(), 'd')]

    def get_progress(self):
        return min(max(self.get_day() / self.DURATION_DAYS, 0), 1)

    def get_days_until_due(self):
        """Negative once the due date has passed."""
        return (self.due_date - self.today).days

    def is_long_overdue(self):
        return -self.get_days_until_due() > self.MAX_OVERDUE_DAYS
