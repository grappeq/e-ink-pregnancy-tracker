#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import logging
import epaper
from pregnancy_tracker import ScreenUI, Pregnancy

logging.basicConfig(level=logging.DEBUG)

config = json.load(open('config.json'))

try:
    epd = epaper.epaper('epd2in7').EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)
    epd.Init_4Gray()

    pregnancy = Pregnancy(config['expected_birth_timestamp'])

    screen_ui = ScreenUI(epd.height, epd.width, pregnancy)
    himage = screen_ui.draw()
    epd.display_4Gray(epd.getbuffer_4Gray(himage))
    time.sleep(2)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

