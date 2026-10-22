# Runs the main Pygame dialogue application and coordinates its components.
import json
import sys
import time

import pygame

try:
    from . import config, hardware, inactivity, message_store, renderer, theme
except ImportError:
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from terminal_python import config, hardware, inactivity, message_store, renderer, theme


def main() -> None:
    with config.DIALOGUE_PATH.open("r", encoding="utf-8") as dialogue_file:
        dialogue_data = json.load(dialogue_file)

    charger = hardware.ChargingSwitch()
    pygame.init()
    if charger.is_raspberry_pi:
        pygame.mouse.set_visible(False)
    fonts = theme.load_fonts()
    screen = pygame.display.set_mode(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        pygame.FULLSCREEN if charger.is_raspberry_pi else 0,
    )
    pygame.display.set_caption("Dialogue UI")
    clock = pygame.time.Clock()
    idle = inactivity.InactivityController.create()

    current_prompt = 0
    current_character = 0
    input_text = ""
    selected_option = 0
    user_name = ""
    input_warning = False
    cursor_bob_offset = -1
    last_cursor_bob = time.time()
    last_character_time = time.time()
    last_gpio_state = None
    running = True

    try:
        while running:
            now = time.time()
            screen.fill(theme.BACKGROUND)
            idle_result = idle.update(current_prompt, now)
            if idle_result == "restart":
                current_prompt = 0
                current_character = 0
                selected_option = 0
                input_text = ""
                user_name = ""
                input_warning = False
                with config.DIALOGUE_PATH.open("r", encoding="utf-8") as dialogue_file:
                    dialogue_data = json.load(dialogue_file)

            last_gpio_state = charger.report_change(last_gpio_state)
            if current_prompt >= len(dialogue_data["dialogue"]):
                current_prompt = 0

            prompt = dialogue_data["dialogue"][current_prompt]
            prompt_text = prompt["text"].replace("[name]", user_name)
            full_text = prompt_text + " ∇"
            display_text = full_text[:current_character]
            text_color = theme.HIGHLIGHT if prompt.get("highlighted", False) else theme.TEXT
            completed = current_character >= len(full_text)
            y = renderer.draw_text(
                screen,
                prompt_text if completed else display_text,
                30,
                60,
                fonts[0],
                text_color,
                config.SCREEN_WIDTH - 60,
            )

            pace = prompt.get("pace", "normal")
            delay = 0.1 if pace == "slow" else 0.001
            if current_character < len(full_text):
                previous = full_text[current_character - 1] if current_character else ""
                delay = {" ": 0.2 if pace == "slow" else 0.05, ",": 0.8 if pace == "slow" else 0.3, ".": 1.2 if pace == "slow" else 0.6, "?": 1.2 if pace == "slow" else 0.6}.get(previous, delay)
                if now - last_character_time > delay:
                    current_character += 1
                    last_character_time = now
            elif now - last_cursor_bob > 0.45:
                cursor_bob_offset = 2 if cursor_bob_offset == -1 else -1
                last_cursor_bob = now

            if completed:
                renderer.draw_message_cursor(screen, prompt_text, 30, 60, fonts[0], text_color, config.SCREEN_WIDTH - 60, cursor_bob_offset, fonts[2])
                if prompt["type"] == "multiple_choice":
                    y += 20
                    for index, option in enumerate(prompt["options"]):
                        color = theme.HIGHLIGHT if index == selected_option else theme.GRAY
                        renderer.draw_text(screen, f"> {option['label']}", 30, y, fonts[1], color, config.SCREEN_WIDTH - 60)
                        y += fonts[1].get_height()
                    renderer.draw_text(screen, "Use the Arrows (↑↓) to select. Press Enter to confirm your answer.", 30, y + 20, fonts[1], theme.INSTRUCTION, config.SCREEN_WIDTH - 60)
                elif prompt["type"] == "text_input":
                    text = input_text or ("Type something to continue, then press Enter." if input_warning else "Type your answer here, then press Enter.")
                    color = theme.TEXT if input_text else theme.INSTRUCTION
                    renderer.draw_text(screen, f"> {text}", 30, y + 20, fonts[1], color, config.SCREEN_WIDTH - 60)
                elif prompt.get("instruction"):
                    renderer.draw_text(screen, prompt["instruction"], 30, y + 20, fonts[1], theme.INSTRUCTION, config.SCREEN_WIDTH - 60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if idle.confirmation_active:
                        if event.key == pygame.K_RETURN:
                            idle.confirm_presence(time.time())
                            current_character = len(full_text)
                        continue
                    idle.register_input(time.time())
                    if current_character < len(full_text):
                        if event.key == pygame.K_RETURN:
                            current_character = len(full_text)
                        continue
                    if prompt["type"] in {"sentence", "restart"} and event.key == pygame.K_RETURN:
                        if prompt["type"] == "restart":
                            current_prompt = 0
                        else:
                            current_prompt += 1
                        current_character = 0
                    elif prompt["type"] == "multiple_choice":
                        if event.key == pygame.K_UP:
                            selected_option = (selected_option - 1) % len(prompt["options"])
                        elif event.key == pygame.K_DOWN:
                            selected_option = (selected_option + 1) % len(prompt["options"])
                        elif event.key == pygame.K_RETURN:
                            reply = prompt["options"][selected_option]["reply"]
                            if reply == "[skip]":
                                current_prompt += 1
                            else:
                                reply_obj = reply[0]
                                dialogue_data["dialogue"].insert(current_prompt + 1, {"type": reply_obj.get("type", "sentence"), "text": reply_obj["text"].replace("[name]", user_name), "highlighted": reply_obj.get("highlighted", False), "pace": reply_obj.get("pace", "normal")})
                                current_prompt += 1
                            current_character = 0
                            selected_option = 0
                    elif prompt["type"] == "text_input":
                        if event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            if not input_text.strip():
                                input_warning = True
                            else:
                                input_type = prompt.get("input_type")
                                if input_type == "name":
                                    user_name = input_text.strip()
                                elif input_type == "message":
                                    message_store.append_message(config.MESSAGE_PATH, user_name, input_text.strip())
                                    if charger.is_raspberry_pi:
                                        deadline = time.time() + 180
                                        while not charger.is_charged() and time.time() < deadline:
                                            renderer.draw_charging_popup(screen, "The mud is charging... It will wake up at 3.5V", fonts[1])
                                            pygame.display.flip()
                                            time.sleep(0.25)
                                input_text = ""
                                input_warning = False
                                current_prompt += 1
                                current_character = 0
                        elif event.unicode.isprintable():
                            input_text += event.unicode
                            input_warning = False

            if idle.confirmation_active:
                renderer.draw_confirmation_screen(screen, idle.seconds_remaining(time.time()), idle.pulse_amount(time.time()), fonts)
            pygame.display.flip()
            clock.tick(config.FPS)
    finally:
        pygame.quit()
        if charger.is_raspberry_pi:
            pygame.mouse.set_visible(True)
        charger.cleanup()


if __name__ == "__main__":
    main()
