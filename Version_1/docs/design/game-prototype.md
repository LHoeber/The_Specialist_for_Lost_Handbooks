# Game Prototype — design reference

Mirrored from the "Game Prototype" page in the PhD Topic Notion project (last synced 2026-08-30, adding the wall-layout diagram transcription and — previously missing from this mirror entirely — the "Implementation" / Phase 1 build spec, plus the Conceptual requirements sub-detail on aleatoric/epistemic uncertainty and POMDP structure). This is reference material — `../../CLAUDE.md` has the condensed, load-bearing version with current decisions layered on top. If this file and a live design conversation disagree, the conversation wins; ask Laura to reconcile. Do not write decisions back to the Notion page from here — Notion is the source, this file is the mirror.

## Decisions

| Question | Decision |
|---|---|
| Discrete or continuous state-space? | Start off with discrete for simplicity |
| 2D or 3D? | Start off with 2D for simplicity |

## Conceptual requirements / theoretical basis

1. Elicit different kinds of curiosity-driven behaviors in the players
2. Aleatoric vs. epistemic uncertainty:
   - aleatoric → some transition probabilities are inherently stochastic and unlearnable
   - epistemic → others are learnable with enough data/observations
   - known environment uncertainty can help evaluate/calibrate a model's uncertainty-quantification method
3. POMDP structure, where the actions influence next and future state of the environment
   - "Active inference on discrete state-spaces" (Costa et al., 2020)
   - based on discrete state-space, action-conditioned HMM with stochastic transition probabilities
   - discrete allows fully specifying the POMDP structure and comparing the model's belief tracking against ground truth
   - POMDP = action-conditioned HMM + reward/cost function + policy
   - even though this is a Markovian process, getting Z_t to predict Z_t+1 in the world model requires memory about the history of states

## Implementation requirements

| Requirement | Details | How to implement |
|---|---|---|
| Partial observability | Player must infer meaning by correlating actions with outcomes; learning through interaction | Indicators don't state what they measure — dials, lights, sounds, levers |
| Hidden sequential state | Machine's condition changes over time; depends on full action history, not only current | State of module/setting and what you can do with it depends on what you did before |
| Graded prior familiarity | Systematically vary how much real-world knowledge transfers | Fully familiar (coffee machine — daily real-life interaction); intermediate (chemistry-bench — unknown context, consistent physics); fully unfamiliar (alien technology — nothing, even physics, must make sense) |
| Aleatoric vs. epistemic contrast | Some behaviors are genuinely learnable; some are inherently random and stay uncertain no matter how much you investigate | Learnable: beakers have random temperature stability, but always survive low. Completely random: console/computer can crash randomly without your actions influencing anything |
| Information-seeking has a price | Investigating must require a trade-off, otherwise there's no reason not to simply explore everything | Fixed time available; limited resources you can use to try out things (money, material, tool wear) |
| Learning-centered goal structure | The learning itself is the goal, not producing a certain outcome (where shortcuts could exist); possibly purely testing knowledge without feedback | End-of-session task: "what would you do to make this item another color," "how would you fix module X if it breaks" |
| Limited state/action space | Keep the number of possible states and actions manageable; stay discrete for now | Cap number of possible actions per module; keep 2D movement incremental |

## Setting

You run a repair company called "The Lost Handbook Specialist." You are employed by companies that lost the handbook for a machine and want you to figure out again how it works.

## Procedure

- You are given a limited amount of time and resources to figure out as much as possible about the machine assembly.
- You have limited tool slots — you can bring your own tools, but need to decide which ones to take or leave behind.
- At the end you are probed to see if you figured out how to produce a certain thing / handle certain problems.

## Machine modules

