/**
 * Canvas2D rendering of the currently-viewed wall. Direct port of
 * Version_1/src/rendering/renderer.py, reusing the exact same algorithms
 * (_to_px, _sprite_topleft, draw order, letterbox scaling, hit-testing) --
 * see that file's comments for the reasoning behind each one.
 */
window.Game = window.Game || {};

Game.Renderer = (function () {

  let gameFrame = 0;
  const {
    GRID_COLS,
    GRID_ROWS,
    MARGIN_COLS,
    CEIL_ROWS,
    TILE_SIZE,
    TOP_FACE_OVERHANG,
    LOGICAL_WIDTH,
    LOGICAL_HEIGHT,
    MIN_SCALE,
    WINDOW_TITLE,
  } = Game.Config;
  const { BACKGROUND_SPRITES, loadImage } = Game.Assets;

  class Renderer {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");

      document.title = WINDOW_TITLE;

      // Offscreen logical-resolution surface; the real canvas only ever
      // receives a scaled, letterboxed blit of this (see _blitToWindow).
      this.logicalCanvas = document.createElement("canvas");
      this.logicalCanvas.width = LOGICAL_WIDTH;
      this.logicalCanvas.height = LOGICAL_HEIGHT;
      this.logicalCtx = this.logicalCanvas.getContext("2d");

      this.wallTile = loadImage(BACKGROUND_SPRITES.wall_tile);
      // hasOverhang: true -- the floor's near edge overlaps 6px up into the
      // last module row on purpose, so modules read as standing on a sliver
      // of visible floor instead of floating flush against a hard seam.
      this.floorTile = loadImage(BACKGROUND_SPRITES.floor_tile, true);

      this._resizeCanvasToWindow();
    }

    _resizeCanvasToWindow() {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
      // Resizing a canvas resets its context state, including smoothing.
      this.ctx.imageSmoothingEnabled = false; // nearest-neighbor only -- smoothing would blur the pixel art
    }

    render(roomState) {
      this._drawBackground();
      this._drawModules(roomState.currentWall);
      this._drawInteractables(roomState.currentWall.interactables);
      this._drawInteractables(roomState.roomInteractables);
      this._blitToWindow();
    }

    /**
     * Grid [row, column] -> logical pixel top-left, shifted by the room's
     * top/left margin. Used for everything (background, modules,
     * interactables) so margins apply uniformly.
     */
    static toPx(row, col) {
      return [(col + MARGIN_COLS) * TILE_SIZE, (row + CEIL_ROWS) * TILE_SIZE];
    }

    /**
     * Grid position -> pixel top-left for blitting/hit-testing a given
     * sprite: shifts up by TOP_FACE_OVERHANG when that sprite actually
     * carries the top-face strip (see assets.Sprite.hasOverhang), and not
     * otherwise. Every sprite draw/hit-test goes through this so the two
     * can never drift apart.
     */
    static spriteTopLeft(sprite, row, col) {
      const [x, y] = Renderer.toPx(row, col);
      return [x, y - (sprite.hasOverhang ? TOP_FACE_OVERHANG : 0)];
    }

    _blitSprite(sprite, row, col) {
      const [x, y] = Renderer.spriteTopLeft(sprite, row, col);
      const [sx, sy, sw, sh] = this._currentFrame(sprite);
      this.logicalCtx.drawImage(sprite.image, sx, sy, sw, sh, x, y, sw, sh);
    }

    _currentFrame(sprite) {
      let secondsPassed = performance.now() / 1000;
      let frameNumber = 0
      if (sprite.seconds_per_frame > 0) {
        frameNumber = Math.floor(secondsPassed / sprite.seconds_per_frame) % sprite.frames_per_channel[sprite.currentChannel % sprite.num_channels];
      }
      let x_offset = frameNumber * sprite.frame_width;
      let y_offset = sprite.currentChannel * sprite.frame_height;

      return [x_offset, y_offset, sprite.frame_width, sprite.frame_height];

    }


    _drawBackground() {
      // Overdraw one tile into the margins on every side (they're only
      // half a tile wide, so a full tile there simply bleeds harmlessly
      // into the grid or past the window edge, both of which get clipped
      // or redrawn over anyway).
      for (let row = -1; row < GRID_ROWS; row++) {
        for (let col = -1; col <= GRID_COLS; col++) {
          this._blitSprite(this.wallTile, row, col);
        }
      }
      for (let col = -1; col <= GRID_COLS; col++) {
        this._blitSprite(this.floorTile, GRID_ROWS, col);
      }
    }

    // Draws every sprite layer of one SpriteOwner (a module or an
    // interactable -- both have the same `sprites`/`spriteOffsets`/`anchor`
    // shape, see Objects.SpriteOwner) at its anchor plus each layer's own
    // offset. Shared by _drawModules and _drawInteractables so there's one
    // multi-layer/animated drawing path, not two.
    _drawSpriteOwner(owner) {
      const [anchorRow, anchorCol] = owner.anchor;
      owner.sprites.forEach((sprite, i) => {
        const offset = owner.spriteOffsets[i];
        this._blitSprite(sprite, anchorRow + offset[0], anchorCol + offset[1]);
      });
    }

    _drawModules(wall) {
      // Painted from the bottom row upward (highest row index first) so
      // each module's sprite draws on top of the 6px top-face overhang
      // bleeding up from whatever sits in the row below it.
      const modules = [...wall.modules].sort((a, b) => b.anchor[0] - a.anchor[0]);
      for (const module of modules) {
        this._drawSpriteOwner(module);
      }
    }

    _drawInteractables(interactables) {
      for (const interactable of interactables) {
        if (!interactable.visible || interactable.sprites.length === 0) continue;
        this._drawSpriteOwner(interactable);
      }
    }

    _fitRect() {
      const windowW = this.canvas.width;
      const windowH = this.canvas.height;
      let scale = Math.min(windowW / LOGICAL_WIDTH, windowH / LOGICAL_HEIGHT);
      scale = Math.max(scale, MIN_SCALE);
      const drawW = Math.max(1, Math.round(LOGICAL_WIDTH * scale));
      const drawH = Math.max(1, Math.round(LOGICAL_HEIGHT * scale));
      const offsetX = Math.floor((windowW - drawW) / 2);
      const offsetY = Math.floor((windowH - drawH) / 2);
      return { offsetX, offsetY, drawW, drawH, scale };
    }

    _blitToWindow() {
      const { offsetX, offsetY, drawW, drawH } = this._fitRect();
      this.ctx.fillStyle = "black";
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      // Nearest-neighbor only -- smoothing would blur the pixel art.
      this.ctx.imageSmoothingEnabled = false;
      this.ctx.drawImage(
        this.logicalCanvas,
        0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT,
        offsetX, offsetY, drawW, drawH
      );
    }

    handleResize() {
      this._resizeCanvasToWindow();
    }

    screenToLogical(x, y) {
      const { offsetX, offsetY, scale } = this._fitRect();
      const logicalX = (x - offsetX) / scale;
      const logicalY = (y - offsetY) / scale;
      if (logicalX >= 0 && logicalX < LOGICAL_WIDTH && logicalY >= 0 && logicalY < LOGICAL_HEIGHT) {
        return [logicalX, logicalY];
      }
      return null;
    }

    /**
     * Only currently-rendered interactables are clickable, and only their
     * non-transparent pixels count as a hit.
     */
    findInteractableAt(logicalPos, roomState) {
      if (logicalPos === null) return null;

      const candidates = [...roomState.roomInteractables, ...roomState.currentWall.interactables];
      for (const interactable of candidates) {
        if (!interactable.visible || interactable.sprites.length === 0) continue;
        // Hit-test against the first (canonical) layer -- same convention
        // widthCells/heightCells use for sizing (see Objects.SpriteOwner).
        const sprite = interactable.sprites[0];
        const spriteOffset = interactable.spriteOffsets[0];
        const [x, y] = Renderer.spriteTopLeft(
          sprite, interactable.anchor[0] + spriteOffset[0], interactable.anchor[1] + spriteOffset[1]
        );
        const [lx, ly] = logicalPos;
        if (lx >= x && lx < x + sprite.width && ly >= y && ly < y + sprite.height) {
          const localX = Math.floor(lx - x);
          const localY = Math.floor(ly - y);
          if (sprite.isOpaqueAt(localX, localY)) return interactable;
        }
      }
      return null;
    }
  }

  gameFrame++;
  return { Renderer };
})();
