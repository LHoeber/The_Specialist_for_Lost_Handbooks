# Grid-based navigation + "do": new interaction model

Captured from a Cowork conversation (2026-09-11) that worked out how to
discretize player/agent controls for a valid human/agent comparison, then
worked through the furnace as the first concrete module built on it. This
is genuinely new infrastructure, not a tweak to something that exists:
nothing about a player position, keyboard movement, or a generic "do"
action exists anywhere in this codebase yet. `rendering/ui.js` today is
pure mouse click + alpha-channel hit-testing (`find_interactable_at`); no
grid-position state, no keyboard handling.

## Why this exists

The click-anywhere interface (mouse click, or click+hold+drag+release)
that Version_1/Version_2 have always used doesn't give a human and an
artificial agent an equal, enumerable action space — clicking anywhere in
a rendered frame is effectively infinite/pixel-scale, requires an agent to
solve object recognition before it can act at all, and can't be "fully
specified" the way the project's POMDP-comparison goal needs. The Notion
"Game Prototype" page's **Controls** section has the full comparison of
three candidate approaches (free-form click; discrete grid + single "do";
discrete grid + hierarchical "do") with pros/cons for each — read that for
the reasoning if you want it. The decision made there: **discrete grid +
hierarchical "do"** (approach 3) is what gets built. This doc is the
concrete mechanic spec plus the first worked example (the Furnace); the
Notion page is the design rationale, this file is the build spec.

## Mouse click is being removed entirely, not kept alongside this (2026-09-11)

Decided after the first version of this doc: the free click-anywhere
interface doesn't just lose the human/agent-parity argument, it's also a
worse fit for the actual research comparison than it looked — clicking
lets you jump straight to any point on screen, which is further from the
VR exploration paradigm this game is meant to be a controlled, discrete
analog of (see the RTG-meeting context handoff and the LeWorldModel notes
in the Claude project) than it first appeared. In VR you can't teleport
either — you move continuously through adjacent space, and where you're
looking/heading is itself part of what's being measured (attention,
approach behavior). Grid movement is a closer discrete stand-in for that
than a mouse click ever was, not just a compromise for agent-compatibility.

So: **`rendering/ui.js`'s click listener, `renderer.js`'s alpha-channel
hit-testing (`find_interactable_at`), and the `MoveArrowLeft`/
`MoveArrowRight` interactables (and their `ROOM_INTERACTABLES` placements
in `wall_layouts.js`) should be removed outright on this branch**, not
left in place unused and not kept as a fallback input method. The
pre-this-change version is preserved on the `Click_Control` git branch
specifically so this branch is free to delete rather than special-case
around it. If `screen_to_logical`/coordinate-scaling code in `renderer.js`
is still needed for anything else (e.g. resizing), keep only that part.

## General mechanic

### Room-level grid

- The player has exactly one current position, `(row, column)`, on the
  currently-viewed wall's grid at all times. **Starting position on load**
  isn't otherwise constrained by anything designed so far — `[1, 0]` on
  wall 0 (middle row, leftmost module column) is a reasonable arbitrary
  default; change it freely if a different starting point reads better
  once it's running.
- The navigable grid extends beyond the existing 3×4 module grid
  (`GRID_ROWS`/`GRID_COLS` in `config.js`) to include the floor and
  ceiling half-rows (`FLOOR_ROWS`/`CEIL_ROWS`) — every cell, including
  those half-height strips, is a navigable position, even though "do"
  does nothing there yet. This is deliberate: it keeps the whole space
  addressable now so content can be added later without changing the
  navigation model.
- Movement: up/down/left/right between adjacent cells, bound to **both**
  the arrow keys and WASD simultaneously (either works interchangeably at
  any time, not a mode the player switches between). "do" is bound to
  **space**.
- Vertical movement has no analog to wall rotation: at the top edge
  (ceiling row) or bottom edge (floor row), moving further up/down is
  simply a no-op — you stay put. Only horizontal movement wraps (see
  "Wall-to-wall rotation" below).
