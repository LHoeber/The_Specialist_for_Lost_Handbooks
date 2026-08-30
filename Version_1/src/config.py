"""Shared constants for the Version_1 prototype."""

TILE_SIZE = 32

# Sprites use a slight top-down perspective: every module sprite has an
# extra strip above its own top row showing the module's top face. This is
# what makes a 1-cell-tall module's sprite 38px tall (32 front + 6 top),
# not 32px.
TOP_FACE_OVERHANG = 6

# A wall is a 3-row by 4-column grid of module cells, plus a half-cell
# floor strip below it that isn't part of the module grid.
GRID_COLS = 4
GRID_ROWS = 3
FLOOR_ROWS = 0.5
NUM_WALLS = 4

LOGICAL_WIDTH = GRID_COLS * TILE_SIZE
LOGICAL_HEIGHT = int((GRID_ROWS + FLOOR_ROWS) * TILE_SIZE)

INITIAL_SCALE = 4
MIN_SCALE = 0.01

FPS = 60

WINDOW_TITLE = "The Specialist for Lost Handbooks"
