/**
 * Room state: builds the four walls' modules once at startup (so module
 * state can persist across visits once modules have real behavior), tracks
 * which wall is currently being viewed, and (see docs/design/grid-navigation.md)
 * the player's discrete grid position, sub-grid-or-null, and the "do"
 * dispatch that drives all of it.
 */
window.Game = window.Game || {};

Game.State = (function () {
  const { Direction } = Game.Enums;
  const { GRID_ROWS, GRID_COLS } = Game.Config;
  const { MODULE_CLASSES } = Game.Objects;
  const { WALLS } = Game.WallLayouts;

  // The navigable grid extends beyond the module grid to include the floor/
  // ceiling half-rows and the left/right half-column margins -- every cell
  // is addressable even though "do" does nothing there yet (see
  // grid-navigation.md, "Room-level grid"). Reaching a margin column is
  // just an extra step, like reaching the floor/ceiling; a *second* LEFT/
  // RIGHT past it is what actually triggers wall rotation (see
  // _performRoomAction below).
  const ROW_MIN = -1; // ceiling strip
  const ROW_MAX = GRID_ROWS; // floor strip
  const COL_MIN = -1; // left margin half-column
  const COL_MAX = GRID_COLS; // right margin half-column

  /**
   * One wall's live modules, built from its wall_layouts.js device list.
   * Each module owns its own interactables (see Objects.ModuleBase); this
   * just flattens them for rendering/hit-testing.
   */
  class Wall {
    constructor(wallIndex, devices) {
      this.wallIndex = wallIndex;
      this.modules = devices.map((device) => {
        const ModuleClass = MODULE_CLASSES[device.type];
        return new ModuleClass(wallIndex, device.anchor, device.kwargs);
      });
      this.interactables = this.modules.flatMap((module) => module.interactables);
    }
  }

  /**
   * All four walls, the currently-viewed wall index, and the player's
   * position on it. `playerSubGrid` is null at room level, or
   * `{ module, entry, cellIndex }` while inside one of a module's
   * sub-grids -- `entry` is the `{offset, grid}` pair from
   * `module.subGrids` that was entered (see Objects.ModuleBase) -- there is
   * no third state (grid-navigation.md).
   */
  class RoomState {
    constructor() {
      this.walls = WALLS.map((devices, index) => new Wall(index, devices));
      this.currentWallIndex = 0;
      this.playerPosition = [1, 0]; // arbitrary reasonable default -- see grid-navigation.md
      this.playerSubGrid = null;
    }

    get currentWall() {
      return this.walls[this.currentWallIndex];
    }

    rotate(direction) {
      const step = direction === Direction.RIGHT ? 1 : -1;
      const n = this.walls.length;
      // JS's % can return a negative result (unlike Python's), so normalize.
      this.currentWallIndex = ((this.currentWallIndex + step) % n + n) % n;
    }

    /**
     * The single input-agnostic entry point for both movement and "do" --
     * a keyboard handler (or, eventually, a scripted agent) should do
     * nothing but call this with one of Direction.UP/DOWN/LEFT/RIGHT or the
     * string "do" (see grid-navigation.md, "Keep movement/do as a shared,
     * input-agnostic function").
     */
    performAction(action) {
      if (this.playerSubGrid) {
        this._performSubGridAction(action);
      } else {
        this._performRoomAction(action);
      }
    }

    //moving around or room-level "do"
    _performRoomAction(action) {
      // perfrom action for modules that themselves are the interactable; have no subgrid
      if (action === "do") {
        this._performRoomDo();
        return;
      }
      // simple movement without action, restricted by window
      const [row, col] = this.playerPosition;
      if (action === Direction.UP) {
        this.playerPosition = [Math.max(row - 1, ROW_MIN), col];
      } else if (action === Direction.DOWN) {
        this.playerPosition = [Math.min(row + 1, ROW_MAX), col];
      } else if (action === Direction.LEFT) {
        if (col > COL_MIN) {
          this.playerPosition = [row, col - 1];
        } else {// moving to next wall
          // Rotation triggers only on the *next* move past the edge, and
          // lands on the opposite edge column, same row (grid-navigation.md,
          // "Wall-to-wall rotation") -- a genuine two-step motion, not an
          // instant trigger from merely arriving at column 0.
          this.rotate(Direction.LEFT);
          this.playerPosition = [row, COL_MAX];
        }
      } else if (action === Direction.RIGHT) {
        if (col < COL_MAX) {
          this.playerPosition = [row, col + 1];
        } else {
          this.rotate(Direction.RIGHT);
          this.playerPosition = [row, COL_MIN];
        }
      }
    }

    //handling the room-level "do" 
    _performRoomDo() {
      const wall = this.currentWall;
      const [row, col] = this.playerPosition;

      const target = wall.interactables.find(
        (i) => i.visible && i.anchor[0] === row && i.anchor[1] === col
      );
      if (target) {
        target.doAction(this);
        return;
      }

      //entering a subgrid if exists
      for (const module of wall.modules) {
        for (const entry of module.subGrids) {
          const entryRow = module.anchor[0] + entry.offset[0];
          const entryCol = module.anchor[1] + entry.offset[1];
          if (entryRow === row && entryCol === col) {
            this.playerSubGrid = { module, entry, cellIndex: entry.grid.exitIndex };
            return;
          }
        }
      }

      // Whole-module "do": any of the module's occupied cells that isn't
      // already claimed by an interactable or a sub-grid entry above falls
      // through to the module's own doAction -- not just its anchor tile
      // (see ModuleBase.doAction's "one direct room-level action" case).
      // -> all cells part of the module defalt to the modules "whole-body" action if the don't have subgrid
      const roomModule = wall.modules.find((m) => {
        const [r0, c0] = m.anchor;
        return row >= r0 && row < r0 + m.heightCells && col >= c0 && col < c0 + m.widthCells;
      });
      if (roomModule) {
        roomModule.doAction(this);
      }
      // Otherwise: nothing defined here -- silent no-op (grid-navigation.md's
      // "never pre-filter legal actions" stance).
    }

    _performSubGridAction(action) {
      // entry ... {offset, subgrid} of the currently selected module
      const { module, entry, cellIndex } = this.playerSubGrid;
      // player wants to interact
      if (action === "do") {
        const cell = entry.grid.cells[cellIndex];
        if (cell.kind === "exit") {
          this.playerSubGrid = null;
        } else {
          cell.interactable.doAction(this);
          this.playerSubGrid = null; // execute-and-auto-exit -- no third state
        }
        return;
      }
      //player only wants to move
      this.playerSubGrid = { module, entry, cellIndex: entry.grid.move(cellIndex, action) };
    }
  }

  return { Wall, RoomState };
})();
