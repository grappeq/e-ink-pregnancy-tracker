#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import time
import logging

logging.basicConfig(level=logging.WARN)

try:
    import epaper
    from baby_tracker import ScreenUI
    from baby_tracker.config import load_config, create_models, screen_options
except ImportError as e:
    logging.error('%s. After updating, reinstall the dependencies: pip3 install -r requirements.txt', e)
    sys.exit(1)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
try:
    config = load_config(config_file_path)
    age, pregnancy = create_models(config)
except (OSError, ValueError) as e:
    logging.error('Cannot read %s: %s', config_file_path, e)
    sys.exit(1)

try:
    epd = epaper.epaper('epd2in7').EPD()
    epd.Init_4Gray()

    screen_ui = ScreenUI(epd.height, epd.width, age, pregnancy, **screen_options(config))
    himage = screen_ui.draw()
    epd.display_4Gray(epd.getbuffer_4Gray(himage))
    time.sleep(2)

    epd.sleep()

except IOError as e:
    logging.error(e)
