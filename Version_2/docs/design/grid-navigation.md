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

## General mechanic

### Room-level grid

- The player has exactly one current position, `(row, column)`, on the
  currently-viewed wall's grid at all times.
- The navigable grid extends beyond the existing 3×4 module grid
  (`GRID_ROWS`/`GRID_COLS` in `config.js`) to include the floor and
  ceiling half-rows (`FLOOR_ROWS`/`CEIL_ROWS`) — every cell, including
  those half-height strips, is a navigable position, even though "do"
  does nothing there yet. This is deliberate: it keeps the whole space
  addressable now so content can be added later without changing the
  navigation model.
- Movement: up/down/left/right between adjacent cells. Key bindings
  aren't specified here — pick something sensible (e.g. arrow keys +
  space/enter for "do") and note the choice where you bind it.
- "do": performs whatever unambiguous action is defined for the player's
  current position. If nothing is defined there (an empty tile, or a
  module whose action isn't built yet), it's a silent no-op — this
  matches the project's existing "never pre-filter legal actions, let the
  environment resolve outcome" stance (also in the Notion Controls
  section) — don't build a legality check that hides the option instead.

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

## Explicitly out of scope for this pass

- Flask in/out and door open/close for the Furnace — no tile assigned,
  don't design placement for them yet.
- Whether wall-to-wall rotation (currently the click-based
  `MoveArrowLeft`/`MoveArrowRight` interactables) gets folded into this
  same grid+do model (e.g. moving off the grid's left/right edge triggers
  rotation) is undecided. Leave the existing arrow-click mechanic as-is;
  don't merge the two systems in this pass.
- Whether the existing mouse-click hit-testing in `rendering/ui.js` is
  removed, disabled, or kept alongside the new keyboard-driven system is
  left to your judgment here — the new system needs to work standalone
  since it's what's being demoed, but fully retiring the old one isn't
  required to satisfy this task.

## Where this fits in the existing code

- `Furnace` in `environment/objects.js` currently constructs a single
  legacy `new Dial([1.0, 0.5], this)`. That offset predates this spec and
  belongs to the old click-based model — replace it with the sub-grid
  definition above rather than keeping both.
- This is new state layered on top of `RoomState`/`Wall`
  (`environment/state.js`) — expect to add the player's current grid
  position and current sub-grid-or-null somewhere in that vicinity.
- The highlight square is new rendering, alongside the existing draw
  calls in `rendering/renderer.js`.
- `environment/rules.js` is still the empty placeholder it's always been.
  The heat-level cycling and the button's cosmetic toggle are exactly the
  kind of "module behavior" that file exists for, per `Version_2/CLAUDE.md`'s
  own "Going forward" section.
