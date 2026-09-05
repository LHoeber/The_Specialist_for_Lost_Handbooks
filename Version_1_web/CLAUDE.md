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

## Chosen path: jsPsych, built standalone first

Build this as a plain HTML5 Canvas app first — its own `<canvas>`, its own
click listener, no jsPsych involved yet — get it to full functional parity
with Version_1, and only then wrap it as a jsPsych plugin.

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

## What actually needs to reach parity (don't over-scope this)

As of 2026-09-04, Version_1's only real behavior is: wall rotation via the
movement arrows (0→1→2→3→0, `RoomState.rotate` in `state.py`) and the
Workbench's cabinet door opening/closing and revealing its hidden contents
(`CabinetDoor` in `objects.py`). `rules.py` is empty — no other module has
real behavior yet, just placeholder sprites and, for a few, an
interactable wired up with no `on_click` logic. The web port's first
milestone is exact parity with *that*, not with the eventual full module
inventory. Don't try to design missing module behaviors while porting —
port what exists, faithfully, then design new behavior directly in the web
version from here on (see "Going forward" below).

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
- **`rendering/renderer.py`** → a Canvas2D renderer reusing the exact same
  algorithms: `_to_px` (grid → logical pixel, margin-adjusted), 
  `_sprite_topleft` (the overhang shift — keep draw and hit-test going
  through the *same* function here too, exactly as the Python version's
  comment insists, so they can't drift apart), `_draw_background`,
  `_draw_modules` (sort by anchor row descending — bottom row first — so
  the overhang layering stays correct), `_draw_interactables`, `_fit_rect`
  (letterbox scaling math), `screen_to_logical`, and `find_interactable_at`.
  The alpha-channel hit-test (`surface.get_at(local_pos).a > 0`) becomes a
  `ctx.getImageData(x, y, 1, 1).data[3] > 0` read on an offscreen canvas
  holding that sprite. Also needs a `window.addEventListener('resize', ...)`
  mirroring `handle_resize`.
- **`rendering/ui.py`** → a `canvas.addEventListener('click', ...)` handler
  running the same `screen_to_logical` → `find_interactable_at` → `on_click`
  sequence.
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

Correction (2026-09-05): opening the HTML file directly (`file://`) does
**not** work for interaction, only for the initial render. Browsers taint a
canvas against pixel reads (`getImageData`) once an image loaded from
`file://` has been drawn onto it — `drawImage` itself is unaffected, which
is why the first wall renders correctly, but `findInteractableAt`'s
alpha-channel hit-test throws a `SecurityError` on every click, silently
(no visible reaction, easy to miss without opening DevTools). This is a
standard browser restriction for local canvas apps, not a bug in this port,
and it disappears entirely once the app is served from a real origin (which
is exactly what happens once this is actually deployed for participants) --
it only bites *local testing*.

So: run a one-line local static server instead of double-clicking the file.
From the repo root (`The_Specialist_for_Lost_Handbooks/`):

```
python -m http.server 8000
```

then open `http://localhost:8000/Version_1_web/index.html` — serving from
the repo root (not `Version_1_web/` itself) keeps `../Version_1/assets/`
resolving correctly. A Claude Cowork/Code session with browser-automation
tools can do the same thing (`.claude/launch.json` already has a
`repo-static-server` config for this), then click through it, read the JS
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
