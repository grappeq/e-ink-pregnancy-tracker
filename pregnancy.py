import math
import time


class Pregnancy:
    PREGNANCY_DURATION_DAYS = 280

    def __init__(self, birth_timestamp):
        self.birth_timestamp = birth_timestamp
        self.pregnancy_start_timestamp = self.birth_timestamp - self.PREGNANCY_DURATION_DAYS*3600*24
        self.update()

    def update(self):
        current_timestamp = time.time()
        self.current_pregnancy_day = (current_timestamp - self.pregnancy_start_timestamp)/3600/24
        self.current_pregnancy_week = math.floor(self.current_pregnancy_day/7)
        self.current_pregnancy_weekday = math.floor(self.current_pregnancy_day)%7
        remaining_time = self.birth_timestamp - current_timestamp
        remaining_days = remaining_time/3600/24
        self.remaining_weeks = remaining_days/7
        self.progress = self.current_pregnancy_day/self.PREGNANCY_DURATION_DAYS

    def get_progress_bar(self):
        num_of_chars_used = 4
        num_of_chars_spacing = 16 - num_of_chars_used
        num_of_chars_progress = round(num_of_chars_spacing*self.progress)
        progress_bar_full = " "*num_of_chars_progress;
        progress_bar_empty = " "*(num_of_chars_spacing-num_of_chars_progress);
        print(f"|{progress_bar_full}Oo{progress_bar_empty}O")
        return f"|{progress_bar_full}Oo{progress_bar_empty}O"

    def get_weekday_str(self):
        return f'{self.current_pregnancy_week}w {self.current_pregnancy_weekday}d'

    def get_percent_str(self):
        return f'{round(self.progress*100,1)}%'
