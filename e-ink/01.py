#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import time
import random
import math
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import textwrap
import json
import traceback
import threading


animation_lock = threading.Lock()
current_animation = None
stop_animation = threading.Event()

# Setup paths
basedir = os.path.dirname(os.path.realpath(__file__))
assetdir = os.path.join(basedir, 'assets')
libdir = os.path.join(basedir, 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.WARNING)

font_path = os.path.join(assetdir, 'PPMondwest-Regular.otf')
data_path = "./data/user_messages.json"

# Display and decay animation function
def display_message(epd, text):
    duration = 60  # seconds
    frame_interval = 0.25  # seconds
    num_frames = int(duration / frame_interval)
    width, height = epd.width, epd.height

    font = ImageFont.truetype(font_path, 66)
    base_image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(base_image)

    wrapped_text = textwrap.fill(text, width=30)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=6)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.multiline_text((x, y), wrapped_text, font=font, fill=0, spacing=6, align='center')

    original_pixels = base_image.load()

    for frame in range(num_frames):
        if stop_animation.is_set():
            print("Animation interrupted.")
            return

        decay_ratio = frame / num_frames
        simulated_voltage = math.exp(-3 * decay_ratio)
        keep_prob = simulated_voltage

        frame_image = Image.new('1', (width, height), 255)
        frame_pixels = frame_image.load()

        for x in range(width):
            for y in range(height):
                if original_pixels[x, y] == 0:
                    if random.random() < keep_prob:
                        frame_pixels[x, y] = 0
                    else:
                        frame_pixels[x, y] = 255

        epd.display_Partial(epd.getbuffer(frame_image), 0, 0, epd.width, epd.height)
        time.sleep(frame_interval)

# Load messages and get most recent
def get_latest_message():
    try:
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
                return max(messages, key=lambda x: datetime.strptime(x['timestamp'], "%d-%m-%Y %H:%M:%S"))
    except Exception as e:
        logging.warning("Failed to read or parse message JSON.")
        logging.warning(traceback.format_exc())
    return None

# --- MAIN LOOP ---
try:
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()
    epd.init_part()

    last_displayed_message = None
    current_animation = None
    stop_animation = threading.Event()

    def run_animation(message_to_display):
        with animation_lock:
            display_message(epd, message_to_display['message'])

    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Polling...", flush=True)

        latest = get_latest_message()
        if latest and last_displayed_message != latest:
            print(f"New message from {latest['name']} at {latest['timestamp']}", flush=True)

            # Interrupt current animation
            if current_animation and current_animation.is_alive():
                print("Interrupting current animation...", flush=True)
                stop_animation.set()
                current_animation.join()
                stop_animation.clear()

            # Full refresh for new message
            epd.init()
            epd.Clear()
            epd.init_part()

            current_animation = threading.Thread(target=run_animation, args=(latest,))
            current_animation.start()
            last_displayed_message = latest

        time.sleep(5)

except KeyboardInterrupt:
    print("Exiting...")
    epd.sleep()

except Exception as e:
    logging.error("Unhandled exception:")
    logging.error(traceback.format_exc())
    epd.sleep()
