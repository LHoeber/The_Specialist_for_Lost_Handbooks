/**
 * Module and interactable classes placed on the machine-room walls. Direct
 * port of Version_1/src/environment/objects.py.
 *
 * Every concrete class below is a Phase 1 placeholder: it only carries the
 * structural state (position, sprites) needed to render the room and rotate
 * between walls. Device-specific behavior (heating, mixing, breakage, ...)
 * gets added to these classes as each one's mechanics are designed -- see
 * ../Version_1/docs/design/game-prototype.md and ../Version_1_web/CLAUDE.md
 * ("Going forward") for where new behavior should be written from now on.
 */
window.Game = window.Game || {};

Game.Objects = (function () {
  const { TILE_SIZE, TOP_FACE_OVERHANG } = Game.Config;
  const { Direction, ModuleType, InteractableType } = Game.Enums;
  const {
    MODULE_SPRITES,
    INTERACTABLE_SPRITES,
    LEVEL_SPRITES,
    BUTTON_SPRITES,
    CABINET_DOOR_SPRITES,
    FURNACE_HEAT_SPRITES,
    loadImage,
  } = Game.Assets;

  // How long Button's pressed-flash step shows before settling onto on/off
  // -- see Button.doAction / SpriteOwner.playAnimation.
  const BUTTON_FLASH_SECONDS = 0.15;

  /**
   * Shared sprite-owning behavior for anything drawn as one or more layered
   * (optionally animated) sprites at some [row, column] position -- both
   * machine modules and interactables are exactly this, so both extend it
   * instead of each having their own copy of this loading/sizing logic.
   *
   * `spriteNames` entries are either a plain path string, or an animated
   * sprite-sheet spec: {path, frames, channels, seconds, frame_width,
   * frame_height} (see Assets.loadImage / Sprite / Renderer._currentFrame).
   * `spriteHasOverhang` is the default top-down-perspective flag (see
   * Config.TOP_FACE_OVERHANG) applied to every entry loaded for this class;
   * `ModuleBase` defaults it to true (every module sprite uses that
   * convention), `InteractableBase` defaults it to false (most interactable
   * icons are flat), and either can be overridden per concrete subclass.
   *
   * Size is inferred from the first sprite layer, same convention
   * throughout: TILE_SIZE px wide by (38 + (n-1)*32) px tall for an n-cell
   * module, minus the overhang strip if that layer has one.
   */
  class SpriteOwner {
    static spriteNames = [];
    static spriteHasOverhang = false;

    constructor() {
      this.setSprites(
        this.constructor.spriteNames.map((entry) => {
          if (typeof entry === "string") {
            return loadImage(entry, this.constructor.spriteHasOverhang);
          }
          // Animated sprite-sheet entry.
          return loadImage(
            entry.path,
            this.constructor.spriteHasOverhang,
            entry.frames,
            entry.channels,
            entry.seconds,
            entry.frame_width,
            entry.frame_height,
          );
        })
      );
      // A one-shot or looping timed sprite sequence started by
      // playAnimation(), temporarily overriding the sprites/spriteOffsets
      // layers above -- see that method and Renderer._advanceAnimation.
      this._animation = null;
    }

    /**
     * Starts a timed sprite sequence that temporarily overrides this
     * owner's whole display (not a specific layer): each step shows
     * `step.sprite` for `step.seconds`, in order. `loop:false` (default)
     * plays once, then runs `onFinish` -- typically a setSprites() call
     * for whatever should persist afterwards -- and reverts to the normal
     * sprites/spriteOffsets layers; `loop:true` cycles the steps forever
     * instead of ever finishing. Used for e.g. Button's pressed-flash.
     * Actually resolved against elapsed wall-clock time once per render by
     * Renderer._advanceAnimation, the same evaluate-per-frame approach
     * already used for animated sprite-sheet frames (_currentFrame).
     */
    playAnimation(steps, { loop = false, onFinish = null } = {}) {
      // onFinish ... lambda function, that will be executed after animation ends
      // steps ... list of {sprites, duration}
      this._animation = { steps, startedAt: performance.now() / 1000, loop, onFinish };
    }

    // Swaps which sprite(s) this owner draws (e.g. CabinetDoor's open vs.
    // closed state) while keeping `spriteOffsets` the same length as
    // `sprites` -- go through this rather than assigning `this.sprites`
    // directly, so the two arrays can't drift out of sync.
    setSprites(sprites) {
      this.sprites = sprites;
      // Relative [row, column] offset of each sprite layer from this
      // owner's own anchor; all layers share the anchor by default (e.g.
      // Mixer's or Beaker's back/front pair), but a layer could be offset
      // later if needed.
      this.spriteOffsets = sprites.map(() => [0.0, 0.0]);
    }

    get widthCells() {
      return this.sprites[0].width / TILE_SIZE;
    }

    get heightCells() {
      const sprite = this.sprites[0];
      return (sprite.height - (sprite.hasOverhang ? TOP_FACE_OVERHANG : 0)) / TILE_SIZE;
    }
  }

  /**
   * One subcell of a module's sub-grid (see SubGrid below): a rectangular
   * region of the single 32x32 tile the sub-grid lives in. `kind` is
   * "exit" (free of any interactable; landing point on entry, exits back
   * to room-level) or "action" (has one `interactable` whose `doAction`
   * runs, then auto-exits).
   *
   * `anchor` is [row0, col0], the cell's top-left corner as a 0..1 fraction
   * of the tile; `size` is [height, width], same units, defaulting to the
   * interactable's own sprite size (via SpriteOwner's heightCells/
   * widthCells) when omitted -- pass `size` explicitly only when the
   * desired footprint doesn't match the sprite's native size (e.g. the
   * Furnace's heatIndicator cell below, which is deliberately half-width
   * regardless of that icon's actual pixel dimensions).
   */
  class SubGridCell {
    constructor(anchor, kind, interactable = null, size = null) {
      this.anchor = anchor;
      this.kind = kind; // "exit" | "action"
      this.interactable = interactable;
      // if size is given, use that; otherwise check if interactable has a size, else default to 1x1
      this.size = size ?? (interactable ? [interactable.heightCells, interactable.widthCells] : [1, 1]);
    }

    // [row0, row1, col0, col1] fractions, derived from anchor + size --
    // SubGrid.move()'s adjacency math and the renderer both read this shape,
    // unchanged by the anchor/size rework above.
    get rect() {
      const [row0, col0] = this.anchor;
      const [h, w] = this.size;
      // for checking start/end of rows/cols
      return { row0, row1: row0 + h, col0, col1: col0 + w };
    }
  }

  /**
   * A module's sub-grid: discrete rectangular sectioning of its one
   * designated interactive tile (see docs/design/grid-navigation.md). Move
   * resolution is pure geometry (which cell shares the right border for a
   * rightward move, etc.) plus the two fixed tie-break defaults for the
   * only ambiguity shapes rectangular sectioning can produce: a horizontal
   * move into a multi-row-spanning target prefers the lower row; a
   * vertical move into a multi-column-spanning target prefers the
   * leftmost column.
   */
  class SubGrid {
    constructor(cells) {
      this.cells = cells;
      this.exitIndex = cells.findIndex((cell) => cell.kind === "exit");
    }

    move(fromIndex, direction) {
      const from = this.cells[fromIndex].rect;
      const candidates = this.cells.filter((cell, index) => {
        if (index === fromIndex) return false;
        const r = cell.rect;
        const rowsOverlap = r.row0 < from.row1 && r.row1 > from.row0;//common row idices
        const colsOverlap = r.col0 < from.col1 && r.col1 > from.col0;//common col indices
        // same row and directly adjacent
        if (direction === Direction.LEFT) return r.col1 === from.col0 && rowsOverlap;
        if (direction === Direction.RIGHT) return r.col0 === from.col1 && rowsOverlap;
        // same column and directly adjacent
        if (direction === Direction.UP) return r.row1 === from.row0 && colsOverlap;
        if (direction === Direction.DOWN) return r.row0 === from.row1 && colsOverlap;
        return false;
      });
      if (candidates.length === 0) return fromIndex; // sub-grid edge -- stay put
      const horizontal = direction === Direction.LEFT || direction === Direction.RIGHT;
      // reducer defines the first checked variable as best and then iteratively updates
      const winner = candidates.reduce((best, cell) => {
        if (horizontal) return cell.rect.row0 > best.rect.row0 ? cell : best; // prefer lower row
        return cell.rect.col0 < best.rect.col0 ? cell : best; // prefer leftmost column
      });
      return this.cells.indexOf(winner);
    }
  }

  /** Shared behavior for every machine module / furniture piece. */
  class ModuleBase extends SpriteOwner {
    static moduleType = null;
    static spriteHasOverhang = true; // every module sprite uses the top-down-perspective convention

    constructor(wallIndex, anchor) {
      super();
      this.wallIndex = wallIndex;
      this.anchor = anchor; // [row, column] of the top-left occupied cell
      // Interactables this module owns (buttons, dials, ...), positioned
      // relative to its own anchor. Empty unless a subclass adds its own.
      this.interactables = [];
      // Any number of this module's occupied tiles can "opt in" to a
      // sub-grid (see Furnace below for a worked example) -- each entry is
      // `{offset, grid}`, `offset` being that tile's [row, col] offset from
      // the module's own anchor and `grid` a SubGrid; "do" on a tile
      // matching some entry's offset enters that entry's grid. Empty
      // unless a subclass adds one (most modules have none).
      this.subGrids = [];
    }

    // For a module with no sub-grid that still has exactly one direct
    // room-level action (see "Modules without sub-functions" in
    // grid-navigation.md) -- override in a subclass. No-op default, same
    // convention as InteractableBase.doAction.
    // eslint-disable-next-line no-unused-vars
    doAction(roomState) { }
  }

  /**
   * Worked example for the sub-grid mechanic (see grid-navigation.md).
   * Footprint is 2x2 (anchor = top-left, rows/cols [0,1] relative to it);
   * only the top-right tile ([0,1]) hosts a sub-grid. The anchor tile
   * itself carries a heat-state overlay layer (see FURNACE_HEAT_SPRITES)
   * kept in sync with the sub-grid's heatIndicator cell. The other two
   * tiles have no "do" behavior yet -- flask in/out and door open/close
   * still need a home in a future iteration.
   */
  class Furnace extends ModuleBase {
    static moduleType = ModuleType.FURNACE;
    static spriteNames = MODULE_SPRITES[ModuleType.FURNACE];

    constructor(wallIndex, anchor) {
      // already loading all sprites and basic attributes
      super(wallIndex, anchor);

      // Anchor tile: base furnace body plus a heat-state overlay layer,
      // both drawn at offset [0,0] (the anchor itself).
      this._baseSprite = this.sprites[0];
      // load images from all the sprite paths saved in furnace_heat_sprites to
      this._heatSprites = FURNACE_HEAT_SPRITES.map((path) => loadImage(path, true));
      this.heatLevel = 0; // index into _heatSprites: off/low/medium/high
      this.setSprites([this._baseSprite, this._heatSprites[this.heatLevel]]);

      // heatIndicator is only ever reached through the sub-grid cell below,
      // never via room-level module.interactables, so its own offset/parent
      // are inert (see InteractableBase.anchor) -- [0,0]/null is just a
      // harmless placeholder, not a real position.
      this.heatIndicator = new LevelIndicator([0, 0], null);
      this.heatIndicator.doAction = () => {
        this.heatLevel = (this.heatLevel + 1) % 4; // wraps: off -> low -> medium -> high -> off
        this.heatIndicator.setLevel(this.heatLevel);
        this.setSprites([this._baseSprite, this._heatSprites[this.heatLevel]]);
      };
      const emergencyButton = new Button([0, 0], null);

      // Sub-grid, entered from tile [0,1] (upper-right of the footprint).
      this.subGrids = [{
        offset: [0, 1],
        grid: new SubGrid([
          new SubGridCell([0.5, 0], "exit", null, [0.5, 0.5]),
          new SubGridCell([0, 0], "action", emergencyButton, [0.5, 0.5]),
          // Explicit half-width size: LevelIndicator's icon isn't natively
          // half-width, so the default (sprite-size) footprint wouldn't fit.
          new SubGridCell([0, 0.5], "action", this.heatIndicator, [1, 0.5]),
        ]),
      }];
    }
  }

  class Press extends ModuleBase {
    static moduleType = ModuleType.PRESS;
    static spriteNames = MODULE_SPRITES[ModuleType.PRESS];

    constructor(wallIndex, anchor) {
      super(wallIndex, anchor);
      this.interactables = [new Lever([1.0, 1.0], this)];
    }
  }

  class PressureTank extends ModuleBase {
    static moduleType = ModuleType.PRESSURE_TANK;
    static spriteNames = MODULE_SPRITES[ModuleType.PRESSURE_TANK];

    constructor(wallIndex, anchor) {
      super(wallIndex, anchor);
      this.interactables = [new LevelIndicator([0.2, 0.0], this)];
    }
  }

  class Centrifuge extends ModuleBase {
    static moduleType = ModuleType.CENTRIFUGE;
    static spriteNames = MODULE_SPRITES[ModuleType.CENTRIFUGE];

    constructor(wallIndex, anchor) {
      super(wallIndex, anchor);
      this.interactables = [new Button([0.5, 0.0], this)];
    }
  }

  class Mixer extends ModuleBase {
    static moduleType = ModuleType.MIXER;
    static spriteNames = MODULE_SPRITES[ModuleType.MIXER];

    constructor(wallIndex, anchor) {
      super(wallIndex, anchor);
      this.interactables = [
        new Button([0.5, 0.0], this),
        new LevelIndicator([1.0, 0.5], this), // VERIFY: exact offset
      ];
    }
  }

  class PackagingStation extends ModuleBase {
    static moduleType = ModuleType.PACKAGING_STATION;
    static spriteNames = MODULE_SPRITES[ModuleType.PACKAGING_STATION];
  }

  class Filter extends ModuleBase {
    static moduleType = ModuleType.FILTER;
    static spriteNames = MODULE_SPRITES[ModuleType.FILTER];
  }

  class FumeHood extends ModuleBase {
    static moduleType = ModuleType.FUME_HOOD;
    static spriteNames = MODULE_SPRITES[ModuleType.FUME_HOOD];
  }

  class ConnectorBox extends ModuleBase {
    static moduleType = ModuleType.CONNECTOR_BOX;
    static spriteNames = MODULE_SPRITES[ModuleType.CONNECTOR_BOX];
  }

  class FuseBox extends ModuleBase {
    static moduleType = ModuleType.FUSE_BOX;
    static spriteNames = MODULE_SPRITES[ModuleType.FUSE_BOX];
  }

  class Generator extends ModuleBase {
    static moduleType = ModuleType.GENERATOR;
    static spriteNames = MODULE_SPRITES[ModuleType.GENERATOR];
  }

  class Electrolyzer extends ModuleBase {
    static moduleType = ModuleType.ELECTROLYZER;
    static spriteNames = MODULE_SPRITES[ModuleType.ELECTROLYZER];

    constructor(wallIndex, anchor) {
      super(wallIndex, anchor);
      this.interactables = [new Button([0.5, 0.0], this)];
    }
  }

  class FlaskHolder extends ModuleBase {
    static moduleType = ModuleType.FLASK_HOLDER;
    static spriteNames = MODULE_SPRITES[ModuleType.FLASK_HOLDER];
  }

  class Dishes extends ModuleBase {
    static moduleType = ModuleType.DISHES;
    static spriteNames = MODULE_SPRITES[ModuleType.DISHES];
  }

  class Bin extends ModuleBase {
    static moduleType = ModuleType.BIN;
    static spriteNames = MODULE_SPRITES[ModuleType.BIN];
  }

  class Shelf extends ModuleBase {
    static moduleType = ModuleType.SHELF;
    static spriteNames = MODULE_SPRITES[ModuleType.SHELF];
  }

  class PipesWithValve extends ModuleBase {
    static moduleType = ModuleType.PIPES_WITH_VALVE;
    static spriteNames = MODULE_SPRITES[ModuleType.PIPES_WITH_VALVE];
  }

  class PressureTankPipes extends ModuleBase {
    static moduleType = ModuleType.PRESSURE_TANK_PIPES;
    static spriteNames = MODULE_SPRITES[ModuleType.PRESSURE_TANK_PIPES];
  }

  class WidePipe extends ModuleBase {
    static moduleType = ModuleType.WIDE_PIPE;
    static spriteNames = MODULE_SPRITES[ModuleType.WIDE_PIPE];
  }

  class Toolbox extends ModuleBase {
    static moduleType = ModuleType.TOOLBOX;
    static spriteNames = MODULE_SPRITES[ModuleType.TOOLBOX];
  }


  class Sink extends ModuleBase {
    static moduleType = ModuleType.SINK;
    static spriteNames = MODULE_SPRITES[ModuleType.SINK];
  }

  class Faucet extends ModuleBase {
    static moduleType = ModuleType.FAUCET;
    static spriteNames = MODULE_SPRITES[ModuleType.FAUCET];
  }

  class CompositionScanner extends ModuleBase {
    static moduleType = ModuleType.COMPOSITION_SCANNER;
    static spriteNames = MODULE_SPRITES[ModuleType.COMPOSITION_SCANNER];
  }

  class ControlPanel extends ModuleBase {
    static moduleType = ModuleType.CONTROL_PANEL;
    static spriteNames = MODULE_SPRITES[ModuleType.CONTROL_PANEL];
  }

  class Clock extends ModuleBase {
    static moduleType = ModuleType.CLOCK;
    static spriteNames = MODULE_SPRITES[ModuleType.CLOCK];
  }

  class Door extends ModuleBase {
    static moduleType = ModuleType.DOOR;
    static spriteNames = MODULE_SPRITES[ModuleType.DOOR];
  }

  class Workbench extends ModuleBase {
    static moduleType = ModuleType.WORKBENCH;
    static spriteNames = MODULE_SPRITES[ModuleType.WORKBENCH];

    constructor(wallIndex, anchor, { contents = [] } = {}) {
      super(wallIndex, anchor);
      const door = new CabinetDoor([0.0, 0.0], this);
      // Placeholder: `contents` is just a list of [InteractableType, offset]
      // handed in from wall_layouts.js, hidden until the door opens. Which
      // workbenches get what -- and whether it's randomized -- isn't
      // designed yet; this only proves the door/reveal mechanism works.
      door.contents = contents.map(([contentType, offset]) => {
        const ContentClass = INTERACTABLE_CLASSES[contentType];
        return new ContentClass(offset, this, false);
      });
      this.interactables = [...door.contents, door, door.closeHandle];
    }
  }

  const MODULE_CLASSES = {
    [ModuleType.FURNACE]: Furnace,
    [ModuleType.PRESS]: Press,
    [ModuleType.PRESSURE_TANK]: PressureTank,
    [ModuleType.CENTRIFUGE]: Centrifuge,
    [ModuleType.MIXER]: Mixer,
    [ModuleType.PACKAGING_STATION]: PackagingStation,
    [ModuleType.FILTER]: Filter,
    [ModuleType.FUME_HOOD]: FumeHood,
    [ModuleType.CONNECTOR_BOX]: ConnectorBox,
    [ModuleType.FUSE_BOX]: FuseBox,
    [ModuleType.GENERATOR]: Generator,
    [ModuleType.ELECTROLYZER]: Electrolyzer,
    [ModuleType.FLASK_HOLDER]: FlaskHolder,
    [ModuleType.DISHES]: Dishes,
    [ModuleType.BIN]: Bin,
    [ModuleType.SHELF]: Shelf,
    [ModuleType.PIPES_WITH_VALVE]: PipesWithValve,
    [ModuleType.PRESSURE_TANK_PIPES]: PressureTankPipes,
    [ModuleType.WIDE_PIPE]: WidePipe,
    [ModuleType.TOOLBOX]: Toolbox,
    [ModuleType.SINK]: Sink,
    [ModuleType.FAUCET]: Faucet,
    [ModuleType.COMPOSITION_SCANNER]: CompositionScanner,
    [ModuleType.CONTROL_PANEL]: ControlPanel,
    [ModuleType.DOOR]: Door,
    [ModuleType.WORKBENCH]: Workbench,
    [ModuleType.CLOCK]: Clock,
  };

  /**
   * Shared behavior for a UI element attached to a module. `spriteNames`
   * works exactly as it does for modules (see SpriteOwner) -- most
   * interactables are one flat icon (a 1-element array), but nothing stops
   * one from being layered (Beaker's back/front pair) or animated, the
   * same mechanism either way.
   */
  class InteractableBase extends SpriteOwner {
    static interactableType = null;
    // Most interactables are flat icons with no top-face strip. Override to
    // true on a subclass whose sprite(s) *do* use that convention (e.g.
    // Compressor, Beaker, CabinetDoor below).
    static spriteHasOverhang = false;

    constructor(offset, parent = null, visible = true) {
      super();
      this.offset = offset; // [row, column] relative to the parent module's anchor
      this.parent = parent; // a ModuleBase instance, or null for room-level
      this.visible = visible;
    }

    // Placeholder: concrete interactables override this once their specific
    // action is designed. No-op by default. Called by RoomState.performAction
    // ("do") -- see grid-navigation.md's "shared, input-agnostic function".
    // eslint-disable-next-line no-unused-vars
    doAction(roomState) { }

    get anchor() {
      // use parent anchor coordiantes as relative anchor, or if no parent exists, default to [0,0]
      const parentAnchor = this.parent !== null ? this.parent.anchor : [0, 0];
      return [parentAnchor[0] + this.offset[0], parentAnchor[1] + this.offset[1]];
    }
  }

  /**
   * Toggles between off/on -- see Assets.BUTTON_SPRITES. Each "do" briefly
   * flashes the pressed sprite, then settles onto (and holds) whichever of
   * on/off it just switched to, without blocking input in the meantime --
   * see SpriteOwner.playAnimation.
   */
  class Button extends InteractableBase {
    static interactableType = InteractableType.BUTTON;

    constructor(offset, parent = null, visible = true) {
      super(offset, parent, visible);
      this.on = false;
      this._offSprite = loadImage(BUTTON_SPRITES.off);
      this._pressedSprite = loadImage(BUTTON_SPRITES.pressed);
      this._onSprite = loadImage(BUTTON_SPRITES.on);
      this.setSprites([this._offSprite]);
    }

    doAction(_roomState) {
      const goingOn = !this.on;//toggle on/off, depending on current state
      this.on = goingOn;
      this.playAnimation([{ sprite: this._pressedSprite, seconds: BUTTON_FLASH_SECONDS }], {
        onFinish: () => this.setSprites([goingOn ? this._onSprite : this._offSprite]),
      });
    }
  }

  class Lever extends InteractableBase {
    static interactableType = InteractableType.LEVER;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.LEVER]];
  }

  class Dial extends InteractableBase {
    static interactableType = InteractableType.DIAL;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.DIAL]];
  }

  /** Cycles through off/low/medium/high -- see Assets.LEVEL_SPRITES. */
  class LevelIndicator extends InteractableBase {
    static interactableType = InteractableType.LEVEL_INDICATOR;

    constructor(offset, parent = null, visible = true) {
      super(offset, parent, visible);
      this._levelSprites = LEVEL_SPRITES.map((path) => loadImage(path));
      this.level = 0;
      this.setSprites([this._levelSprites[0]]);
    }

    setLevel(level) {
      this.level = level;
      this.setSprites([this._levelSprites[level]]);
    }
  }

  class Compressor extends InteractableBase {
    static interactableType = InteractableType.COMPRESSOR;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.COMPRESSOR]];
    static spriteHasOverhang = true; // counter_compressor.png uses the perspective convention
  }

  class Beaker extends InteractableBase {
    static interactableType = InteractableType.BEAKER;
    static spriteNames = INTERACTABLE_SPRITES[InteractableType.BEAKER]; // [back, front]
    static spriteHasOverhang = true; // beaker sprites use the perspective convention
  }

  /**
   * The Workbench's own door/hatch (see grid-navigation.md, "Existing
   * behavior carried over: Workbench cabinet door"). Closed (default): "do"
   * at the anchor tile opens it. Open: the anchor tile goes empty and the
   * door's own open sprite (see Assets.CABINET_DOOR_SPRITES) is drawn on
   * the tile to the right (anchor + [0,1]) instead, where a companion
   * CabinetDoorCloseHandle becomes visible; "do" at the anchor while open
   * is a no-op (not a second way to close it), matching the spec exactly.
   */
  class CabinetDoor extends InteractableBase {
    static interactableType = InteractableType.CABINET_DOOR;
    static spriteHasOverhang = true;

    constructor(offset, parent = null) {
      super(offset, parent, true);
      this.open = false;
      this.contents = []; // assigned by the owning module after construction
      this._closedSprite = loadImage(CABINET_DOOR_SPRITES.closed, true);
      this._openSprite = loadImage(CABINET_DOOR_SPRITES.open, true);
      this.setSprites([this._closedSprite]);
      this.closeHandle = new CabinetDoorCloseHandle([offset[0], offset[1] + 1], parent, this);
    }

    doAction(_roomState) {
      if (this.open) return; // no-op -- closing only happens from closeHandle's tile
      this.open = true;
      this.setSprites([]);
      // The door's own open sprite is what actually gets drawn, now at the
      // tile to the right instead of at the anchor.
      this.closeHandle.setSprites([this._openSprite]);
      this.closeHandle.visible = true;
      for (const item of this.contents) {
        item.visible = true;
      }
    }
  }

  /**
   * The tile a CabinetDoor's panel swings open onto (anchor + [0,1]). Not
   * placed via wall_layouts.js data like other interactables -- it's always
   * constructed directly by its CabinetDoor, which also owns showing/hiding
   * it and setting its sprite (the door's own open sprite -- see
   * CabinetDoor.doAction). Invisible with no sprite until the door opens.
   */
  class CabinetDoorCloseHandle extends InteractableBase {
    constructor(offset, parent, door) {
      super(offset, parent, false);
      this.door = door;
    }

    doAction(_roomState) {
      this.door.open = false;
      this.door.setSprites([this.door._closedSprite]);
      this.visible = false;
      for (const item of this.door.contents) {
        item.visible = false;
      }
    }
  }

  /**
   * Defined as a type but not yet placed on any wall -- no sprite has been
   * decided for it (see docs/design/game-prototype.md).
   */
  class PowerPlug extends InteractableBase {
    static interactableType = InteractableType.POWER_PLUG;
    static spriteNames = [];
  }

  const INTERACTABLE_CLASSES = {
    [InteractableType.BUTTON]: Button,
    [InteractableType.LEVER]: Lever,
    [InteractableType.DIAL]: Dial,
    [InteractableType.LEVEL_INDICATOR]: LevelIndicator,
    [InteractableType.COMPRESSOR]: Compressor,
    [InteractableType.POWER_PLUG]: PowerPlug,
    [InteractableType.CABINET_DOOR]: CabinetDoor,
    [InteractableType.BEAKER]: Beaker,
  };

  return {
    ModuleBase,
    MODULE_CLASSES,
    SubGrid,
    SubGridCell,
    InteractableBase,
    Button,
    Lever,
    Dial,
    LevelIndicator,
    Compressor,
    Beaker,
    CabinetDoor,
    CabinetDoorCloseHandle,
    PowerPlug,
    INTERACTABLE_CLASSES,
  };
})();
