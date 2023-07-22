#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from screen_ui import ScreenUI

logging.basicConfig(level=logging.DEBUG)

GRAY1  = 0xff #white
GRAY2  = 0xC0
GRAY3  = 0x80 #gray
GRAY4  = 0x00 #Blackest

try:
    screen_ui = ScreenUI(264, 176, grey_scale=(GRAY1,GRAY2, GRAY3, GRAY4))
    himage = screen_ui.draw()
    himage.show()


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()
