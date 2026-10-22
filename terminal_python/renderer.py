# Draws dialogue text, cursors, charging popups, and confirmation screens.
import pygame

from . import config, theme


def draw_text(surface, text, x, y, font, color, max_width):
    words = text.split(" ")
    line = ""
    y_offset = 0
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] > max_width:
            surface.blit(font.render(line, False, color), (x, y + y_offset))
            y_offset += font.get_height()
            line = word
        else:
            line = test_line
    surface.blit(font.render(line, False, color), (x, y + y_offset))
    return y + y_offset + font.get_height()


def get_text_end_position(text, x, y, font, max_width):
    words = text.split(" ")
    line = ""
    y_offset = 0
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] > max_width:
            y_offset += font.get_height()
            line = word
        else:
            line = test_line
    return x + font.size(line)[0], y + y_offset


def draw_message_cursor(surface, text, x, y, font, color, max_width, offset, cursor_font):
    end_x, end_y = get_text_end_position(text, x, y, font, max_width)
    space_width = font.size(" ")[0]
    surface.blit(cursor_font.render("∇", False, color), (end_x + space_width, end_y + offset))


def draw_charging_popup(screen, message, instruction_font):
    popup_width, popup_height = 600, 300
    popup_x = (screen.get_width() - popup_width) // 2
    popup_y = (screen.get_height() - popup_height) // 2
    pygame.draw.rect(screen, theme.BACKGROUND, (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(screen, theme.INSTRUCTION, (popup_x, popup_y, popup_width, popup_height), 2)
    text_surface = instruction_font.render(message, True, theme.TEXT)
    screen.blit(text_surface, text_surface.get_rect(center=screen.get_rect().center))


def draw_confirmation_screen(screen, seconds_remaining, pulse_amount, fonts):
    font, instruction_font, _ = fonts
    background = theme.blend_colors(theme.BACKGROUND, theme.TEXT, pulse_amount)
    text = theme.blend_colors(theme.TEXT, theme.BACKGROUND, pulse_amount)
    highlight = theme.blend_colors(theme.HIGHLIGHT, theme.BACKGROUND, pulse_amount)
    screen.fill(background)
    y = draw_text(screen, "Are you still here?", 30, 60, font, text, config.SCREEN_WIDTH - 60)
    y = draw_text(screen, f"Restarting in {seconds_remaining} seconds.", 30, y + 10, font, text, config.SCREEN_WIDTH - 60)
    draw_text(screen, "> Yes [press Enter]", 30, y + 25, instruction_font, highlight, config.SCREEN_WIDTH - 60)
