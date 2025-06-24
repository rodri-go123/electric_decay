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
# from waveshare_epd import epd7in5_V2
import time
import random
import math
# from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import traceback
import textwrap
import json

logging.basicConfig(level=logging.WARNING)

# Setup paths (adjust if needed)
font_path = os.path.join(assetdir, 'PPMondwest-Regular.otf')  # Use any .ttf or .ttc font available
data_path = "./data/user_messages.json"

if os.path.exists(data_path):
    with open(data_path, "r", encoding="utf-8") as f:
        message_data = json.load(f)
else:
    message_data = [{
        "name": "Rodrigo",
        "message": "What if the internet needs a nap, but we won't let it sleep?",
        "timestamp": "24-06-2025 10:30:00"
    }]

alt_data = [{
    "name": "Rodrigo",
    "message": "What if the internet needs a nap, but we won't let it sleep?",
    "timestamp": "24-06-2025 10:30:00"
}]

# Convert timestamp strings to datetime objects and find the latest
most_recent = max(message_data, key=lambda x: datetime.strptime(x['timestamp'], "%d-%m-%Y %H:%M:%S"))

# Print the most recent message
print("Most recent message:")
print(f"From: {most_recent['name']}")
print(f"Message: {most_recent['message']}")
print(f"Timestamp: {most_recent['timestamp']}")
print("stopping")

# Initialize e-ink
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()
epd.init_part()

# Parameters
text = "Please delete this message, but this time it is a very very long one."
duration = 5  # seconds
frame_interval = .25  # seconds per frame
num_frames = duration // frame_interval
width, height = epd.width, epd.height

# Font setup
font = ImageFont.truetype(font_path, 56)

# Create initial image
base_image = Image.new('1', (width, height), 255)
draw = ImageDraw.Draw(base_image)

# Wrap the text
wrapped_text = textwrap.fill(text, width=30)  # Wrap text to approx. 30 characters per line

# Calculate text size using the new Pillow method
bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=6)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text on the display
x = (width - text_width) // 2
y = (height - text_height) // 2

# Draw the text
draw.multiline_text((x, y), wrapped_text, font=font, fill=0, spacing=6, align='center')

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
# final_image = Image.new('1', (width, height), 255)
# epd.display(epd.getbuffer(final_image))
