"""Window setup and drawing the currently-viewed wall to the screen."""

import pygame

from config import (
    GRID_COLS,
    GRID_ROWS,
    MARGIN_COLS,
    CEIL_ROWS,
    INITIAL_SCALE,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    MIN_SCALE,
    TILE_SIZE,
    TOP_FACE_OVERHANG,
    WINDOW_TITLE,
)
from rendering.assets import BACKGROUND_SPRITES, load_image, ASSET_DIR


class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)


        self.window = pygame.display.set_mode(
            (LOGICAL_WIDTH * INITIAL_SCALE, LOGICAL_HEIGHT * INITIAL_SCALE),
            pygame.RESIZABLE,
        )
        self.logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        pygame.display.set_icon(pygame.image.load(ASSET_DIR /BACKGROUND_SPRITES["icon"]))


        self.wall_tile = load_image(BACKGROUND_SPRITES["wall_tile"])
        self.floor_tile = load_image(BACKGROUND_SPRITES["floor_tile"])

    def render(self, room_state):
        self._draw_background()
        self._draw_modules(room_state.current_wall)
        self._draw_interactables(room_state.current_wall.interactables)
        self._draw_interactables(room_state.room_interactables)
        self._blit_to_window()

    @staticmethod
    def _to_px(row, col):
        """Grid (row, column) -> logical pixel top-left, shifted by the
        room's top/left margin. Used for everything (background, modules,
        interactables) so margins apply uniformly."""
        return (col + MARGIN_COLS) * TILE_SIZE, (row + CEIL_ROWS) * TILE_SIZE

    @classmethod
    def _sprite_topleft(cls, sprite, row, col):
        """Grid position -> pixel top-left for blitting/hit-testing a given
        sprite: shifts up by TOP_FACE_OVERHANG when that sprite actually
        carries the top-face strip (see assets.Sprite.has_overhang), and not
        otherwise. Every sprite draw/hit-test goes through this so the two
        can never drift apart."""
        x, y = cls._to_px(row, col)
        if sprite.has_overhang:
            y -= TOP_FACE_OVERHANG
        return x, y

    def _blit_sprite(self, sprite, row, col):
        self.logical_surface.blit(sprite.surface, self._sprite_topleft(sprite, row, col))

    def _draw_background(self):
        # Overdraw one tile into the margins on every side (they're only
        # half a tile wide, so a full tile there simply bleeds harmlessly
        # into the grid or past the window edge, both of which get clipped
        # or redrawn over anyway).
        for row in range(-1, GRID_ROWS):
            for col in range(-1, GRID_COLS + 1):
                self._blit_sprite(self.wall_tile, row, col)
        for col in range(-1, GRID_COLS + 1):
            self._blit_sprite(self.floor_tile, GRID_ROWS-6/32, col)

    def _draw_modules(self, wall):
        # Painted from the bottom row upward (highest row index first) so
        # each module's sprite draws on top of the 6px top-face overhang
        # bleeding up from whatever sits in the row below it.
        for module in sorted(wall.modules, key=lambda m: m.anchor[0], reverse=True):
            anchor_row, anchor_col = module.anchor
            for sprite, offset in zip(module.sprites, module.sprite_offsets):
                self._blit_sprite(sprite, anchor_row + offset[0], anchor_col + offset[1])

    def _draw_interactables(self, interactables):
        for interactable in interactables:
            if not interactable.visible or interactable.sprite is None:
                continue
            self._blit_sprite(interactable.sprite, *interactable.anchor)

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
            surface = interactable.sprite.surface
            rect = surface.get_rect(topleft=self._sprite_topleft(interactable.sprite, *interactable.anchor))
            if rect.collidepoint(logical_pos):
                local_pos = (int(logical_pos[0] - rect.x), int(logical_pos[1] - rect.y))
                if surface.get_at(local_pos).a > 0:
                    return interactable
        return None
