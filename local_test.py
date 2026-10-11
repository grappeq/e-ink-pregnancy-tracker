#!/usr/bin/python
# -*- coding:utf-8 -*-
"""Render the screen without the e-paper hardware.

    python3 local_test.py [birth_date] [today] [--name NAME] [--time HH:MM] [--out FILE.png]

Writes a PNG that approximates how the 4 gray levels look on the panel
(scaled up 3x). Without --out the image is opened in a viewer.
"""
import argparse
from datetime import date, datetime

from PIL import Image

from baby_tracker import ScreenUI, Age

# Approximate on-panel tones for the driver values 0x00, 0x80, 0xC0, 0xFF.
PANEL_TONES = {0x00: 0x2a, 0x80: 0x6e, 0xC0: 0xa8, 0xFF: 0xe4}

parser = argparse.ArgumentParser()
parser.add_argument('birth_date', nargs='?', default='2024-01-01')
parser.add_argument('today', nargs='?', default=None, help='YYYY-MM-DD, defaults to today')
parser.add_argument('--name')
parser.add_argument('--time', help='HH:MM shown as the refresh time, defaults to now')
parser.add_argument('--out')
args = parser.parse_args()

today = datetime.strptime(args.today, '%Y-%m-%d').date() if args.today else date.today()
time = datetime.strptime(args.time, '%H:%M').time() if args.time else datetime.now().time()
now = datetime.combine(today, time)

age = Age(args.birth_date, today=today)
image = ScreenUI(264, 176, age, name=args.name, now=now).draw()

preview = image.point(lambda v: PANEL_TONES.get(v, v)).resize((264 * 3, 176 * 3), Image.NEAREST)
if args.out:
    preview.save(args.out)
else:
    preview.show()
