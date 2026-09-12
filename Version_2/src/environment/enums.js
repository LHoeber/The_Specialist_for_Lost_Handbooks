/**
 * General enums for the game environment. Direct port of
 * Version_1/src/environment/enums.py. ModuleType and InteractableType are
 * the wall-placement vocabulary and live in wall_layouts.js (the
 * machine-readable source of truth for exact placements) -- re-exported
 * here so the rest of the environment/rendering code can pull them from one
 * place alongside enums that aren't about placement.
 */
window.Game = window.Game || {};

Game.Enums = (function () {
  // Room-level movement (also doubles as sub-grid movement -- see
  // Objects.SubGrid.move) plus wall-to-wall rotation, which now reuses
  // LEFT/RIGHT rather than a separate concept (see grid-navigation.md).
  const Direction = Object.freeze({ UP: "UP", DOWN: "DOWN", LEFT: "LEFT", RIGHT: "RIGHT" });

  return {
    ModuleType: Game.WallLayouts.ModuleType,
    InteractableType: Game.WallLayouts.InteractableType,
    Direction,
  };
})();
