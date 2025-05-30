#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
assetdir = os.path.join(basedir, 'assets')
libdir = os.path.join(basedir, 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
import random
import math
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.WARNING)

# Setup paths (adjust if needed)
font_path = os.path.join(assetdir, 'Font.ttc')  # Use any .ttf or .ttc font available

# Initialize e-ink
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()
epd.init_part()

# Parameters
text = "Please delete this message"
duration = 5  # seconds
frame_interval = .25  # seconds per frame
num_frames = duration // frame_interval
width, height = epd.width, epd.height

# Font setup
font = ImageFont.truetype(font_path, 36)

# Create initial image
base_image = Image.new('1', (width, height), 255)
draw = ImageDraw.Draw(base_image)
text_width, text_height = draw.textsize(text, font=font)
draw.text(((width - text_width) // 2, (height - text_height) // 2), text, font=font, fill=0)
original_pixels = base_image.load()

# Simulate decay and display over time
for frame in range(int(num_frames)):
    decay_ratio = frame / num_frames  # 0.0 to 1.0
    simulated_voltage = math.exp(-3 * decay_ratio)  # Exponential decay: V(t) = e^(-kt)
    keep_prob = simulated_voltage  # 1.0 (no decay) → 0.0 (fully disintegrated)

    # Copy original and apply decay
    frame_image = Image.new('1', (width, height), 255)
    frame_pixels = frame_image.load()

    for x in range(width):
        for y in range(height):
            if original_pixels[x, y] == 0:
                if random.random() < keep_prob:
                    frame_pixels[x, y] = 0  # keep pixel
                else:
                    frame_pixels[x, y] = 255  # erase pixel

    epd.display_Partial(epd.getbuffer(frame_image), 0, 0, epd.width, epd.height)
    time.sleep(frame_interval)

# Optional: clear or show final empty state
final_image = Image.new('1', (width, height), 255)
epd.display(epd.getbuffer(final_image))