- "do": performs whatever unambiguous action is defined for the player's
  current position. If nothing is defined there (an empty tile, or a
  module whose action isn't built yet), it's a silent no-op — this
  matches the project's existing "never pre-filter legal actions, let the
  environment resolve outcome" stance (also in the Notion Controls
  section) — don't build a legality check that hides the option instead.

### Wall-to-wall rotation (replaces the click-based arrows entirely)

The `MoveArrowLeft`/`MoveArrowRight` interactables are removed, not
repositioned into a do-triggered cell — rotation is a consequence of
movement itself, not a separate action:

- Moving left/right normally, within columns 0..3 (`GRID_COLS - 1`), just
  moves the player one column as usual — reaching column 0 or column 3
  is not itself special, it's a normal position.
- Rotation triggers only on the *next* move past that edge: pressing left
  again while already at column 0, or right again while already at
  column 3, switches `currentWallIndex` (reusing `RoomState.rotate()`'s
  existing step-and-modulo logic in `state.js`) and re-renders the new
  wall — a genuine two-step motion (move to the edge, then move again),
  not an instant trigger from merely arriving at the edge column.
- **Landing position after rotating**: the opposite edge column, same
  row — rotating right lands you at column 0 of the new wall; rotating
  left lands you at column 3 of the new wall; the row is unchanged
  either way. This is deliberate continuity ("walked around the corner"),
  not a reset to a fixed spawn point.
- This applies uniformly across every row, including the floor/ceiling
  half-rows — no special-casing by row.

### Modules without sub-functions

Unchanged in spirit from a module's current `onClick`: "do" at that
module's tile executes its one action immediately once an action is
defined. Most modules don't have one defined yet (see `objects.js` —
almost every `onClick` is still the `InteractableBase` no-op), which is
fine and expected; leave those as no-ops rather than inventing behavior.

### Modules with sub-functions (sub-grid)