| Name | States | Actions | Size | Function / notes |
|---|---|---|---|---|
| Furnace | door open/close; heat level off, low, medium, high | put flask in/take it out; close/open door; set heat | 2x2 | Heat can only increase to high if door is closed; heat decreases to medium if door opened while high; liquid mixtures become a dense mass; burns liquid and produces a smoke cloud if set too high |
| Press and Pressure Tank | active/inactive; pressure level low, medium, high; form: block, diamond, plate | put flask in/take it out; activate/deactivate; set pressure | 2x2 | Form is only maintained if the mixture was heated; otherwise liquid is spilled and needs to be cleaned |
| Centrifuge | active/inactive; rotation level low, medium, high | put flask in/take it out; activate/deactivate; set rotation speed | 1x1 | Separates colors |
| Mixer | active/inactive; rotation level low, medium, high | put flask in/take it out; activate/deactivate; set rotation speed | 2x1 | Mixes colors |
| Packaging and Labeling Station | # labels left; label ready/not ready | put label on; seal | 2x1 | Sticks on label if present and seals final product |
| Filter/Sieve | filled/empty; active/inactive; percent done 0/25/50/75/100; spilled/clean | fill/empty; activate/inactivate; put container in before something spills | 2x1 | Separates powder from mixture |
| Fume hood | active/inactive | activate/inactivate | 1x1 | Removes built-up smoke |
| Connector Box | open/closed; connections: I1, I2 | connect I1 or I2 | closed 1x1, open 1x2 | Connects one of two devices to the power supply |
| Fuse Box | fuses 1,2 active/inactive | switch on/off 1,2 | closed 1x1, open 1x2 | Emergency-stop a machine or reconnect it |
| Generator | active/inactive; fuel level empty, low, medium, high | activate/inactivate; fill fuel | 1x2 | Provides an additional power source |
| Electrolyzer | active/inactive | activate/deactivate | 1x1 | Electrolizes mixture to make it shiny |
| Flask holder | holding 0,1,2,3 | add material to beaker | 1x1 | Holds liquid resources |
| Dishes | holding 0,1,2,3 | add material to beaker | 0.5x1 | Holds powder resources |
| Bin | empty, low, medium, full | discard | 1x1 | Deletes beaker + contents |
| Shelf | — | — | 1x1 or 1x2 | — |
| Pipes with valve | open/blocked | open/block | 1x1 | Makes the sink work / emergency shut-off water if the sink is broken |
| Toolbox | — | — | 1x2 | — |
| Beaker holder | filled/empty | place/take beaker | 1x1 | — |
| Sink | (unspecified) | empty + wash beaker | 2x1 | Can break and overflow if the handle breaks off |
| Composition scanner | filled/empty; closed/open | open/close shutter; place/take beaker | 2x1 | — |
| **Control panel** | active/inactive | cut/connect power supply; activate composition scanner; discard data/send results to printer | 1x1 | **Randomly crashes and goes black with a loading screen; needs to be unplugged to restart.** Controls the composition scanner; can only start if the scanner's shutter is closed; only shows useful results if a mixture was inside; can send results to print out on the label printer. |

**Door** and **Workbench** also appear as placed objects in the wall-layout diagrams (see Wall Layouts below) but are plain furniture, not machine modules — no states or actions, just floor space with a footprint.

## Interactables

| Name | States | Actions | Size | Function |
|---|---|---|---|---|
| Beaker | slot 1/2, empty/filled; **heat stability: medium, high, unbreakable**; **centrifuge stability: medium, high, unbreakable** | move; fill; empty | 1x1 | Moves mixture between modules; can be discarded in the bin with its contents; can be emptied and washed in the sink; leaves a spill when filled and breaking in the centrifuge or furnace |
| Lever | up/down | toggle | 1x0.5 | — |
| Button | active/inactive | toggle | 0.5x0.5 | — |
| Dial with arrows | position off, low, medium, high | left/right | 0.5x1 | — |

**Level Indicator** and **Compressor** also show up in the wall diagrams, attached to specific modules (see Wall Layouts below); **Power Plug** is defined as a type but not currently placed on any wall. None of the three have their states/actions specified yet — add rows here once their behavior is defined.

## Wall Layouts (Version_1, Phase 1)

Transcribed from the "Wall Designs" diagram screenshot into `wall_layouts.py` in the Version_1 codebase (`Version_1/src/environment/wall_layouts.py`), which is the machine-readable source of truth for exact placements — this section mirrors it in prose. Most of the ambiguities from the initial transcription pass have since been resolved directly in that file (last edited 2026-08-30); the few still open are called out below and in `wall_layouts.py` itself.

Each wall is a grid 3 rows (0–2) by 4 columns (0–3), with a 0.5-cell floor strip below row 2 that sits outside the module grid. A device's position is given as its top-left `(row, column)` anchor cell; its full footprint follows from its sprite size at render time. An interactable's position is given as an `(row, column)` offset relative to its parent device's anchor (the movement arrows are the exception — they belong to the room, not a device). Wall numbering here is 0-indexed and matches the room-orientation mechanics (wall 0 shown initially, rotating 0→1→2→3→0); the Notion diagram itself labels the same four walls 1–4.

**Wall 0**

| Device | Anchor | Notes |
|---|---|---|
| Mixer | (0,0) | spans down into row 1 |
| Dishes | (0,1) | |
| Flask holder | (0,2) | |
| Flask holder | (0,3) | |
| Shelf | (1,1) | |
| Door | (1,2) | spans down into row 2 |
| Beaker holder | (1,3) | |
| Toolbox | (2,0) | |
| Workbench | (2,3) | |

(2,1) and (2,2) are empty. Interactables: a Button and a Level Indicator sit side by side at the bottom of the Mixer. **Still open:** the Level Indicator's exact offset is marked VERIFY in `wall_layouts.py`.

