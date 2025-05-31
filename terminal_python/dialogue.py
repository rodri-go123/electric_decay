import pygame
import json
import sys
import os
import platform
import time

# Loading JSON
with open("terminal_python/sentences.json", "r", encoding="utf-8") as f:
    sentences = json.load(f)

# Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30
INPUT_FILE = "/tmp/input.txt"

# check if running on Raspberry Pi
is_raspberry_pi = platform.system() == "Linux" and os.uname().machine.startswith("arm")

# Initialize pygame
pygame.init()

flags = pygame.FULLSCREEN if is_raspberry_pi else 0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
pygame.display.set_caption("Dialogue UI")
clock = pygame.time.Clock()

# Typing animation
string_index = 0
current_character = 0

# Typing speed
last_char_time = time.time()
delay_normal = 0.001  
delay_comma = 0.3       
delay_period = 0.6 
delay_space = 0.05     

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

# Load font
FONT_PATH = "./assets/PPMondwest-Regular.otf"
font = pygame.font.Font(FONT_PATH, 34)
# font = pygame.font.SysFont("monospace", 24)

# Wrap lines to fit screen

def draw_text(surface, text, x, y, font, color, max_width):
    words = text.split(' ')
    line = ""
    y_offset = 0
    for word in words:
        test_line = f"{line} {word}".strip()
        test_width, _ = font.size(test_line)
        if test_width > max_width:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y + y_offset))
            y_offset += font.get_height()
            line = word
        else:
            line = test_line
    rendered = font.render(line, True, color)
    surface.blit(rendered, (x, y + y_offset))

# Main loop
running = True
while running:
    screen.fill(BLACK)

    if string_index < len(sentences):
        full_text = sentences[string_index] + " ∇"
        display_text = full_text[:current_character]
        draw_text(screen, display_text, 30, 60, font, WHITE, SCREEN_WIDTH - 60)

        if current_character < len(full_text):
            now = time.time()
            # Determine delay depending on previous character typed
            prev_char = full_text[current_character - 1] if current_character > 0 else ''
            
            if prev_char in {'.', '?', '...'}:
                delay = delay_period
            elif prev_char == ',':
                delay = delay_comma
            elif prev_char == ' ':
                delay = delay_space
            else:
                delay = delay_normal

            if now - last_char_time > delay:
                current_character += 1
                last_char_time = now
    else:
        draw_text(screen, "End of narrative.", 30, 60, font, WHITE, SCREEN_WIDTH - 60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                string_index += 1
                current_character = 0

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
