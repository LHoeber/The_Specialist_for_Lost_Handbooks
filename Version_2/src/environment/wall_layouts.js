/**
 * Wall layout definitions for the machine room. Direct port of
 * Version_1/src/environment/wall_layouts.py -- pure data, ported verbatim.
 * See that file's module docstring for the full convention writeup:
 *
 * Each wall is just a list of PlacedDevice entries: (type, anchor, kwargs)
 * where anchor is the device's top-left [row, column] cell -- its full
 * footprint is inferred from its sprite's pixel size at render time
 * (width/32, (height-6)/32), see ModuleBase -- and kwargs is an optional
 * object of extra constructor arguments for the rare device that needs
 * per-instance configuration (e.g. a specific Workbench's hidden contents).
 *
 * A device's own interactables (buttons, dials, ...) are NOT listed here --
 * each module class builds the ones intrinsic to it in its own constructor
 * (e.g. every Centrifuge owns a Button), so there is nothing to keep in sync
 * with this file when devices are added, removed or reordered. The only
 * interactables still declared as data are the room-level ones with no
 * device of their own -- see ROOM_INTERACTABLES at the bottom.
 *
 * Grid convention: [row, column], origin top-left. Each wall is 3 rows (0-2)
 * wide enough for a 4-column grid (0-3); a 0.5-cell floor strip sits below
 * row 2 but is not part of this module grid.
 *
 * Wall numbering: the "Wall Designs" diagram in Notion labels walls 1-4;
 * this file is 0-indexed (WALL_0 = diagram wall 1, ... WALL_3 = diagram
 * wall 4), matching the room orientation mechanics (wall 0 shown initially,
 * sequential 0->1->2->3->0).
 */
window.Game = window.Game || {};

