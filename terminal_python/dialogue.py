import pygame
import json
import sys
import os
import platform
import time

# Loading JSON
with open("./data/updated_dialogue.json", "r", encoding="utf-8") as f:
    dialogue_data = json.load(f)

# Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30
INPUT_FILE = "/tmp/input.txt"

# check if running on Raspberry Pi
is_raspberry_pi = platform.system() == "Linux" and os.uname().machine.startswith("aarch64")
print(platform.system())
print(os.uname().machine)

if is_raspberry_pi:
    import RPi.GPIO as GPIO   
    # GPIO pin number (BCM numbering)
    SWITCH_PIN = 4
    print("Running on Raspberry Pi")

# Initialize pygame
pygame.init()

flags = pygame.FULLSCREEN if is_raspberry_pi else 0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
pygame.display.set_caption("Dialogue UI")
clock = pygame.time.Clock()

# Typing animation
string_index = 0
current_character = 0

# Typing time counter
last_char_time = time.time()

# State
showing_reply = False
reply_data = None
current_prompt = 0
current_character = 0
input_text = ""
selected_option = 0
show_cursor = True
last_cursor_switch = time.time()
cursor_interval = 0.5
user_name = ""
input_warning = False

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (0, 0, 255)
HIGHLIGHT = (200, 20, 200) # magenta
BACKGROUND = (255, 255, 255) # white
TEXT = (0, 0, 0) # black
INSTRUCTION = (0, 0, 255)

# Load font
FONT_PATH = "./assets/PPMondwest-Regular.otf"
INSTRUCTION_FONT_PATH = "./assets/PPNeueBit-Bold.otf"
font = pygame.font.Font(FONT_PATH, 40)
instruction_font = pygame.font.Font(FONT_PATH, 34)
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
            rendered = font.render(line, False, color)
            surface.blit(rendered, (x, y + y_offset))
            y_offset += font.get_height()
            line = word
        else:
            line = test_line
    rendered = font.render(line, False, color)
    surface.blit(rendered, (x, y + y_offset))
    return y + y_offset + font.get_height()