A module "opts in" to a sub-grid explicitly — most modules don't have one
(and shouldn't yet). For a module that does:

- **The sub-grid always lives inside exactly one 32×32 tile**, even for a
  module whose visual footprint spans more than one tile. For a
  multi-tile module, only that one designated tile responds to "do" to
  enter the sub-grid — the module's other occupied tiles have no
  interactive behavior defined yet (not an oversight; those actions
  haven't been designed, see the Furnace example below).
- That tile's sub-grid subdivides it into subcells via discrete
  rectangular sectioning — uniform (2×2, 3×1, 1×2, ...) or mixed, as long
  as the subcells exactly tile the 32×32 square with no gaps or overlaps.
- **Every sub-grid has exactly one designated "exit" subcell**, kept free
  of any functional interactable. Entering the module (pressing "do" on
  its interactive tile from room-level) always lands here first.
  Pressing "do" while positioned on this cell exits back to room-level —
  this is purely positional (true any time you're standing on it,
  whether you just entered or wandered back to it later), not a one-shot
  action available only immediately after entry.
- Executing any other subcell (pressing "do" on it) performs that one
  unambiguous action, then automatically returns the player to
  room-level, positioned back on the module's tile. You never remain
  inside a sub-grid after executing — you either exit deliberately, or
  execute-and-auto-exit. There's no third state.
- **Navigation ambiguity defaults**: movement between subcells follows
  whatever adjacency the shape allows (e.g. a 1×3 row only allows
  left/right). When a move direction has more than one geometrically
  valid target — moving toward (or away from) a cell that spans multiple
  rows or columns — resolve it with a fixed default: a horizontal move
  (left/right) into an ambiguous multi-row target defaults to the **lower**
  row; a vertical move (up/down) into an ambiguous multi-column target
  defaults to the **leftmost** column. These are the only two ambiguity
  shapes possible under rectangular sectioning, so no other case needs a
  rule.

### Keep movement/do as a shared, input-agnostic function

This redesign exists specifically so a human and an artificial agent can
eventually act through the same interface (see "Why this exists" above)
— that only holds if the actual game logic isn't entangled with the
keyboard listener itself. Structure this as a small dispatch function
(e.g. `performAction(direction | "do")`) that mutates player/room state
and triggers a re-render, with the keyboard event handler doing nothing
but translating a keypress into a call to that function. A future
scripted agent should be able to drive the exact same function directly,
without touching the DOM at all — if that's not true of whatever gets
built here, the human/agent parity this mechanic exists for hasn't
actually been achieved.

### Visual feedback

A white square highlights the player's current position at all times —
drawn around the full tile at room-level, or around the current subcell
when inside a sub-grid. This applies to every navigable cell, including
plain floor/ceiling tiles with no module on them — it's general position
feedback, not something reserved for interactive modules.

## Worked example: Furnace

The Furnace is the first module built against this mechanic, chosen
because its existing 2×2 footprint (Wall 3 / `WALL_3_DEVICES`, anchor
`[1, 2]` in `wall_layouts.js`) gives enough room for a real sub-grid with
more than one interactable.

**Footprint** (rows are `[1, 2]`, columns are `[2, 3]`):

| | col 2 | col 3 |
|---|---|---|
| **row 1** | top-left `[1,2]` — heat-level indicator (see below) | top-right `[1,3]` — **the interactive tile**, hosts the sub-grid below |
| **row 2** | bottom-left `[2,2]` — no behavior yet | bottom-right `[2,3]` — no behavior yet |

Only `[1,3]` responds to "do" to enter the sub-grid. The other three
tiles (including the top-left one, which only *displays* the heat-level
sprite) have no "do" behavior defined yet — flask in/out and door
open/close still need a home somewhere in this footprint, but that's a
future iteration, not this one. Don't invent a placement for them.

**Sub-grid inside tile `[1,3]`** (described as row/column fractions 0–1
within that one 32×32 tile):

| Subcell | Extent (row × col, as fractions of the tile) | Contents |
|---|---|---|
| Emergency button | rows `[0, 0.5)`, cols `[0, 0.5)` — top-left quadrant | Toggle. "do" flips pressed/unpressed (bright/dark). Cosmetic only for now — eventually intended to gate a heater shutoff for fuel replacement, not built yet. Likely sprites `button_off.png` / `button_pressed.png` (already in `assets/indicators/`) — confirm against the actual art rather than assuming the mapping; `button_on.png` also exists and is probably unrelated to this toggle. |
| Exit / entry | rows `[0.5, 1)`, cols `[0, 0.5)` — bottom-left quadrant | Free of interactables. Landing point on entry; "do" here exits to room-level (see the general "exit" rule above). |
| Heat dial/selector | rows `[0, 1)`, cols `[0.5, 1)` — right half, full height, spans both rows | "do" advances the heat level **with wraparound**: off → low → medium → high → off → ... Each press updates the heat-level sprite shown on tile `[1,2]` (top-left of the furnace's footprint) — likely a `LevelIndicator`-style interactable, reusing the existing class/convention already used by `PressureTank`/`Mixer` in `objects.js`. `assets/indicators/levels_off.png` / `levels_low.png` / `levels_medium.png` / `levels_high.png` already exist and look purpose-built for exactly these 4 states. |

**Navigation graph inside this sub-grid**: from the exit, `up` → button,
`right` → dial (unambiguous — the dial spans both rows, so it's the only
thing to the right regardless of which row you're in). From the button,
`down` → exit, `right` → dial. From the dial, `left` is the ambiguous
case (both button and exit are valid horizontal targets) → resolves to
the lower option → exit. **The button is therefore only reachable via the
exit cell, not directly from the dial** — a direct, intended consequence
of the "prefer lower" default, not a gap to fix.

## Existing behavior carried over: Workbench cabinet door

The Workbench's door predates this whole mechanic (it already works via
click today) and stays exactly as designed — it's simpler than the
Furnace: no sub-grid, just two ordinary room-level tiles whose "do"
behavior depends on the door's current state, not a location you enter:

- **Closed** (default): "do" at the Workbench's own anchor tile opens it.
- **Open**: the door sprite swings out far enough to visually cover the
  tile immediately to its right (anchor `+ [0, 1]`) — already handled on
  the rendering side (the open-door sprite blits there instead of at the
  anchor; see the sprite change made earlier this session). The
  *interactive* surface moves with it: "do" now closes the door only
  from that right-hand tile — "do" at the anchor tile while open is a
  no-op, not a second way to close it.
- Revealed contents (the Beaker in Wall 0's Workbench at `[2,3]`, the
  Compressor in Wall 3's at `[2,0]`) become visible at the anchor tile
  once open, same as today, but per "explicitly out of scope" below
  they're not interactively reachable via "do" yet — standing there and
  pressing "do" is a no-op for now, not an error.

**Check before implementing**: `wall_layouts.js` places three Workbenches
in a row on Wall 2 — `[2,0]`, `[2,1]`, `[2,2]` — so opening the one at
`[2,0]` would visually cover `[2,1]`, which is itself a Workbench with
its own door. This wasn't addressed when the doors were originally
designed (a floating click never forced the conflict into view); confirm
with Laura whether overlapping doors there is fine or needs a different
rule for adjacent Workbenches, rather than guessing.

## Explicitly out of scope for this pass

- Flask in/out and door open/close for the Furnace — no tile assigned,
  don't design placement for them yet.
- The Workbench's revealed contents (once its door is open) aren't
  interactively reachable via "do" in this pass — see "Existing behavior
  carried over: Workbench cabinet door" above for exactly what *is* in
  scope for the door itself.
- The Orientation section's second point ("you can only see one side of a
  machine and walk around it discretely between all 4") is a *different*
  mechanic from the Furnace's sub-grid built above — that one is about
  circling an individual machine to see its other faces, and nothing in
  this pass builds it. Don't conflate the two: the Furnace's sub-grid is
  entered from one fixed face, not walked around.

## Where this fits in the existing code

- `Furnace` in `environment/objects.js` currently constructs a single
  legacy `new Dial([1.0, 0.5], this)`. That offset predates this spec and
  belongs to the old click-based model — replace it with the sub-grid
  definition above rather than keeping both.
- `MoveArrowLeft`/`MoveArrowRight` (in `objects.js`'s `INTERACTABLE_CLASSES`
  and `wall_layouts.js`'s `ROOM_INTERACTABLES`) are removed, not just
  unused — rotation is now a consequence of movement past the grid edge
  (see "Wall-to-wall rotation" above), not a separate clickable
  interactable. `RoomState.rotate()` in `state.js` still does the actual
  wall-index switching; only what calls it changes.
- `rendering/ui.js`'s click listener and `renderer.js`'s alpha-channel
  hit-test (`find_interactable_at`) are removed, per "Mouse click is
  being removed entirely" above — replaced by the keyboard-driven
  dispatch function described under "Keep movement/do as a shared,
  input-agnostic function".
- `CabinetDoor.onClick` in `objects.js` currently doesn't care where it
  was triggered from — one click anywhere on its sprite always just
  toggles `this.open`. Under "do", it needs to become position-aware (see
  "Existing behavior carried over: Workbench cabinet door" above): open
  only fires from the anchor tile, close only fires from `anchor + [0,1]`
  — this is new logic, not a straight port of the existing method.
- This is new state layered on top of `RoomState`/`Wall`
  (`environment/state.js`) — expect to add the player's current grid
  position and current sub-grid-or-null somewhere in that vicinity.
- The highlight square is new rendering, alongside the existing draw
  calls in `rendering/renderer.js`.
- `environment/rules.js` is still the empty placeholder it's always been.
  The heat-level cycling and the button's cosmetic toggle are exactly the
  kind of "module behavior" that file exists for, per `Version_2/CLAUDE.md`'s
  own "Going forward" section.