**Wall 1**

| Device | Anchor | Notes |
|---|---|---|
| Composition scanner | (0,0) | spans down into row 1; "Mixture/Analyzer/Shutter" labels in the diagram are its own state, not a separate object |
| Shelf | (0,1) | |
| Fuse box | (0,3) | |
| Packaging and Labeling Station | (1,1) | spans right into column 2 |
| Control panel | (1,3) | |
| Workbench | (2,0) | |
| Bin | (2,1) | |
| Connector box | (2,2) | |
| Generator | (2,3) | |

No red-marked interactables visible on this wall in the diagram.

**Wall 2**

| Device | Anchor | Notes |
|---|---|---|
| Shelf | (0,0) | |
| Shelf | (0,1) | |
| Pipes with valve | (0,2) | spans down into row 1 |
| Filter | (0,3) | spans down into row 1 |
| Centrifuge | (1,0) | |
| Electrolyzer | (1,1) | |
| Press | (1,2) | |
| Workbench | (2,0) | |
| Workbench | (2,1) | |
| Workbench | (2,2) | |

Interactables: a Button on the Centrifuge; a Button on the Electrolyzer; a Lever on the Press. The Power Plug that an earlier transcription pass placed on the Shelf at (0,0) has since been removed from this wall in `wall_layouts.py` — it's currently unplaced anywhere (still defined as an `InteractableType`, just with no location assigned yet).

**Wall 3**

| Device | Anchor | Notes |
|---|---|---|
| Pressure tank | (0,0) | |
| Shelf | (0,1) | |
| Fume hood | (0,2) | |
| Fume hood | (0,3) | |
| Pipes with valve | (1,0) | |
| Sink | (1,1) | |
| Furnace | (1,2) | |
| Workbench | (2,0) | |

The earlier ambiguity here is resolved: what first read as one oversized Fume Hood plus two unexplained "Sliding Door" labels is actually two ordinary 1x1 Fume Hoods, side by side at (0,2) and (0,3) — no separate sliding-door object needed.

Interactables: a Level Indicator on the Pressure Tank; a Dial; a Compressor, meant to sit **inside the Workbench**, only visible once the Workbench is opened — a real design decision (not a placement guess), confirmed by Laura. The Workbench doesn't yet have an openable handle/door interactable to reveal it, though — that's a known follow-up, not built yet.

**Worth checking in `wall_layouts.py` before Claude Code builds off this wall:** adding the second Fume Hood shifted every later device's index by one (Sink is now index 5, Furnace 6, Workbench 7 — each one higher than before), but the Dial's and Compressor's `parent_index` values weren't updated to match. As written, the Dial's `parent_index=5` now points at the Sink and the Compressor's `parent_index=6` now points at the Furnace — not the Workbench the Compressor's own comment says it belongs to. This looks like an off-by-one left over from the reindexing rather than an intentional move; if the Dial was meant to stay on the Furnace and the Compressor on the Workbench, those two indices need bumping to 6 and 7 respectively.

**Movement arrows** (room-level, not attached to any device, identical on every wall): left arrow at the wall's middle row, leftmost column; right arrow at the middle row, rightmost column.

## Orientation

1. You can only see one wall of the machine room at a time and rotate discretely between all 4.
2. You can only see one side of a machine at a time and walk around it discretely between all 4.

## Data to collect

- Number of interactions per module
- Percentage of action space covered
- Switching time between perspectives
- Waiting time between actions
- Model-predicted uncertainty (σ² or equivalent)

## Implementation

This section is the actual build spec for Claude Code — it was missing from this mirror until 2026-08-30 even though it's been in the Notion page for a while, so past Claude Code sessions had nothing concrete to work from beyond the module/wall reference tables above. `Version_1/CLAUDE.md` should always point here for "what to build first."

### Phase 1

**Environment setup**

- Create the overall structure of the game inside `src/`, similar to Version_0:
  - `main.py` for calling all of the subscripts
  - a game environment folder with scripts for environment, state, enums, objects, and rules
  - a rendering folder, where all sprite loading and rendering to the window is handled, plus the UI script that handles all direct player input
  - an agent folder, containing scripts that try out (different) agent implementations for the eventual reinforcement learning

**Initial rendering**

- Create a window sized as a multiple of 32×32 tiles, starting at width 4 and height 3.5 (the floor only takes up 0.5 tiles at the bottom).
  - The origin is the top-left cell (0,0); coordinates are represented as (row, column).
