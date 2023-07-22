#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
import time
import logging
import epaper
from pregnancy_tracker import ScreenUI, Pregnancy

logging.basicConfig(level=logging.DEBUG)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

try:
    epd = epaper.epaper('epd2in7').EPD()
    epd.Init_4Gray()

    pregnancy = Pregnancy(config['expected_birth_timestamp'])

    screen_ui = ScreenUI(epd.height, epd.width, pregnancy)
    himage = screen_ui.draw()
    epd.display_4Gray(epd.getbuffer_4Gray(himage))
    time.sleep(2)

    epd.sleep()

except IOError as e:
    logging.info(e)

