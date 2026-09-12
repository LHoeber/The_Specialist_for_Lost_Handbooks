/**
 * Canvas2D rendering of the currently-viewed wall. Originally a direct port
 * of Version_1/src/rendering/renderer.py; the alpha-channel click
 * hit-testing (`findInteractableAt`/`screenToLogical`) was removed per
 * docs/design/grid-navigation.md when the click interface was replaced by
 * keyboard grid movement -- what's left (`_to_px`, `_sprite_topleft`, draw
 * order, letterbox scaling) is still that same logic.
 */
window.Game = window.Game || {};

Game.Renderer = (function () {

  let gameFrame = 0;
  const {
    GRID_COLS,
    GRID_ROWS,
    MARGIN_COLS,
    CEIL_ROWS,
    FLOOR_ROWS,
    TILE_SIZE,
    TOP_FACE_OVERHANG,
    LOGICAL_WIDTH,
    LOGICAL_HEIGHT,
    MIN_SCALE,
    WINDOW_TITLE,
  } = Game.Config;
  const { BACKGROUND_SPRITES, loadImage } = Game.Assets;

  // The highlight isn't a flat single-alpha outline -- see
  // _strokeHighlightRect: a 3px-wide stroke at OUTER alpha, with a 1px
  // stroke of INNER alpha laid exactly on its center line, so the two only
  // overlap in the middle pixel and read as a slight fade from a dimmer
  // edge to a brighter center.
  const HIGHLIGHT_OUTER_ALPHA = 80;
  const HIGHLIGHT_INNER_ALPHA = 255;

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

      // The position-highlight color -- any [r, g, b] triple, not just
      // white; see _strokeHighlightRect. Light blue by default.
      this.highlightColor = [220, 255, 255];

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
      this._drawSubGridIcons(roomState.currentWall);
      this._drawHighlight(roomState);
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
    // multi-layer/animated drawing path, not two. A playAnimation() in
    // progress overrides the whole owner with a single transient sprite
    // instead (see _advanceAnimation).
    _drawSpriteOwner(owner) {
      const [anchorRow, anchorCol] = owner.anchor;
      const transientSprite = this._advanceAnimation(owner);
      if (transientSprite) {
        this._blitSprite(transientSprite, anchorRow, anchorCol);
        return;
      }
      owner.sprites.forEach((sprite, i) => {
        const offset = owner.spriteOffsets[i];
        this._blitSprite(sprite, anchorRow + offset[0], anchorCol + offset[1]);
      });
    }

    // Resolves a SpriteOwner's playAnimation() sequence (if any) against
    // elapsed wall-clock time: returns the sprite to draw this frame, or
    // null if there's no active sequence (caller falls back to the normal
    // sprites/spriteOffsets layers). A finished, non-looping sequence fires
    // its onFinish callback once and clears itself here -- this is the one
    // place per frame that actually checks elapsed time, same approach as
    // the animated sprite-sheet frame math in _currentFrame.
    _advanceAnimation(owner) {
      const anim = owner._animation;
      if (!anim) return null;
      //iterates over full array, taking initial value and incrementally adding values
      //sum ... ourput that gets carried along each step
      //step... current array value
      //here: adding the individual frame durations together
      const totalDuration = anim.steps.reduce((sum, step) => sum + step.seconds, 0);
      //updating elapsed time based on global time
      let elapsed = performance.now() / 1000 - anim.startedAt;
      //final call once animation is finished
      if (!anim.loop && elapsed >= totalDuration) {
        owner._animation = null;
        if (anim.onFinish) anim.onFinish();
        return null;
      }
      //reset elapsed time if looping is activated
      if (anim.loop && totalDuration > 0) elapsed %= totalDuration;
      let cumulative = 0;
      //check which sprite needs to be shown at the currently elapsed time
      for (const step of anim.steps) {
        cumulative += step.seconds;
        if (elapsed < cumulative) return step.sprite;
      }
      //if not looping, stop at the last sprite and perform on-finish on next run
      return anim.steps[anim.steps.length - 1].sprite;
    }

    _drawModules(wall) {
      // Painted from the bottom row upward (highest row index first) so
      // each module's sprite draws on top of the 6px top-face overhang
      // bleeding up from whatever sits in the row below it.
      // "..." makes shallow copy of walls array before sorting
      //       , repeatedyl compairs pairs until all are ordered
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

    // Sub-grid action-cell icons (e.g. the Furnace's emergency button and
    // heat dial) are real fixtures on the module's face, always visible --
    // not something that only appears once you've entered the sub-grid.
    // Drawn at native size, centered within their fractional subcell rect
    // (see Objects.SubGrid); no stretching/rotation for a first pass.
    _drawSubGridIcons(wall) {
      for (const module of wall.modules) {
        for (const entry of module.subGrids) {
          const [entryRow, entryCol] = [
            module.anchor[0] + entry.offset[0],
            module.anchor[1] + entry.offset[1],
          ];
          const [tileX, tileY] = Renderer.toPx(entryRow, entryCol);
          for (const cell of entry.grid.cells) {
            // check if subcell contains any interactable object
            if (cell.kind !== "action" || !cell.interactable) continue;
            // check if it has an animation that needs to get advanced on interaction
            const sprite = this._advanceAnimation(cell.interactable) ?? cell.interactable.sprites[0];
            if (!sprite) continue;
            const cellX = tileX + cell.rect.col0 * TILE_SIZE;
            const cellY = tileY + cell.rect.row0 * TILE_SIZE;
            const cellW = (cell.rect.col1 - cell.rect.col0) * TILE_SIZE;
            const cellH = (cell.rect.row1 - cell.rect.row0) * TILE_SIZE;
            //upper left anchor of sprite is chosen, so that it gets centered in the sub-area
            this.logicalCtx.drawImage(
              sprite.image,
              cellX + (cellW - sprite.width) / 2,
              cellY + (cellH - sprite.height) / 2
            );
          }
        }
      }
    }

    // Draws the highlight square/rect marking the player's current position
    // (see grid-navigation.md, "Visual feedback"): not a flat single-alpha
    // outline, but a 3px-wide stroke at HIGHLIGHT_OUTER_ALPHA with a 1px
    // stroke of HIGHLIGHT_INNER_ALPHA on its exact center line -- a canvas
    // stroke always centers on the path it's given, so the two land on the
    // same line and only overlap in that middle pixel, reading as a slight
    // fade from a dimmer edge to a brighter center. For a full tile that's
    // effectively three nested rectangles (32/30/28px), without needing a
    // dedicated sprite. `x, y, w, h` are the raw (unshifted) rect -- the
    // +0.5/-1 pixel-grid alignment used by the previous 1px-only version
    // happens once, here, not at each call site.
    _strokeHighlightRect(x, y, w, h) {
      const [r, g, b] = this.highlightColor;
      const cx = x + 0.5;
      const cy = y + 0.5;
      const cw = w - 1;
      const ch = h - 1;
      this.logicalCtx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${HIGHLIGHT_OUTER_ALPHA / 255})`;
      this.logicalCtx.lineWidth = 3;
      this.logicalCtx.strokeRect(cx, cy, cw, ch);
      this.logicalCtx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${HIGHLIGHT_INNER_ALPHA / 255})`;
      this.logicalCtx.lineWidth = 1;
      this.logicalCtx.strokeRect(cx, cy, cw, ch);
    }

    _drawHighlight(roomState) {
      if (roomState.playerSubGrid) {
        const { module, entry, cellIndex } = roomState.playerSubGrid;
        const cell = entry.grid.cells[cellIndex];
        const [entryRow, entryCol] = [
          module.anchor[0] + entry.offset[0],
          module.anchor[1] + entry.offset[1],
        ];
        const [tileX, tileY] = Renderer.toPx(entryRow, entryCol);
        const x = tileX + cell.rect.col0 * TILE_SIZE;
        const y = tileY + cell.rect.row0 * TILE_SIZE;
        const w = (cell.rect.col1 - cell.rect.col0) * TILE_SIZE;
        const h = (cell.rect.row1 - cell.rect.row0) * TILE_SIZE;
        this._strokeHighlightRect(x, y, w, h);
      } else {
        const [row, col] = roomState.playerPosition;
        // toPx's uniform 32px-per-row/column formula only works for the
        // "normal" row/column range -- the ceiling/left-margin sit *before*
        // row/col 0 as half-size bands, so their naive toPx position lands
        // 16px outside their actual visible strip (unlike the floor/
        // right-margin, whose naive position coincidentally already lands
        // on their own strip). So the two outer bands on each axis need
        // their own extent, computed independently of one another.
        let y, h;
        if (row === -1) {
          y = 0;
          h = CEIL_ROWS * TILE_SIZE;
        } else if (row === GRID_ROWS) {
          y = (GRID_ROWS + CEIL_ROWS) * TILE_SIZE;
          h = FLOOR_ROWS * TILE_SIZE;
        } else {
          [, y] = Renderer.toPx(row, col);
          h = TILE_SIZE;
        }
        let x, w;
        if (col === -1) {
          x = 0;
          w = MARGIN_COLS * TILE_SIZE;
        } else if (col === GRID_COLS) {
          x = (GRID_COLS + MARGIN_COLS) * TILE_SIZE;
          w = MARGIN_COLS * TILE_SIZE;
        } else {
          [x] = Renderer.toPx(row, col);
          w = TILE_SIZE;
        }
        this._strokeHighlightRect(x, y, w, h);
      }
    }

    _fitRect() {
      //actual size of window; can be manually changed
      const windowW = this.canvas.width;
      const windowH = this.canvas.height;
      //checking which dimension is squeezed more by manual sizing
      let scale = Math.min(windowW / LOGICAL_WIDTH, windowH / LOGICAL_HEIGHT);
      scale = Math.max(scale, MIN_SCALE);
      //scaling wanted width/height by smallest squeezed scale
      //i.e. getting maximum possible size under current constraints, without loosing ration of h/w
      const drawW = Math.max(1, Math.round(LOGICAL_WIDTH * scale));
      const drawH = Math.max(1, Math.round(LOGICAL_HEIGHT * scale));
      //checking how much to fill in on sides or above/below to fill out the full manually sized window
      const offsetX = Math.floor((windowW - drawW) / 2);
      const offsetY = Math.floor((windowH - drawH) / 2);
      //offset needed to center the resized game image
      return { offsetX, offsetY, drawW, drawH, scale };
    }

    _blitToWindow() {
      // add additional black fill-in if the tab in which window is opened doesn't equal the size of the window
      const { offsetX, offsetY, drawW, drawH } = this._fitRect();
      this.ctx.fillStyle = "black";
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      // Nearest-neighbor only -- smoothing would blur the pixel art.
      this.ctx.imageSmoothingEnabled = false;
      //draw actual image in the middle of the black placeholder/filler screen
      this.ctx.drawImage(
        this.logicalCanvas,
        0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT,
        offsetX, offsetY, drawW, drawH
      );
    }

    handleResize() {
      this._resizeCanvasToWindow();
    }
  }

  gameFrame++;
  return { Renderer };
})();