Game.WallLayouts = (function () {
  // Machine modules / devices. See the "Machine modules" table in the Game
  // Prototype Notion page for each type's states, actions and size. DOOR and
  // WORKBENCH are plain furniture pieces that show up in the wall diagrams
  // but aren't part of that table.
  const ModuleType = Object.freeze({
    FURNACE: "FURNACE",
    PRESS: "PRESS",
    PRESSURE_TANK: "PRESSURE_TANK",
    CENTRIFUGE: "CENTRIFUGE",
    MIXER: "MIXER",
    PACKAGING_STATION: "PACKAGING_STATION",
    FILTER: "FILTER",
    FUME_HOOD: "FUME_HOOD",
    CONNECTOR_BOX: "CONNECTOR_BOX",
    FUSE_BOX: "FUSE_BOX",
    GENERATOR: "GENERATOR",
    ELECTROLYZER: "ELECTROLYZER",
    FLASK_HOLDER: "FLASK_HOLDER",
    DISHES: "DISHES",
    BIN: "BIN",
    SHELF: "SHELF",
    PIPES_WITH_VALVE: "PIPES_WITH_VALVE",
    PRESSURE_TANK_PIPES: "PRESSURE_TANK_PIPES",
    WIDE_PIPE: "WIDE_PIPE",
    TOOLBOX: "TOOLBOX",
    SINK: "SINK",
    FAUCET: "FAUCET",
    COMPOSITION_SCANNER: "COMPOSITION_SCANNER",
    CONTROL_PANEL: "CONTROL_PANEL",
    DOOR: "DOOR",
    WORKBENCH: "WORKBENCH",
    CLOCK: "CLOCK",
  });

  // Small UI elements attached to a device (or, for the movement arrows,
  // standalone at the room level). See the "Interactables" table in the
  // Game Prototype Notion page. LEVEL_INDICATOR, POWER_PLUG and COMPRESSOR
  // appear in the wall diagrams but aren't described in that table yet.
  const InteractableType = Object.freeze({
    BUTTON: "BUTTON",
    LEVER: "LEVER",
    DIAL: "DIAL",
    MOVE_ARROW_LEFT: "MOVE_ARROW_LEFT",
    MOVE_ARROW_RIGHT: "MOVE_ARROW_RIGHT",
    LEVEL_INDICATOR: "LEVEL_INDICATOR", // "Levels" (wall 0) / "Pressure Indicator" (wall 3) -- undocumented, verify
    POWER_PLUG: "POWER_PLUG", // wall 2 -- undocumented, verify
    COMPRESSOR: "COMPRESSOR", // a possible Workbench content -- undocumented, verify
    CABINET_DOOR: "CABINET_DOOR", // a Workbench's own door; see Objects.Workbench/CabinetDoor
    BEAKER: "BEAKER",
  });

  class PlacedDevice {
    constructor(type, anchor, kwargs = {}) {
      this.type = type;
      this.anchor = anchor; // [row, column] of the device's top-left cell
      this.kwargs = kwargs; // extra per-instance constructor args, rarely needed
    }
  }

  class PlacedInteractable {
    constructor(type, offset) {
      this.type = type;
      this.offset = offset; // [row, column], relative to the room origin
    }
  }

  // --- Wall 0 (diagram wall 1) --------------------------------------------

  const WALL_0_DEVICES = [
    new PlacedDevice(ModuleType.SHELF, [0, 1]),
    new PlacedDevice(ModuleType.SHELF, [0, 2]),
    new PlacedDevice(ModuleType.SHELF, [0, 3]),
    new PlacedDevice(ModuleType.SHELF, [1, 0]),
    new PlacedDevice(ModuleType.MIXER, [1, 0]), // spans down into row 1
    new PlacedDevice(ModuleType.DISHES, [0, 1]),
    new PlacedDevice(ModuleType.FLASK_HOLDER, [0, 2]),
    new PlacedDevice(ModuleType.FLASK_HOLDER, [0, 3]),
    new PlacedDevice(ModuleType.SHELF, [1, 1]),
    new PlacedDevice(ModuleType.DOOR, [1, 2]), // spans down into row 2
    new PlacedDevice(ModuleType.TOOLBOX, [2, 0]),
    new PlacedDevice(ModuleType.WORKBENCH, [2, 3], {
      contents: [[InteractableType.BEAKER, [0.0, 0.0]]],
    }),
  ];

  // --- Wall 1 (diagram wall 2) --------------------------------------------

  const WALL_1_DEVICES = [
    new PlacedDevice(ModuleType.COMPOSITION_SCANNER, [0, 0]), // spans down into row 1; "Mixture/Analyzer/Shutter" labels in diagram are its own state, not a separate object
    new PlacedDevice(ModuleType.SHELF, [0, 1]),
    new PlacedDevice(ModuleType.FUSE_BOX, [0, 3]),
    new PlacedDevice(ModuleType.SHELF, [1, 1]),
    new PlacedDevice(ModuleType.SHELF, [1, 2]),
    new PlacedDevice(ModuleType.PACKAGING_STATION, [1, 1]), // spans right into column 2
    new PlacedDevice(ModuleType.CONTROL_PANEL, [1, 3]),
    new PlacedDevice(ModuleType.WORKBENCH, [2, 0]),
    new PlacedDevice(ModuleType.BIN, [2, 1]),
    new PlacedDevice(ModuleType.CONNECTOR_BOX, [2, 2]),
    new PlacedDevice(ModuleType.GENERATOR, [2, 3]),
  ];

  // --- Wall 2 (diagram wall 3) --------------------------------------------

  const WALL_2_DEVICES = [
    new PlacedDevice(ModuleType.SHELF, [0, 0]),
    new PlacedDevice(ModuleType.SHELF, [0, 1]),
    new PlacedDevice(ModuleType.CLOCK, [0, 1]),
    new PlacedDevice(ModuleType.WIDE_PIPE, [0, 3]), // spans down into row 1
    new PlacedDevice(ModuleType.FILTER, [0, 2]), // spans down into row 1
    new PlacedDevice(ModuleType.CENTRIFUGE, [1, 0]),
    new PlacedDevice(ModuleType.ELECTROLYZER, [1, 1]),
    new PlacedDevice(ModuleType.PRESS, [1, 3]),
    new PlacedDevice(ModuleType.WORKBENCH, [2, 0]),
    new PlacedDevice(ModuleType.WORKBENCH, [2, 1]),
    new PlacedDevice(ModuleType.WORKBENCH, [2, 2]),
  ];

  // --- Wall 3 (diagram wall 4) --------------------------------------------

  const WALL_3_DEVICES = [
    new PlacedDevice(ModuleType.PRESSURE_TANK, [0, 0]),
    new PlacedDevice(ModuleType.PRESSURE_TANK_PIPES, [0, 0]),
    new PlacedDevice(ModuleType.SHELF, [0, 1]),
    new PlacedDevice(ModuleType.FUME_HOOD, [0, 2]),
    new PlacedDevice(ModuleType.FUME_HOOD, [0, 3]),
    new PlacedDevice(ModuleType.PIPES_WITH_VALVE, [1, 0]),
    new PlacedDevice(ModuleType.SINK, [2, 1]),
    new PlacedDevice(ModuleType.FAUCET, [1, 1]),
    new PlacedDevice(ModuleType.FURNACE, [1, 2]),
    // Placeholder content assignment: this is the one Workbench with
    // something hidden behind its door. Which workbenches get what (and
    // whether it's randomized) isn't designed yet -- see Objects.Workbench.
    new PlacedDevice(ModuleType.WORKBENCH, [2, 0], {
      contents: [[InteractableType.COMPRESSOR, [0.0, 0.0]]],
    }),
  ];

  const WALLS = [WALL_0_DEVICES, WALL_1_DEVICES, WALL_2_DEVICES, WALL_3_DEVICES];

  // The movement arrows are standalone room-level interactables, not
  // attached to a device. They sit at the wall's middle row, in the
  // half-cell side margins outside the 4-column device grid (column -0.5
  // and 3.5), so they never overlap a placed module.
  const ROOM_INTERACTABLES = [
    new PlacedInteractable(InteractableType.MOVE_ARROW_LEFT, [1, -0.5]),
    new PlacedInteractable(InteractableType.MOVE_ARROW_RIGHT, [1, 3.5]),
  ];

  return {
    ModuleType,
    InteractableType,
    PlacedDevice,
    PlacedInteractable,
    WALLS,
    ROOM_INTERACTABLES,
  };
})();
