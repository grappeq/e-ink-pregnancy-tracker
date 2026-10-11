#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Render the screen without the e-paper hardware.

    python3 local_test.py [date] [today] [--born DATE] [--name NAME] [--lang en|pl]
                          [--time HH:MM] [--out FILE.png]

`date` is the expected birth date (a past one is treated like config.json does),
--born sets the actual birth date. Writes a PNG that approximates how the 4 gray
levels look on the panel (scaled up 3x). Without --out the image is opened in a viewer.
"""
import argparse
from datetime import date, datetime

from PIL import Image

from baby_tracker import ScreenUI
from baby_tracker.config import create_models, screen_options

# Approximate on-panel tones for the driver values 0x00, 0x80, 0xC0, 0xFF.
PANEL_TONES = {0x00: 0x2a, 0x80: 0x6e, 0xC0: 0xa8, 0xFF: 0xe4}

parser = argparse.ArgumentParser()
parser.add_argument('expected_birth_date', nargs='?', default='2027-01-20')
parser.add_argument('today', nargs='?', default=None, help='YYYY-MM-DD, defaults to today')
parser.add_argument('--born', help='actual birth date, YYYY-MM-DD')
parser.add_argument('--name')
parser.add_argument('--lang', default='en')
parser.add_argument('--time', help='HH:MM shown as the refresh time, defaults to now')
parser.add_argument('--out')
args = parser.parse_args()

today = datetime.strptime(args.today, '%Y-%m-%d').date() if args.today else date.today()
time = datetime.strptime(args.time, '%H:%M').time() if args.time else datetime.now().time()
now = datetime.combine(today, time)

config = {'expected_birth_date': args.expected_birth_date, 'birth_date': args.born,
          'name': args.name, 'language': args.lang}
age, pregnancy = create_models(config, today=today)
image = ScreenUI(264, 176, age, pregnancy, now=now, **screen_options(config)).draw()

preview = image.point(lambda v: PANEL_TONES.get(v, v)).resize((264 * 3, 176 * 3), Image.NEAREST)
if args.out:
    preview.save(args.out)
else:
    preview.show()
