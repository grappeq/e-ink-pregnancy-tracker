import math
import time
from datetime import datetime, timedelta

class Pregnancy:
    PREGNANCY_DURATION_DAYS = 280

    def __init__(self, birth_date):
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        self.pregnancy_start_date = self.birth_date - timedelta(days=self.PREGNANCY_DURATION_DAYS)

    def get_progress(self):
        total_pregnancy_secs = self.birth_date.timestamp() - self.pregnancy_start_date.timestamp()
        return min(self.get_pregnancy_secs()/total_pregnancy_secs, 1)

    def get_weekday_str(self):
        return f'{self.get_pregnancy_week()}w {self.get_pregnancy_weekday()}d'

    def get_percent_str(self):
        return "{:.1f}%".format(self.get_progress()*100)

    def get_pregnancy_day(self):
        return (datetime.now() - self.pregnancy_start_date).days

    def get_pregnancy_secs(self):
        return time.time() - self.pregnancy_start_date.timestamp()

    def get_pregnancy_week(self):
        return math.floor(self.get_pregnancy_day()/7)

    def get_pregnancy_weekday(self):
        return math.floor(self.get_pregnancy_day())%7
