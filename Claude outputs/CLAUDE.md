# Version_1_web — porting Version_1 (Pygame) to a browser-deployable game

This file is the bridge between the deployment-strategy discussion in Laura's
Cowork/Claude.ai conversation (2026-09-04) and this folder. Read it fully
before writing any code here — it explains *why* this port has to work the
way it does, not just what to build. `../Version_1/CLAUDE.md` remains the
source of truth for the game's research design; this file is only about
getting that same game running in a browser.

## Why this folder exists

`../Version_1/` is a working Pygame prototype: full room rendering across
four walls, correct sprite layering (the 6px top-face overhang), window
resize handling, pixel-alpha hit-testing, and a real module/interactable
class hierarchy. It is not deployable to participants as-is. The plan is to
recruit participants online (Prolific / Mechanical Turk) to get enough data
across ages and conditions, and both platforms work by sending a participant
to a URL that runs entirely in their browser — no install, no local Python.
Pygame is built on SDL, a desktop library; it does not run in a browser
without a nonstandard compile step (see "Rejected options" below), so
Version_1 as it stands cannot be the shipped experiment.

## Rejected options, and why (don't re-litigate these without new information)

- **pygbag** (compiles Pygame to WebAssembly): technically real and would
  need only a small, mechanical change to `main.py`'s loop (wrap it in
  `async def`, add `await asyncio.sleep(0)`, call via `asyncio.run(...)`).
  Rejected as the *deployment* target because pygbag's own documentation
  describes it as an experimental test tool, not built with production or
  data-integrity guarantees — not something to trust with real thesis data
  collection. It stays a legitimate option only for a fast, throwaway demo
  link if one is ever wanted (e.g. to show Maik or a TAC member), not for
  anything that touches real participant data.
- **PsychoJS** (PsychoPy's web export via Pavlovia): rejected because
  PsychoJS's main benefit — write once in Python, get the web version free —
  only applies to PsychoPy's *built-in* components (text, image, keyboard
  response). Version_1's entire game is bespoke canvas-style rendering and
  hit-testing (see `renderer.py`'s `_to_px`, `_sprite_topleft`,
  `find_interactable_at`), none of which PsychoJS can auto-translate. Using
  it would mean hand-writing the same JavaScript anyway, while also
  maintaining a parallel Python copy of that same logic in a PsychoPy code
  component — a real maintenance tax for zero benefit given how custom this
  game is.
- **Gorilla** (gorilla.sc): a real, well-integrated alternative — free to
  build, pay-per-participant (~£1.09/participant academic rate), with a
  documented native Prolific integration (automatic participant-ID capture,
  completion redirects, consent/screener automation). Not chosen as the
  primary path because it still requires the actual game to live inside one
  custom HTML/JS "Zone" — same fundamental situation as jsPsych, just paired
  with a paid recruitment layer instead of a free one. Worth revisiting if
  the Sinz lab or the RTG already holds an institutional license — check
  before ruling it out on cost alone.
- **GDevelop**: the best architectural fit for the actual game specifically
  — free, open-source, no-code 2D engine with native HTML5 export, and a
  genuine game engine rather than a trial-sequence tool, so the room/module/
  history structure would sit naturally in it. Not chosen because it has
  zero built-in research-specific plumbing (no Prolific integration, no
  established academic timing/logging precedent) — all of that would be
  fully DIY, unlike jsPsych's ecosystem.
- **Unity/WebGL**: technically deployable in a browser, but rejected for
  *this* artifact specifically — WebGL builds are large and slow to load
  (a real dropout risk on Prolific, where participants expect near-instant
  start), cross-browser/mobile support is more variable than HTML5-native
  options, and Unity is a heavyweight 3D-first tool for what is fundamentally
  a 2D room-and-sprites game. Unity remains the sensible choice for the
  separate VR arm of the PhD project — this rejection is about the 2D game
  only.

## Rendering architecture: DOM elements, not `<canvas>`

Version_1_web renders the room as absolutely-positioned `<img>` elements
inside a container `<div>`, not as pixels drawn into a `<canvas>`. Both are
legitimate ways to do 2D graphics in a browser — canvas is a blank bitmap
you draw into with imperative calls (`ctx.drawImage(...)`), the closest
sibling to what Pygame already does, since `logical_surface` is basically a
canvas and `renderer.py`'s blits map almost directly onto `drawImage`. DOM
means building the scene from positioned, styled elements instead
(`position: absolute`, `top`/`left`, `z-index`).

