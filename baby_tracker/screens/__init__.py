from .age import AgeScreen
from .birthday import BirthdayScreen
from .countdown import CountdownScreen
from .pregnancy import PregnancyScreen
from .base import NORMAL, COUNTDOWN, WELCOME, BIRTHDAY, PREGNANCY
from .welcome import WelcomeScreen


def select_state(age, pregnancy=None):
    if age is not None and age.is_born():
        if age.get_total_days() == 0:
            return WELCOME
        if age.is_birthday():
            return BIRTHDAY
        return NORMAL
    if pregnancy is not None and pregnancy.get_day() >= 1:
        return PREGNANCY
    return COUNTDOWN


SCREENS = {
    NORMAL: AgeScreen,
    COUNTDOWN: CountdownScreen,
    WELCOME: WelcomeScreen,
    BIRTHDAY: BirthdayScreen,
    PREGNANCY: PregnancyScreen,
}


def create_screen(width, height, age=None, pregnancy=None, name=None, now=None, locale=None):
    """The screen for today's state; draw() renders it."""
    return SCREENS[select_state(age, pregnancy)](width, height, age, pregnancy, name=name, now=now, locale=locale)