def show_popup(screen, font, message):
    popup_width, popup_height = 600, 300
    screen_width, screen_height = screen.get_size()
    popup_x = (screen_width - popup_width) // 2
    popup_y = (screen_height - popup_height) // 2

    # Draw popup background
    pygame.draw.rect(screen, (50, 50, 50), (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 2)  # Border

    # Render and draw text
    text_surface = instruction_font.render(message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text_surface, text_rect)


# user name
def substitute_vars(text):
    return text.replace("[name]", user_name)

def restart():
    global current_prompt, current_character, selected_option
    global input_text, user_name, input_warning
    global showing_reply, reply_data

    current_prompt = 0
    current_character = 0
    selected_option = 0
    input_text = ""
    user_name = ""
    input_warning = False
    showing_reply = False
    reply_data = None


# Main loop
running = True
while running:
    screen.fill(BACKGROUND)

    # reset logic
    if current_prompt >= len(dialogue_data["dialogue"]):
        restart()

    prompt = dialogue_data["dialogue"][current_prompt]
    prompt_text = substitute_vars(prompt["text"]) # substitute name if present
    prompt_type = prompt["type"]
    highlight = prompt.get("highlighted", "no") == "yes" # check if highlighted

    # Display prompt text with typing effect
    full_text = prompt_text + " ∇"
    display_text = full_text[:current_character] # show text up to current character
    text_color = HIGHLIGHT if highlight else TEXT
    instruction_color = INSTRUCTION
    y_offset = draw_text(screen, display_text, 30, 60, font, text_color, SCREEN_WIDTH - 60)  

    # access the prompt["pace"] and make a multiplier
    if prompt["pace"] == "slow":
        delay_normal = 0.1  
        delay_comma = 0.8       
        delay_period = 1.2 
        delay_space = 0.2
    else:
        delay_normal = 0.001  
        delay_comma = 0.3       
        delay_period = 0.6 
        delay_space = 0.05 

    now = time.time()
    if current_character < len(full_text):
        prev_char = full_text[current_character - 1] if current_character > 0 else ''
        # set delays so it loolks cute
        delay = delay_normal
        if prev_char in {'.', '?'}:
            delay = delay_period
        elif prev_char == ',':
            delay = delay_comma
        elif prev_char == ' ':
            delay = delay_space

        if now - last_char_time > delay:
            current_character += 1
            last_char_time = now
    else:
        if prompt_type == "multiple_choice":
            if showing_reply and reply_data:
                reply_text = substitute_vars(reply_data[0]["text"])
                display_reply = reply_text[:current_character]
                y_offset = draw_text(screen, display_reply, 30, y_offset + 20, instruction_font, TEXT, SCREEN_WIDTH - 60)
            else:
                y_offset += 20
                for i, option in enumerate(prompt["options"]):
                    option_text = option["label"]
                    color = HIGHLIGHT if i == selected_option else GRAY
                    draw_text(screen, f"> {option_text}", 30, y_offset, instruction_font, color, SCREEN_WIDTH - 60)
                    y_offset += instruction_font.get_height()
                color = INSTRUCTION
                helper_text = "Use the Arrows (↑↓) to select. Press Enter to confirm your answer."
                draw_text(screen, helper_text, 30, y_offset + 20, instruction_font, color, SCREEN_WIDTH - 60)

        elif prompt_type == "text_input":
            if input_text:
                input_display_text = input_text
                color = TEXT
            elif input_warning:
                input_display_text = "Type something to continue, then press Enter."
                color = INSTRUCTION
            else:
                input_display_text = "Type your answer here, then press Enter."
                color = INSTRUCTION

            cursor = "|" if show_cursor else ""
            draw_text(screen, f"> {input_display_text}{cursor}", 30, y_offset + 20, instruction_font, color, SCREEN_WIDTH - 60)

        # make this elif into if there's an instruction, display it
        elif prompt_type == "sentence" :
            instruction = prompt.get("instruction")
            if instruction:
                helper_text = instruction
                color = INSTRUCTION
                draw_text(screen, helper_text, 30, y_offset + 20, instruction_font, color, SCREEN_WIDTH - 60)



    # Cursor blink
    if now - last_cursor_switch > cursor_interval:
        show_cursor = not show_cursor
        last_cursor_switch = now

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # skip to end of text on ENTER
            if current_character < len(full_text):
                if event.key == pygame.K_RETURN:
                    current_character = len(full_text)  
                continue

            elif prompt_type == "sentence" or prompt_type == "restart":
                if event.key == pygame.K_RETURN:
                    if prompt_type == "restart":
                        restart()
                    else:
                        current_prompt += 1
                        current_character = 0

            # multiple choice handling
            elif prompt_type == "multiple_choice":
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(prompt["options"])
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(prompt["options"])
                elif event.key == pygame.K_RETURN:
                    # first check if reply is skip
                    if prompt["options"][selected_option]["reply"] == "[skip]":
                        # Skip to next prompt
                        current_prompt += 1
                        current_character = 0
                        selected_option = 0

                    # Otherwise, get the reply text
                    else:
                        reply_obj = prompt["options"][selected_option]["reply"][0]
                        reply_text = substitute_vars(reply_obj["text"])
                        reply_type = reply_obj.get("type", "sentence")

                        # Inject reply as a temporary prompt and delay moving forward
                        dialogue_data["dialogue"].insert(current_prompt + 1, {
                            "type": reply_type,
                            "text": reply_text,
                            "highlighted": str(reply_obj.get("highlighted", False)).lower(),
                            "pace": str(reply_obj.get("pace", "normal")).lower()
                        })

                        current_prompt += 1
                        current_character = 0
                        selected_option = 0
 
            # text input handling
            elif prompt_type == "text_input":
                if event.key == pygame.K_RETURN:
                        
                    if input_text.strip() == "":
                        input_warning = True  # Trigger the special placeholder
                    else:
                        input_type = prompt.get("input_type")
                        if input_type == "name":
                            user_name = input_text.strip()

                        elif input_type == "message":
                            user_message = input_text.strip()

                            #add character limit
                            new_message = {
                                "name": user_name,
                                "message": user_message,
                                "timestamp": time.strftime("%d-%m-%Y %H:%M:%S")
                            }

                            print(new_message)

                            new_message_path = "./data/user_messages.json"
                            temp_message_path = "./data/user_messages.json.tmp"

                            if os.path.exists(new_message_path):
                                with open(new_message_path, "r") as infile:
                                    try:
                                        messages = json.load(infile)
                                        if not isinstance(messages, list):
                                            messages = []
                                    except json.JSONDecodeError:
                                        messages = []
                            else:
                                messages = []
                            
                            # Append new message
                            messages.append(new_message)

                            # Check if mud has charged enough
                            if is_raspberry_pi:
                                GPIO.setmode(GPIO.BCM)       # Use BCM pin numbering
                                GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up
                                is_charged = False
                                # start fallback timer if mud doesn't charge in 3 minutes
                                fallback_timer = time.time() + 180  # 3 minutes from now
                                try:

                                    while not is_charged and time.time() < fallback_timer:
                                        # current_prompt += 1
                                        # current_character = 0
                                        input_state = GPIO.input(SWITCH_PIN)
                                        if input_state == GPIO.LOW:
                                            print("Mud is charged!")
                                            is_charged = True
                                            # popup goes away
                                        else:
                                            #popup message saying mud is not charged
                                            print("Mud is not charged yet, waiting...")
                                            show_popup(screen, font, "The mud is charging... It will wake up at 3.5V")
                                            pygame.display.flip()
                                            time.sleep(0.25)


                                except KeyboardInterrupt:
                                    print("\nExiting...")

                                finally:
                                    GPIO.cleanup()

                            # Write to temp file if mud is charged or if it has been more than 3 minutes since user submitted
                            with open(temp_message_path, "w") as tmpfile:
                                json.dump(messages, tmpfile, indent=4)
                                tmpfile.flush()
                                os.fsync(tmpfile.fileno())

                            os.replace(temp_message_path, new_message_path)

                        input_text = ""
                        current_prompt += 1
                        current_character = 0
                        input_warning = False  # Reset warning on valid input

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    char = event.unicode
                    if char.isprintable():
                        input_text += char
                        input_warning = False  # Clear warning when user types

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
