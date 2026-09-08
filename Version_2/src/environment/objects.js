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
  const { MODULE_SPRITES, INTERACTABLE_SPRITES, CABINET_DOOR_SPRITES, loadImage } = Game.Assets;

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
    }
  }

  class Furnace extends ModuleBase {
    static moduleType = ModuleType.FURNACE;
    static spriteNames = MODULE_SPRITES[ModuleType.FURNACE];

    constructor(wallIndex, anchor) {
      super(wallIndex, anchor);
      this.interactables = [new Dial([1.0, 0.5], this)];
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

  class BeakerHolder extends ModuleBase {
    static moduleType = ModuleType.BEAKER_HOLDER;
    static spriteNames = MODULE_SPRITES[ModuleType.BEAKER_HOLDER];
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
      this.interactables = [...door.contents, door];
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
    [ModuleType.BEAKER_HOLDER]: BeakerHolder,
    [ModuleType.SINK]: Sink,
    [ModuleType.FAUCET]: Faucet,
    [ModuleType.COMPOSITION_SCANNER]: CompositionScanner,
    [ModuleType.CONTROL_PANEL]: ControlPanel,
    [ModuleType.DOOR]: Door,
    [ModuleType.WORKBENCH]: Workbench,
    [ModuleType.CLOCK]: Clock,
  };

  /**
   * Shared behavior for a UI element attached to a module (or, for the
   * movement arrows, standalone at the room level). `spriteNames` works
   * exactly as it does for modules (see SpriteOwner) -- most interactables
   * are one flat icon (a 1-element array), but nothing stops one from being
   * layered (Beaker's back/front pair) or animated, the same mechanism
   * either way.
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

    // eslint-disable-next-line no-unused-vars
    onClick(roomState) {
      // Placeholder: concrete interactables override this once their
      // specific action is designed. No-op by default.
    }

    get anchor() {
      const parentAnchor = this.parent !== null ? this.parent.anchor : [0, 0];
      return [parentAnchor[0] + this.offset[0], parentAnchor[1] + this.offset[1]];
    }
  }

  class Button extends InteractableBase {
    static interactableType = InteractableType.BUTTON;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.BUTTON]];
  }

  class Lever extends InteractableBase {
    static interactableType = InteractableType.LEVER;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.LEVER]];
  }

  class Dial extends InteractableBase {
    static interactableType = InteractableType.DIAL;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.DIAL]];
  }

  class LevelIndicator extends InteractableBase {
    static interactableType = InteractableType.LEVEL_INDICATOR;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.LEVEL_INDICATOR]];
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
   * A container's own door/hatch: toggles open/closed and reveals whichever
   * content interactables its owning module attaches afterward via
   * `.contents` (see Workbench). Open/closed are alternative single-sprite
   * states (only one shown at a time), not layers drawn together, which is
   * why this swaps the whole `sprites` array on click rather than using
   * `spriteNames` -- a genuinely different case from Beaker's simultaneous
   * back/front layers, not a parallel implementation of the same thing.
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
    }

    onClick(_roomState) {
      this.open = !this.open;
      this.setSprites([this.open ? this._openSprite : this._closedSprite]);
      for (const item of this.contents) {
        item.visible = this.open;
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

  class MoveArrowLeft extends InteractableBase {
    static interactableType = InteractableType.MOVE_ARROW_LEFT;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.MOVE_ARROW_LEFT]];

    onClick(roomState) {
      roomState.rotate(Direction.LEFT);
    }
  }

  class MoveArrowRight extends InteractableBase {
    static interactableType = InteractableType.MOVE_ARROW_RIGHT;
    static spriteNames = [INTERACTABLE_SPRITES[InteractableType.MOVE_ARROW_RIGHT]];

    onClick(roomState) {
      roomState.rotate(Direction.RIGHT);
    }
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
    [InteractableType.MOVE_ARROW_LEFT]: MoveArrowLeft,
    [InteractableType.MOVE_ARROW_RIGHT]: MoveArrowRight,
  };

  return {
    ModuleBase,
    MODULE_CLASSES,
    InteractableBase,
    Button,
    Lever,
    Dial,
    LevelIndicator,
    Compressor,
    Beaker,
    CabinetDoor,
    PowerPlug,
    MoveArrowLeft,
    MoveArrowRight,
    INTERACTABLE_CLASSES,
  };
})();
