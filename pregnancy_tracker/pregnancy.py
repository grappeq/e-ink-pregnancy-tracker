import math
import time


class Pregnancy:
    PREGNANCY_DURATION_DAYS = 280

    def __init__(self, birth_timestamp):
        self.birth_timestamp = birth_timestamp
        self.pregnancy_start_timestamp = self.birth_timestamp - self.PREGNANCY_DURATION_DAYS*3600*24

    def get_progress(self):
        return min(self.get_pregnancy_day_f()/self.PREGNANCY_DURATION_DAYS, 1)

    def get_weekday_str(self):
        return f'{self.get_pregnancy_week()}w {self.get_pregnancy_weekday()}d'

    def get_percent_str(self):
        return f'{round(self.get_progress()*100,1)}%'

    def get_pregnancy_day_f(self):
        return (time.time() - self.pregnancy_start_timestamp)/3600/24

    def get_pregnancy_week(self):
        return math.floor(self.get_pregnancy_day_f()/7)

    def get_pregnancy_weekday(self):
        return math.floor(self.get_pregnancy_day_f())%7
