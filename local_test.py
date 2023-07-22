#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import time

from pregnancy_tracker import ScreenUI, Pregnancy

logging.basicConfig(level=logging.DEBUG)

try:
    pregnancy = Pregnancy(time.time()+3600*24*100)
    screen_ui = ScreenUI(264, 176, pregnancy)
    himage = screen_ui.draw()
    himage.show()


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()