- Carry over the Version_0 mechanic that scales the window and every sprite placed in it by a pre-defined scale factor.
  - Also support dynamic scaling when the user resizes the window, keeping the width:height proportion and filling the remainder in black when the window size isn't an exact multiple of the defined height and width.
  - Scaling must not use smoothscaling — the sprites are pixel art and shouldn't blur.
  - Sprites use a slight top-down perspective: a module 1 cell tall has a sprite 32px wide × 38px tall (32px for the front face + 6px showing the top face); a module n cells tall has a sprite 32px wide × (38 + (n−1)×32)px tall (e.g. 70px tall for n=2).
  - That extra 6px sits above the module's own topmost occupied row and overlaps into the row directly above it — so modules must be painted in row order from the bottom row of the wall upward (highest row index first), so each module's sprite draws on top of the 6px overhang of whatever is in the row below it, not the other way round.
  - Concretely: a module's sprite is blitted starting 6px above the pixel-row where its top occupied grid cell begins, not exactly at that row's boundary.
- Load the sprites of different categories from the assets folder and build templates of 3×4-cell walls, where sprites can be flexibly assigned to cells.
  - This should also allow placing tiles (smaller buttons and levers) in a specific quarter of one of those larger cells.
- Layer order: background tiles for walls and floor first (walls cover rows 0–2, floor covers the bottom half-row), then the module sprites placed per the manual assignment in `wall_layouts.py`.
- Initially only show the arrangement of wall 0.

**Initialize all objects**

- Create a basic (abstract) parent class for modules with the functions/attributes shared by all of them (position, assigned wall, currently assigned sprite(s) — can be multiple, relative sprite position(s) for those possibly-multiple sprites).
  - Size is inferred from the sprite's pixel dimensions: width in cells = sprite width / 32; height in cells = (sprite height − 6) / 32, to account for the fixed 6px top-face overhang described under "initial rendering."
- Create derived classes for every object defined in the Notion documentation — for now as placeholders, before their specific functions and possible interactions get defined.
- Create a basic class for UI elements / interactables:
  - each is assigned to a specific module and has a position relative to the cells that module occupies
  - each has its own size and can span multiple cells or only part of a cell
  - each performs a specific action when clicked
  - the sprite's non-transparent area defines what's actually clickable/interactable

**Room orientation mechanics**

- Build a basic structure for handling player UI input: recognize clicks at a given point in the window (accounting for the current scale factor).
- Determine which UI element was clicked:
  - only non-transparent regions of a UI sprite count as an interaction/activation
  - only the sprites of currently-rendered objects are interactable
- Implement changing room orientation via the movement arrows:
  - place the big moving left/right arrow sprites at row 1, column 0 and row 1, column 3
  - clicking the left arrow shifts the view to wall 3 (from wall 0) and renders everything predefined there
  - clicking the right arrow shifts the view to wall 1
  - walls cycle sequentially 0 → 1 → 2 → 3 → 0 when always moving right, and the reverse when always moving left

### Wall layout data format

The manual wall/cell assignment referenced under "initial rendering" above is specified in code at `Version_1/src/environment/wall_layouts.py`. Conventions used there:

- `ModuleType` — one entry per machine module from the Machine modules table, plus `DOOR` and `WORKBENCH` for the plain furniture pieces.
- `InteractableType` — one entry per row of the Interactables table, plus `LEVEL_INDICATOR`, `POWER_PLUG`, and `COMPRESSOR`, which appear in the wall diagrams but aren't described in that table yet.
- Each wall lists its devices as `(type, anchor)` pairs, where `anchor` is only the device's top-left `(row, column)` cell — the full footprint is inferred from its sprite at render time, so nothing here needs to restate a device's size.
- Interactables are listed separately as `(type, offset, parent_index)`, where `offset` is a `(row, column)` position relative to the parent device's anchor, and `parent_index` points at that device's position in the wall's device list. The movement arrows are the one exception — they're standalone (`parent_index = None`) since they belong to the room, not to a specific device.

## Notes carried over from the PhD Topic design chat

- **Tier flag:** this whole inventory reads as the intermediate/chemistry-bench familiarity tier (per the "Graded prior familiarity" requirement above), not the familiar/coffee-machine tier. A separate, smaller module set built from real kitchen-object priors (reservoir, grounds compartment, drip tray, a couple of buttons) still needs to be designed for that tier.
- **Aleatoric vs. epistemic contrast — now implemented by real modules, not just illustrative text:** the *Control panel*'s random crash-and-reboot is the irreducible/aleatoric side (no action prevents it). The *Beaker*'s heat/centrifuge stability (medium/high/unbreakable, assigned per beaker) is the learnable/epistemic side — it's a hidden variable, but one the player can build a working estimate of through repeated testing across beakers and settings. Together these are the pairing the design chat flagged as the single most diagnostic manipulation for the underlying research framework (only epistemic, not aleatoric, uncertainty is meant to be curiosity-relevant) — confirmed by Laura as a protected priority on 2026-08-28.