DOM was chosen for this specific game because it's a static room of
discretely positioned, individually clickable sprites with no continuous
animation — exactly the case DOM is a natural fit for — and it comes with a
concrete win that matters given how much debuggability mattered for the
Pygame build: DOM elements are inspectable directly in browser dev tools
(right-click → inspect shows exactly where each sprite sits and why), where
a canvas is just pixels with no separate structure to inspect. CSS also
gives `image-rendering: pixelated` as a one-line replacement for Pygame's
"no smoothscaling" rule, and native browser click events remove some
hand-rolled input-handling code.

DOM does **not**, however, remove the two trickiest pieces of this port —
don't assume either comes for granted just from picking DOM over canvas:

- **Alpha-channel hit-testing.** A DOM `<img>`'s clickable area is its
  rectangular bounding box by default — same problem a naive canvas hit-test
  would have. The "only non-transparent pixels count as a click" rule
  (`find_interactable_at`'s `surface.get_at(local_pos).a > 0`) still needs a
  small helper: draw each sprite once into an offscreen canvas at load time,
  then read `ctx.getImageData(x, y, 1, 1).data[3] > 0` at click time.
- **Coordinate math and the overhang layering rule.** `_to_px` and
  `_sprite_topleft` still need to exist and run identically for both
  rendering and hit-testing; they just end up setting `style.top`/
  `style.left` (and `style.zIndex` for draw order) instead of calling
  `drawImage`.

## JS file structure: classic multi-file scripts, not ES6 modules

Each `../Version_1/src/` file gets one corresponding `.js` file here
(`config.js`, `wallLayouts.js`, `objects.js`, `assets.js`, `renderer.js`,
`ui.js`, `main.js`), loaded via plain `<script src="...">` tags in
`index.html`, in dependency order — **not** `<script type="module">` with
`import`/`export`. Each file attaches what it exports to one shared
namespace object instead (`window.Game = window.Game || {}; Game.TILE_SIZE
= 32;`), so nothing collides as a bare global.

This is a real constraint, not a style preference: ES6 modules are fetched
via a CORS-checked request, and browsers refuse that fetch from a
`file://` page's `null` origin — so `import`/`export` between these files
would throw a CORS error and nothing would run. Classic `<script>` tags
don't go through that fetch-and-check path, so the *script-loading* half of
this problem doesn't need a server. A single bundled file would also dodge
it, but erases the clean one-Python-file-to-one-JS-file mapping that makes
this port mechanical — that's a reasonable *shipping* format once wrapping
into a jsPsych plugin later, not the format to port in.

This does **not**, on its own, mean the app runs with no server at all —
see "Debugging workflow" below for a second, unrelated `file://` restriction
(canvas pixel reads) that still requires one. This choice doesn't need
revisiting at deployment either way: once hosted over `http(s)` for
Prolific/MTurk, both `file://` restrictions are moot, so nothing forces a
switch away from classic scripts then. jsPsych itself ships a plain
`<script src="...">` / global-object flavor alongside its npm/bundler
flavor, so the jsPsych plugin wrapper can be written as one more script in
the `Game` namespace pattern with no friction. If a single-file bundle is
wanted before shipping (fewer network requests), these classic scripts
concatenate in load order with no tooling required — easier than bundling
ES6 modules would have been, not harder.

## Chosen path: jsPsych, built standalone first

Build this as a plain DOM app first — its own container `<div>`, its own
click listeners on the sprite elements, no jsPsych involved yet — get it to
full functional parity with Version_1, and only then wrap it as a jsPsych
plugin.

Why in that order: a jsPsych plugin has its own lifecycle (mount into a
container jsPsych provides, call `finishTrial()` when done, follow its data-
recording conventions). Building directly inside that from day one means any
bug could be in the actual port or in jsPsych's mounting/timing — two
tangled variables at once, right when the port itself (coordinate math,
overhang-based draw order, alpha-channel hit-testing) is already the hard,
error-prone part. A standalone build isolates that: any bug is definitely
the port. Wrapping a working standalone app in jsPsych afterward is
comparatively mechanical — move the existing `init()`/`start()` into the
plugin's trial function, call `finishTrial()` at whatever point counts as
"session over."

## What actually needs to reach parity (don't under-scope this)

Full visual rendering — every module and interactable sprite, correctly
positioned and layered, across all four walls, exactly matching what Pygame
already shows — is the immediate porting target, in full, from the start.
That's not extra design work sitting beyond the first milestone; it's a
direct, mechanical translation of code that already exists and works
(`objects.py`'s ~25 module classes, `assets.py`'s sprite tables,
`renderer.py`'s draw loop). There's no reason to scope the visual port down
to a subset of modules or a single wall.

What's genuinely out of scope for this first milestone is *module-specific
behavior* — the Press's dial-to-output mapping, the Control Panel's crash
logic, the Beaker's hidden stability variable, and so on — because none of
that exists in the Python version either: `rules.py` is empty, and most
interactables carry a placeholder sprite with no `on_click` logic behind
them yet. The only real behavior anywhere in Version_1 right now is wall
rotation via the movement arrows (0→1→2→3→0, `RoomState.rotate` in
`state.py`) and the Workbench's cabinet door opening/closing and revealing
its hidden contents (`CabinetDoor` in `objects.py`). Port those two
behaviors faithfully alongside the full visual render, then design new
module behavior directly in the web version from here on (see "Going
forward" below) — not by building it in Pygame first.

## Porting map — file by file, `../Version_1/src/` → here

Treat `../Version_1/src/` as the reference implementation and translate it
function by function rather than redesigning from scratch — it's already
correct and factored into small, clearly-named pieces, which makes this a
mechanical translation for most of it.

- **`config.py`** → a JS constants module. `TILE_SIZE`, `TOP_FACE_OVERHANG`,
  `GRID_COLS`/`GRID_ROWS`, `FLOOR_ROWS`/`CEIL_ROWS`/`MARGIN_COLS`,
  `NUM_WALLS`, `LOGICAL_WIDTH`/`LOGICAL_HEIGHT`, `INITIAL_SCALE`,
  `MIN_SCALE` all carry over as plain constants/arithmetic. `FPS` /
  `pygame.time.Clock().tick(FPS)` do **not** carry over as-is — see the
  `main.py` note below.
- **`environment/wall_layouts.py`** → nearly a direct transliteration, since
  it's pure data. `ModuleType`/`InteractableType` become JS objects or a
  small enum-like const map; `PlacedDevice`/`PlacedInteractable` become
  plain objects or classes; `WALL_0..3_DEVICES`/`_INTERACTABLES` and
  `ROOM_INTERACTABLES` carry over verbatim in structure.
- **`environment/enums.py`** → trivial (`Direction.LEFT`/`RIGHT` as a const
  object or string union).
- **`environment/objects.py`** → ES6 classes mirroring `ModuleBase` and
  `InteractableBase` exactly, plus every concrete subclass (all ~25 module
  types, `MODULE_CLASSES` lookup) and every interactable
  (`Button`, `Lever`, `Dial`, `LevelIndicator`, `Compressor`, `CabinetDoor`
  with its open/close + `.contents`-reveal behavior, `MoveArrowLeft`/
  `MoveArrowRight` wired to room rotation, `INTERACTABLE_CLASSES` lookup).
  `width_cells`/`height_cells` getters port directly (image width/height
  divided by `TILE_SIZE`, minus the overhang for modules).
- **`environment/environment.py`, `environment/state.py`** → a
  `RoomState`/`Wall` pair with the same `rotate()` step-and-modulo logic and
  `current_wall` accessor.
- **`environment/rules.py`** → stays an empty placeholder here too, for now.
- **`rendering/assets.py`** → a JS asset-preloader. This is the one place
  that needs a genuinely new pattern, not just a transliteration: browser
  image loading is asynchronous (`new Image(); img.onload = ...`), unlike
  `pygame.image.load()`, which is synchronous. The port needs an explicit
  "wait until every sprite has loaded" step (e.g. a `Promise.all` over every
  image) before the first render — Version_1 never had to think about this.
  Keep `MODULE_SPRITES`, `INTERACTABLE_SPRITES`, `BACKGROUND_SPRITES`, and
  `CABINET_DOOR_SPRITES` as the same lookup tables, same relative paths,
  just as JS objects instead of Python dicts.
- **`rendering/renderer.py`** → a DOM renderer reusing the exact same
  algorithms, per the "Rendering architecture" section above: `_to_px`
  (grid → logical pixel, margin-adjusted) still does the same arithmetic,
  just to produce `style.left`/`style.top` values instead of blit
  coordinates; `_sprite_topleft` (the overhang shift) is unchanged — keep
  render and hit-test going through the *same* function here too, exactly
  as the Python version's comment insists, so they can't drift apart.
  `_draw_background` creates/positions the wall-tile and floor-tile `<img>`
  elements once. `_draw_modules` and `_draw_interactables` create or
  reposition one `<img>` per sprite and set its `style.zIndex` from the
  anchor row (bottom row first, mirroring the Python sort) so the overhang
  layering stays correct — DOM append order alone isn't enough once
  elements get repositioned instead of recreated on every render.
  `_fit_rect`'s letterbox scaling becomes a CSS `transform: scale(...)` on
  the room container plus centering, recomputed on
  `window.addEventListener('resize', ...)` mirroring `handle_resize`.
  `find_interactable_at`'s alpha-channel hit-test (`surface.get_at
  (local_pos).a > 0`) becomes a `ctx.getImageData(x, y, 1, 1).data[3] > 0`
  read against an offscreen canvas that each sprite is drawn into once at
  load time (see "Rendering architecture" above — this doesn't come free
  just because the visible rendering is DOM-based). `screen_to_logical` is
  still needed to turn a click's page coordinates into logical room
  coordinates for that hit-test, even though the click event itself arrives
  from a DOM listener rather than a canvas one.
- **`rendering/ui.py`** → a click listener on the room container (event
  delegation, rather than one listener per sprite `<img>`) running the same
  `screen_to_logical` → `find_interactable_at` → `on_click` sequence.
- **`main.py`**'s `while running:` loop → do **not** port this as a
  continuous polling loop. Nothing in this game actually animates
  continuously — it's a static room until a click changes state — so the
  web version can be simpler than the Pygame one: render once on load
  (after assets finish loading), then re-render only after a click mutates
  state. If a continuous loop turns out to be needed later (e.g. for an
  animation), use `requestAnimationFrame`, not a fixed-tick loop — that's
  the standard web equivalent of `clock.tick(FPS)`.

Sprites: the same PNG files under `../Version_1/assets/` are reused
unchanged — no conversion needed, just reference them by relative path from
HTML/JS instead of through `ASSET_DIR`.

## Debugging workflow

A local server is required — do not open `index.html` directly via
`file://`. Run `python -m http.server 8000` (or any static file server)
from the project root, then navigate to
`http://localhost:8000/Version_1_web/index.html`.

This is unrelated to the ES6-module-vs-classic-script decision above
(classic scripts do load fine over `file://`). The actual cause: the
alpha-channel hit-test canvas (see "Rendering architecture") calls
`ctx.getImageData(...)` on a canvas that a locally-loaded sprite image was
just drawn into, and browsers refuse to read pixels back out of a canvas
that has drawn a `file://`-loaded image — every local file is treated as
its own unlabeled origin, so the canvas is considered "tainted" the moment
a cross-origin-looking image is drawn into it, purely as a security
precaution (stopping one local file from reading another's data through a
canvas). Serving over `http://localhost:8000` (or any real server) removes
this restriction because same-origin requests aren't subject to it.

This is not a workaround to remove later — it's already a preview of the
real deployment environment. The shipped version will be served from a real
`http(s)://` URL for Prolific/MTurk the same way `localhost:8000` stands in
for one now; only *which* server changes between now and then, not whether
one exists. Treat `http://localhost:8000/...` as the standard way to open
this project from here on, not `file://`.

A Claude Cowork/Code session with browser-automation tools can also load the
page itself (over the same local server), click through it, read the JS
console for errors, and take screenshots to self-check a change before
handing it back for a manual look.

## After parity: jsPsych wrapper + Prolific/MTurk plumbing

Once the standalone build matches Version_1 exactly (wall rotation + cabinet
door), wrap it as a jsPsych plugin, then layer on: a consent screen,
instructions, minimal demographics, an end screen; Prolific/MTurk URL-
parameter capture for the participant ID and the completion-code/redirect
flow back to the platform; and data logging via DataPipe → OSF (free, no
custom backend needed) rather than anything bespoke. These are standard,
well-documented jsPsych patterns — don't reinvent them.

## Going forward: where new module behavior gets written

Any module behavior designed from now on (the Press's dial→output mapping,
the Control Panel's random crash, the Beaker's hidden stability variable,
etc. — see `../Version_1/CLAUDE.md`) should be written directly here, in the
web version, not in Version_1's Pygame code first. Writing it once in Python
and porting it again later is exactly the duplicated effort this whole
folder exists to avoid. Version_1's Pygame build can still be used as a
personal scratchpad for reasoning through tricky logic if that's genuinely
faster to think in, but nothing written there from this point on is meant
to ship.

## Keeping this file current

This file reflects a deployment-strategy conversation that happened in
Cowork, not in the Notion design chat — if that conversation continues or
the tooling decision changes (e.g. Gorilla institutional access turns out
to be available, or jsPsych proves painful for a specific mechanic), fold
the update back in here before relying on stale reasoning.
