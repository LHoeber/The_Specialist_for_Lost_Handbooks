/**
 * Shared constants for the web port. Direct port of Version_1/src/config.py --
 * see that file for the reasoning behind each constant. FPS is intentionally
 * dropped here: the web version renders on demand (on load, then after each
 * click), not on a fixed-tick loop -- see main.js.
 */
window.Game = window.Game || {};

Game.Config = (function () {
  const TILE_SIZE = 32;

  // Sprites use a slight top-down perspective: every module sprite has an
  // extra strip above its own top row showing the module's top face. This is
  // what makes a 1-cell-tall module's sprite 38px tall (32 front + 6 top),
  // not 32px.
  const TOP_FACE_OVERHANG = 6;

  // A wall is a 3-row by 4-column grid of module cells, plus a half-cell
  // floor strip below it that isn't part of the module grid.
  const GRID_COLS = 4;
  const GRID_ROWS = 3;
  const FLOOR_ROWS = 0.5;
  const CEIL_ROWS = 0.5;
  const MARGIN_COLS = 0.5;
  const NUM_WALLS = 4;

  // Margins sit on both sides of the grid, not just one.
  const LOGICAL_WIDTH = Math.round((GRID_COLS + 2 * MARGIN_COLS) * TILE_SIZE);
  const LOGICAL_HEIGHT = Math.round((CEIL_ROWS + GRID_ROWS + FLOOR_ROWS) * TILE_SIZE);

  const INITIAL_SCALE = 3;
  const MIN_SCALE = 0.01;

  const WINDOW_TITLE = "The Specialist for Lost Handbooks";

  return {
    TILE_SIZE,
    TOP_FACE_OVERHANG,
    GRID_COLS,
    GRID_ROWS,
    FLOOR_ROWS,
    CEIL_ROWS,
    MARGIN_COLS,
    NUM_WALLS,
    LOGICAL_WIDTH,
    LOGICAL_HEIGHT,
    INITIAL_SCALE,
    MIN_SCALE,
    WINDOW_TITLE,
  };
})();
