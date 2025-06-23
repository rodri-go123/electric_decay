import pygame
import random
import sys
from pygame.locals import *

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
TITLE = "Decaying Data"
ANIMATION_DURATION = 40  # seconds
FPS = 60
LETTER_INTERVAL = 0.4  # delay between each letter appearing
LOADING_START_DELAY = 3  # seconds after last letter
STAR_COUNT = 100
STAR_SPEED = 0.5

# --- INITIALIZE ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Replace with your own font later
FONT_PATH = "./assets/PPMondwest-Regular.otf"
font = pygame.font.Font(FONT_PATH, 100)
small_font = pygame.font.Font(FONT_PATH, 40)

# --- STARFIELD SETUP ---
class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(STAR_SPEED, STAR_SPEED * 2)
        self.size = random.choice([1, 1, 2])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()
            self.y = 0

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), (self.x, int(self.y), self.size, self.size))

stars = [Star() for _ in range(STAR_COUNT)]

# --- LETTER ANIMATION CLASS ---
class AnimatedLetter:
    def __init__(self, char, target_x, target_y, appear_time):
        self.char = char
        self.target_x = target_x
        self.target_y = target_y
        self.appear_time = appear_time
        self.active = False
        self.scale = 0.1
        self.y_offset = -100
        self.opacity = 0
        self.duration = 0.4  # time for a letter to fully "arrive"

    def update(self, current_time, surface):
        if current_time >= self.appear_time:
            self.active = True
            progress = min((current_time - self.appear_time) / self.duration, 1.0)
            self.scale = 0.1 + 0.9 * progress  # from 0.1 to 1.0
            self.y_offset = -100 * (1 - progress)
            self.opacity = int(255 * progress)

            # Render letter
            letter_surface = font.render(self.char, True, (255, 255, 255))
            letter_surface = pygame.transform.rotozoom(letter_surface, 0, self.scale)

            # Set alpha
            letter_surface.set_alpha(self.opacity)
            rect = letter_surface.get_rect(center=(self.target_x, self.target_y + self.y_offset))
            surface.blit(letter_surface, rect)

# --- SETUP LETTER POSITIONS ---
letters = []
total_text_width = sum([font.size(c)[0] for c in TITLE])
start_x = WIDTH // 2 - total_text_width // 2
x = start_x
current_time = 0
for i, char in enumerate(TITLE):
    char_width = font.size(char)[0]
    appear_time = i * LETTER_INTERVAL
    letter = AnimatedLetter(char, x + char_width // 2, HEIGHT // 2 - 40, appear_time)
    letters.append(letter)
    x += char_width

# --- MAIN LOOP ---
start_time = pygame.time.get_ticks() / 1000
loading_started = False
loading_dots = 0
loading_dot_timer = 0
running = True

while running:
    current_time = pygame.time.get_ticks() / 1000 - start_time
    elapsed = current_time

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Animate stars
    for star in stars:
        star.update()
        star.draw(screen)

    # Animate title
    for letter in letters:
        letter.update(current_time, screen)

    # Start loading text after last letter
    if elapsed > (LETTER_INTERVAL * len(TITLE)) + LOADING_START_DELAY:
        if not loading_started:
            loading_started = True
            loading_dot_timer = current_time

        if current_time - loading_dot_timer > 0.5:
            loading_dots = (loading_dots + 1) % 4
            loading_dot_timer = current_time

        loading_text = "LOADING" + ("." * loading_dots)
        loading_surface = small_font.render(loading_text, True, (255, 255, 255))
        loading_rect = loading_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        screen.blit(loading_surface, loading_rect)

    pygame.display.flip()
    clock.tick(FPS)

    if elapsed > ANIMATION_DURATION:
        running = False

pygame.quit()
sys.exit()
