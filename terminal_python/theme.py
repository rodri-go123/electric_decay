# Defines the Pygame color palette, color blending, and application fonts.
import pygame

from . import config

WHITE = pygame.Color("#ffffff")
BLACK = pygame.Color("#141414")
GRAY = pygame.Color("#636c00")
HIGHLIGHT = pygame.Color("#fff200")
BACKGROUND = pygame.Color("#192008")
TEXT = pygame.Color("#ebff00")
INSTRUCTION = pygame.Color("#99a700")


def blend_colors(start: pygame.Color, end: pygame.Color, amount: float) -> pygame.Color:
    amount = max(0.0, min(1.0, amount))
    return pygame.Color(
        round(start.r + (end.r - start.r) * amount),
        round(start.g + (end.g - start.g) * amount),
        round(start.b + (end.b - start.b) * amount),
    )


def load_fonts() -> tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
    return (
        pygame.font.Font(str(config.FONT_PATH), 40),
        pygame.font.Font(str(config.INSTRUCTION_FONT_PATH), 34),
        pygame.font.Font(str(config.FONT_PATH), 32),
    )
