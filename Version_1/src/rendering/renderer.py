"""Window setup and drawing the currently-viewed wall to the screen."""

import pygame

from config import (
    GRID_COLS,
    GRID_ROWS,
    INITIAL_SCALE,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    MIN_SCALE,
    TILE_SIZE,
    TOP_FACE_OVERHANG,
    WINDOW_TITLE,
)
from rendering.assets import BACKGROUND_SPRITES, load_image


class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.window = pygame.display.set_mode(
            (LOGICAL_WIDTH * INITIAL_SCALE, LOGICAL_HEIGHT * INITIAL_SCALE),
            pygame.RESIZABLE,
        )
        self.logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

        self.wall_tile = load_image(BACKGROUND_SPRITES["wall_tile"])
        self.floor_tile = load_image(BACKGROUND_SPRITES["floor_tile"])

    def render(self, room_state):
        self._draw_background()
        self._draw_modules(room_state.current_wall)
        self._draw_interactables(room_state.current_wall.interactables)
        self._draw_interactables(room_state.room_interactables)
        self._blit_to_window()

    def _draw_background(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                self.logical_surface.blit(self.wall_tile, (col * TILE_SIZE, row * TILE_SIZE))
        floor_y = GRID_ROWS * TILE_SIZE-TOP_FACE_OVERHANG
        for col in range(GRID_COLS):
            self.logical_surface.blit(self.floor_tile, (col * TILE_SIZE, floor_y))

    def _draw_modules(self, wall):
        # Painted from the bottom row upward (highest row index first) so
        # each module's sprite draws on top of the 6px top-face overhang
        # bleeding up from whatever sits in the row below it.
        for module in sorted(wall.modules, key=lambda m: m.anchor[0], reverse=True):
            x = module.anchor[1] * TILE_SIZE
            y = module.anchor[0] * TILE_SIZE - TOP_FACE_OVERHANG
            for sprite, offset in zip(module.sprites, module.sprite_offsets):
                self.logical_surface.blit(
                    sprite, (x + offset[1] * TILE_SIZE, y + offset[0] * TILE_SIZE)
                )

    def _draw_interactables(self, interactables):
        for interactable in interactables:
            if not interactable.visible or interactable.sprite is None:
                continue
            row, col = interactable.anchor
            self.logical_surface.blit(interactable.sprite, (col * TILE_SIZE, row * TILE_SIZE))

    def _fit_rect(self):
        window_w, window_h = self.window.get_size()
        scale = min(window_w / LOGICAL_WIDTH, window_h / LOGICAL_HEIGHT)
        scale = max(scale, MIN_SCALE)
        draw_w = max(1, int(LOGICAL_WIDTH * scale))
        draw_h = max(1, int(LOGICAL_HEIGHT * scale))
        offset_x = (window_w - draw_w) // 2
        offset_y = (window_h - draw_h) // 2
        return offset_x, offset_y, draw_w, draw_h, scale

    def _blit_to_window(self):
        offset_x, offset_y, draw_w, draw_h, _ = self._fit_rect()
        self.window.fill((0, 0, 0))
        # Nearest-neighbor only -- smoothscale would blur the pixel art.
        scaled = pygame.transform.scale(self.logical_surface, (draw_w, draw_h))
        self.window.blit(scaled, (offset_x, offset_y))
        pygame.display.flip()

    def handle_resize(self, size):
        self.window = pygame.display.set_mode(size, pygame.RESIZABLE)

    def screen_to_logical(self, pos):
        offset_x, offset_y, draw_w, draw_h, scale = self._fit_rect()
        x, y = pos
        logical_x = (x - offset_x) / scale
        logical_y = (y - offset_y) / scale
        if 0 <= logical_x < LOGICAL_WIDTH and 0 <= logical_y < LOGICAL_HEIGHT:
            return logical_x, logical_y
        return None

    def find_interactable_at(self, logical_pos, room_state):
        """Only currently-rendered interactables are clickable, and only
        their non-transparent pixels count as a hit."""
        if logical_pos is None:
            return None

        candidates = list(room_state.room_interactables) + list(
            room_state.current_wall.interactables
        )
        for interactable in candidates:
            if not interactable.visible or interactable.sprite is None:
                continue
            row, col = interactable.anchor
            rect = interactable.sprite.get_rect(
                topleft=(col * TILE_SIZE, row * TILE_SIZE)
            )
            if rect.collidepoint(logical_pos):
                local_pos = (int(logical_pos[0] - rect.x), int(logical_pos[1] - rect.y))
                if interactable.sprite.get_at(local_pos).a > 0:
                    return interactable
        return None
