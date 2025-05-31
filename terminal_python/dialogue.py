import pygame
import sys

# --- Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Dialogue UI")
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# --- Load Font ---
# Uncomment and replace with your font path if desired
# FONT_PATH = "/home/pi/fonts/MyFont.ttf"
# font = pygame.font.Font(FONT_PATH, 24)

font = pygame.font.SysFont("monospace", 24)

# --- Dialogue Data ---
dialogue_text = "Welcome, traveler. What do you seek?"
user_input = ""
prompt = ">> "

# --- Main Loop ---
running = True
while running:
    screen.fill(BLACK)

    # --- Render Dialogue ---
    dialogue_surface = font.render(dialogue_text, True, WHITE)
    screen.blit(dialogue_surface, (50, 100))

    # --- Render Input ---
    input_surface = font.render(prompt + user_input, True, GRAY)
    screen.blit(input_surface, (50, 200))

    pygame.display.flip()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]

            elif event.key == pygame.K_RETURN:
                # Process input here
                print("User typed:", user_input)
                # Reset or update dialogue
                dialogue_text = f"You said: {user_input}"
                user_input = ""

            else:
                # Add typed character to user_input
                user_input += event.unicode

    clock.tick(FPS)

pygame.quit()
sys.exit()