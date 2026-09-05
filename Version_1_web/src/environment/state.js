/**
 * Room state: builds the four walls' modules once at startup (so module
 * state can persist across visits once modules have real behavior) and
 * tracks which wall is currently being viewed. Direct port of
 * Version_1/src/environment/state.py.
 */
window.Game = window.Game || {};

Game.State = (function () {
  const { Direction } = Game.Enums;
  const { MODULE_CLASSES, INTERACTABLE_CLASSES } = Game.Objects;
  const { WALLS, ROOM_INTERACTABLES } = Game.WallLayouts;

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

  /** All four walls plus the currently-viewed wall index. */
  class RoomState {
    constructor() {
      this.walls = WALLS.map((devices, index) => new Wall(index, devices));
      // Movement arrows are room-level and identical on every wall, so
      // they're built once here rather than per-wall.
      this.roomInteractables = ROOM_INTERACTABLES.map((item) => {
        const InteractableClass = INTERACTABLE_CLASSES[item.type];
        return new InteractableClass(item.offset, null);
      });
      this.currentWallIndex = 0;
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
  }

  return { Wall, RoomState };
})();
