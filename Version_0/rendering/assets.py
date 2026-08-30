import pygame
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"


def load_image(path, size=None):
    image = pygame.image.load(ASSET_DIR / path).convert_alpha()

    if size is not None:
        image = pygame.transform.smoothscale(image, size)

    return image