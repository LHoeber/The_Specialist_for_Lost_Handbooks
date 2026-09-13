/**
 * Sprite loading and the type-to-sprite-filename lookup tables. Port of
 * Version_1/src/rendering/assets.py. The one genuinely new pattern here
 * (vs. the Python original): browser image loading is asynchronous, unlike
 * pygame.image.load(), so loadImage() returns a Sprite immediately (mirroring
 * the Python call site, which expects a value back right away) while the
 * actual decode happens in the background -- callers must await
 * Game.Assets.whenAllLoaded() once, after building the room, before the
 * first render.
 *
 * Sprites live in this folder's own assets/ -- a copy of Version_1/assets/,
 * decoupled on purpose (see ../CLAUDE.md, "Assets are now self-contained")
 * so editing sprites for this version can never accidentally touch the
 * frozen Version_1 (Pygame) copy or vice versa.
 */
window.Game = window.Game || {};

Game.Assets = (function () {
  const { ModuleType, InteractableType } = Game.WallLayouts;

  const ASSET_DIR = "assets/";

  /**
   * A loaded image plus whether it was drawn with the top-down-perspective
   * convention (a 6px top-face strip above the front face -- see
   * Config.TOP_FACE_OVERHANG). Set explicitly at load time rather than
   * guessed from pixel size, since a flat icon could coincidentally be
   * sized the same as a headered one.
   */
  class Sprite {
    constructor(image, hasOverhang = false, frames_per_channel = [1], num_channels = 1, seconds_per_frame = 0, frame_width = null, frame_height = null) {
      this.image = image;
      this.hasOverhang = hasOverhang;
      this._offscreenCtx = null; // lazily built the first time alpha is read
      this.frames_per_channel = frames_per_channel;
      this.num_channels = num_channels;
      this.seconds_per_frame = seconds_per_frame;
      this.currentChannel = 0;
      this._frame_width = frame_width;
      this._frame_height = frame_height;
    }

    get width() {
      return this.image.naturalWidth;
    }

    get height() {
      return this.image.naturalHeight;
    }

    // Defaults to the image's own size for sprites that don't specify an
    // explicit frame size (i.e. everything non-animated). Computed lazily
    // via getters rather than on image.onload, since loadImage() sets its
    // own onload (to resolve the load promise) which would otherwise
    // silently clobber a second onload assigned here.
    get frame_width() {
      return this._frame_width ?? this.width;
    }

    get frame_height() {
      return this._frame_height ?? this.height;
    }

    /** Mirrors surface.get_at(local_pos).a > 0 -- alpha-channel hit-test. */
    isOpaqueAt(localX, localY) {
      if (localX < 0 || localY < 0 || localX >= this.width || localY >= this.height) {
        return false;
      }
      if (!this._offscreenCtx) {
        const canvas = document.createElement("canvas");
        canvas.width = this.width;
        canvas.height = this.height;
        this._offscreenCtx = canvas.getContext("2d", { willReadFrequently: true });
        this._offscreenCtx.drawImage(this.image, 0, 0);
      }
      const data = this._offscreenCtx.getImageData(localX, localY, 1, 1).data;
      return data[3] > 0;
    }
  }

  const _pendingLoads = [];

  function loadImage(relativePath, hasOverhang = false, frames_per_channel = [1], num_channels = 1, seconds_per_frame = 0, frame_width = null, frame_height = null) {
    const image = new Image();
    const sprite = new Sprite(image, hasOverhang, frames_per_channel, num_channels, seconds_per_frame, frame_width, frame_height);
    const promise = new Promise((resolve, reject) => {
      image.onload = () => resolve(sprite);
      image.onerror = () => reject(new Error(`Failed to load sprite: ${relativePath}`));
    });
    image.src = ASSET_DIR + relativePath;
    _pendingLoads.push(promise);
    return sprite;
  }


  function whenAllLoaded() {
    return Promise.all(_pendingLoads);
  }

  // One sprite list per module type, in back-to-front draw order. Most
  // modules are a single sprite; a few (Mixer, Flask holder, Dishes) are
  // modeled as a back/front pair so a future mixture-visibility layer can
  // sit between them.
  const MODULE_SPRITES = {
    [ModuleType.FURNACE]: ["devices/furnace.png"],
    [ModuleType.PRESS]: ["devices/press.png"],
    [ModuleType.PRESSURE_TANK]: ["devices/pressure_tank_big.png"],
    [ModuleType.CENTRIFUGE]: ["devices/centrifuge.png"],
    [ModuleType.MIXER]: ["devices/mixer_back.png", "devices/mixer_front.png"],
    [ModuleType.PACKAGING_STATION]: ["devices/packaging_station.png"],
    [ModuleType.FILTER]: ["devices/filter.png"],
    [ModuleType.FUME_HOOD]: ["devices/fume_hood_back.png", { path: "devices/ventilator.png", frames: [10], channels: 1, seconds: 0.08, frame_width: 32, frame_height: 38 }
      , "devices/fume_hood_front.png"],
    [ModuleType.CONNECTOR_BOX]: ["devices/connector_box.png"],
    [ModuleType.FUSE_BOX]: ["devices/fuse_box.png"],
    [ModuleType.GENERATOR]: ["devices/generator.png"],
    [ModuleType.ELECTROLYZER]: ["devices/electrolyzer.png"],
    [ModuleType.FLASK_HOLDER]: ["containers/flask_holder_back.png", "containers/flask_holder_front.png"],
    [ModuleType.DISHES]: ["containers/dish_holder_back.png", "containers/dish_holder_front.png"],
    [ModuleType.BIN]: ["devices/bin.png"],
    [ModuleType.SHELF]: ["furniture/shelf_0.png"],
    [ModuleType.PIPES_WITH_VALVE]: ["devices/pipes_down.png"],
    [ModuleType.PRESSURE_TANK_PIPES]: ["devices/pressure_tank_big_pipes.png"],
    [ModuleType.WIDE_PIPE]: ["devices/wide_pipe.png"],
    [ModuleType.TOOLBOX]: ["devices/toolbox.png"],
    [ModuleType.SINK]: ["devices/sink.png", "devices/sink_front.png"],
    [ModuleType.FAUCET]: ["devices/faucet.png", "devices/faucet_front_off.png",
      { path: "devices/faucet_front_on.png", frames: [4], channels: 1, seconds: 0.1, frame_width: 32, frame_height: 38 }],
    [ModuleType.COMPOSITION_SCANNER]: ["devices/analyzer.png"],
    [ModuleType.CONTROL_PANEL]: ["devices/control_panel_off.png"],
    [ModuleType.DOOR]: ["furniture/door.png"],
    [ModuleType.WORKBENCH]: ["furniture/counter.png"],
    [ModuleType.CLOCK]: ["devices/clock.png",
      { path: "devices/clock_number_0.png", frames: [10], channels: 1, seconds: 1, frame_width: 32, frame_height: 38 },
      { path: "devices/clock_number_1.png", frames: [10], channels: 1, seconds: 10, frame_width: 32, frame_height: 38 },
      { path: "devices/clock_number_2.png", frames: [10], channels: 1, seconds: 60, frame_width: 32, frame_height: 38 },
      { path: "devices/clock_number_3.png", frames: [10], channels: 1, seconds: 600, frame_width: 32, frame_height: 38 },
    ]
  };

  // One default sprite per interactable type. POWER_PLUG is intentionally
  // absent: per docs/design/game-prototype.md it isn't placed on any wall
  // yet and no sprite has been decided for it. MOVE_ARROW_LEFT/RIGHT are
  // gone along with the click-based interface they belonged to (see
  // docs/design/grid-navigation.md) -- wall-to-wall rotation is now a
  // consequence of movement, not a clickable interactable.
  const INTERACTABLE_SPRITES = {
    [InteractableType.LEVER]: "indicators/lever_up.png",
    [InteractableType.DIAL]: "indicators/dial_0.png",
    [InteractableType.COMPRESSOR]: "devices/counter_compressor.png",
    [InteractableType.BEAKER]: ["containers/beaker_back.png", "containers/beaker_front.png"],
  };

  // LevelIndicator cycles through these four sprites (see Objects.LevelIndicator.setLevel).
  const LEVEL_SPRITES = [
    "indicators/levels_off.png",
    "indicators/levels_low.png",
    "indicators/levels_medium.png",
    "indicators/levels_high.png",
  ];

  // Button's 3-sprite flash-then-settle sequence (see Objects.Button.doAction):
  // "do" briefly shows `pressed`, then settles onto (and holds) `on` or `off`.
  const BUTTON_SPRITES = {
    off: "indicators/button_off.png",
    pressed: "indicators/button_pressed.png",
    on: "indicators/button_on.png",
  };

  // Furnace's heat-level overlay, layered onto the module's own base sprite
  // at its anchor tile (see Objects.Furnace) -- distinct from LEVEL_SPRITES,
  // which is the small on-face level icon shown in its sub-grid, not the
  // furnace body itself.
  const FURNACE_HEAT_SPRITES = [
    "devices/furnace_off.png",
    "devices/furnace_low.png",
    "devices/furnace_medium.png",
    "devices/furnace_high.png",
  ];

  const BACKGROUND_SPRITES = {
    wall_tile: "background/wall_tiles.png",
    floor_tile: "background/floor_plate.png",
    icon: "background/icon.png",
  };

  // A Workbench's door has two states rather than one fixed sprite, so it
  // doesn't fit INTERACTABLE_SPRITES above -- see Objects.CabinetDoor.
  // `open` is what's actually drawn on the closeHandle tile once the door
  // swings out to the right; `closed` only ever appears back at the door's
  // own anchor.
  const CABINET_DOOR_SPRITES = {
    closed: "furniture/counter_door_closed.png",
    open: "furniture/counter_door_opened.png",
  };

  return {
    ASSET_DIR,
    Sprite,
    loadImage,
    whenAllLoaded,
    MODULE_SPRITES,
    INTERACTABLE_SPRITES,
    LEVEL_SPRITES,
    BUTTON_SPRITES,
    FURNACE_HEAT_SPRITES,
    BACKGROUND_SPRITES,
    CABINET_DOOR_SPRITES,
  };
})();
