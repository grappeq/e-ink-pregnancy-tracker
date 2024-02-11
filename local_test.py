#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from datetime import datetime, timedelta

from pregnancy_tracker import ScreenUI, Pregnancy

logging.basicConfig(level=logging.DEBUG)

try:
    birth_time = datetime.now() + timedelta(days=100)
    pregnancy = Pregnancy(birth_time.strftime("%Y-%m-%d"))
    screen_ui = ScreenUI(264, 176, pregnancy)
    himage = screen_ui.draw()
    himage.show()


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()
