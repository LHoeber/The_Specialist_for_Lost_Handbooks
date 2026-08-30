# Version_1 — context for Claude Code

This file is the bridge between the design conversation happening in Laura's Claude.ai project ("PhD Topic") and this repo. Read it fully before making structural changes — it explains *why* the game has to work the way it does, not just what to build.

## Research framing

Project title: "Information Theoretic Models of Curiosity in Hierarchical Models of the World." The game is one leg of a larger PhD project that otherwise centers on a VR room-exploration paradigm and an information-theoretic/RL model of curiosity (see `docs/design/research-context.md`). The game's job is to serve as a controlled, game-based condition for eliciting curiosity-driven behavior under information theory / RL framings, and potentially to contribute to a benchmark comparing different curiosity models. It is deliberately a (PO)MDP: actions must influence future states, and state must be only partially observable — that structural requirement is the whole point, not an incidental design choice, and it's what differentiates this from simpler exploration-behavior projects in the group.

## What the game has to do (non-negotiable requirements)

1. **Partial observability** — indicators (dials, lights, sounds, levers) never state what they measure. Players must infer meaning by correlating actions with outcomes.
2. **Hidden sequential state** — a module's condition/behavior depends on its full action history, not just its current setting.
3. **Graded prior familiarity** — real-world knowledge should transfer differently across module "tiers":
   - familiar (coffee-machine-like: daily real-world interaction) — not yet built, see Open TODOs below.
   - intermediate (chemistry-bench-like: unfamiliar context, consistent physics) — **this is what the current module inventory below implements.**
   - unfamiliar (alien technology: nothing, even physics, can be assumed) — not yet built.
4. **Aleatoric vs. epistemic contrast** — some behaviors must be genuinely learnable through inspection; others must be irreducibly random no matter how carefully the player investigates. Confirmed by Laura (2026-08-28) as a protected priority: keep this even if other requirements get trimmed. Rationale: the Model Framework doc states only epistemic (not aleatoric) uncertainty is curiosity-relevant — without a module that separates "learnable through inspection" from "stays random regardless," there's no way to check in the game data whether curiosity tracks epistemic uncertainty specifically, rather than uncertainty/noise in general.
5. **Information-seeking has a price** — fixed time and/or limited resources, so exhaustive exploration isn't free.
6. **Learning-centered goal structure** — the point is that the player learns how something works, not that they produce a specific output through a shortcut. End-of-session probes ("how would you fix module X," "what would you do to change this item's color") test understanding, not task completion.
7. **Limited state/action space** — stay discrete, cap the number of actions per module, keep movement incremental.

## Setting & procedure

The player runs a repair company ("The Lost Handbook Specialist"), hired by companies that lost the manual for a machine and want it reverse-engineered. Each session: limited time/resources to investigate the machine, limited tool slots (bring-your-own tools means deciding what to leave behind), then a probe at the end testing what was actually learned. Orientation is discrete: one wall of the room visible at a time (rotate between 4), one side of a machine visible at a time (walk around it, 4 discrete positions).

## Where to start building

`docs/design/game-prototype.md` has an "Implementation" section with a concrete **Phase 1** build spec — environment setup, initial rendering (window sizing, sprite-scaling rules, the 6px top-face-overhang blitting order), object initialization (module/interactable base classes), and room orientation mechanics (click handling, the movement arrows). That section was missing from this repo's mirror until 2026-08-30 — if an earlier Code session asked Laura to paste `game-prototype.md`'s content directly into chat, this was why: there was nothing concrete to build from beyond the module/wall reference tables. Start there for "what to build first," not from the module tables alone.

## Current module inventory & tier flag

`docs/design/game-prototype.md` mirrors the full Notion module/interactable tables (Furnace, Press and Pressure Tank, Centrifuge, Mixer, Packaging/Labeling, Filter/Sieve, Fume Hood, Connector Box, Fuse Box, Generator, Electrolyzer, Flask/Beaker/Dishes holders, Bin, Shelf, Pipes, Toolbox — plus generic interactables: beaker, lever, button, dial).

**Important:** this inventory reads as the *intermediate/chemistry-bench* familiarity tier (per requirement 3 above), not the familiar/coffee-machine tier. A separate, smaller module set built from real kitchen-object priors (water reservoir, grounds compartment, drip tray, a couple of buttons/dials) still needs to be designed for the familiar tier — don't assume the current inventory covers all tiers.

**Wall layouts — the full room is now specced, not just wall 1.** `wall_layouts.py` (`src/environment/wall_layouts.py`, added 2026-08-30) is a machine-readable transcription of the "Wall Designs" diagram and places devices across **all four walls**, not just wall 1 — see the "Wall Layouts" section in `docs/design/game-prototype.md` for the full per-wall device/interactable listing. It also corrects the grid to **3 rows × 4 columns** per wall (the "wall-1 loadout" paragraph below originally assumed a 3×3 grid). Note this is about how much of the room's *content* is speced/built, separate from the room-orientation mechanic in "Setting & procedure" above (one wall visible at a time, rotating discretely through all 4) — that viewing mechanic was never in question and holds regardless of how many walls have content. What is still open: whether the earlier plan to build wall 1 first and hold the rest "in reserve" still applies now that the diagram already specs content for all four walls, or whether that plan has effectively been superseded — worth confirming with Laura rather than assuming either way.

**Original wall-1 rationale, and where it now sits in the diagram.** The three modules this section originally proposed as a single co-located wall-1 loadout turn out, per `wall_layouts.py`, to be spread across three *different* walls, not grouped together: Centrifuge and Press both land on diagram wall 3 (0-indexed WALL_2) — but Pressure Tank lands on diagram wall 4 (WALL_3), separated from the Press it's supposed to pair with — and Control panel lands on diagram wall 2 (WALL_1). None of the three sit on diagram wall 1 (WALL_0). That's worth resolving with Laura: either the diagram's placement should move to co-locate Press with Pressure Tank on one wall as originally designed, or the "wall-1 loadout" framing itself needs to be dropped in favor of whatever the diagram actually encodes. The design rationale below is unaffected either way:

- **Press and Pressure Tank** (2x2 = 4 cells, if kept co-located) — the pressure-level dial → output form (block/diamond/plate) mapping must never be stated in the UI; the player has to correlate dial position with resulting output. If repeated use degrades the mold and drifts the output distribution, this module also covers requirement 2 (hidden sequential state) in the same slot — prefer that over adding a separate module for it.
- **Centrifuge** (1x1 = 1 cell) — kept deliberately simple, no history-dependence, active/inactive + 3-level rotation. Serves as the clean contrast case against the Press ("this one has memory, this one doesn't").
- **Control panel** (1x1 = 1 cell) — real module, now in the inventory (see `docs/design/game-prototype.md`). Randomly crashes and goes black with a loading screen; needs to be unplugged to restart — no player action prevents it. Controls the composition scanner (can only start with the scanner's shutter closed; only shows useful results if a mixture was inside; can send results to the label printer). This is the module that implements the irreducible/aleatoric side of requirement 4. `Version_0/assets/indicators/noisy_console.png` from the previous prototype is a plausible visual starting point. The learnable/epistemic counterpart is the Beaker's heat/centrifuge stability (medium/high/unbreakable, assigned per beaker) — a hidden variable the player can build a working estimate of through repeated testing, unlike the control panel's crash.

Whether the rest of the inventory (Furnace, Mixer, Filter/Sieve, Fuse Box, Generator, Electrolyzer, etc.) is still "held in reserve for wall 2+" or should now be built out per the full diagram is exactly the open question flagged above — don't assume either answer without checking with Laura.

**Compressor lives inside the Workbench, but there's no way to open one yet.** On wall 4 (0-indexed WALL_3), the Compressor interactable is meant to sit inside the Workbench and only become visible once the Workbench is opened — confirmed design intent, not a placement guess. The Workbench doesn't have an openable handle/door interactable defined yet, though, so this can't actually be implemented as "hidden until opened" until that's built. Before building wall 4 in code, also double check `wall_layouts.py`'s `parent_index` values on that wall: adding a second Fume Hood shifted every later device's list index up by one, and the Dial's and Compressor's `parent_index` weren't updated to match — as written they now point at the Sink and the Furnace respectively, not the Furnace and the Workbench their own comments describe. Likely just a leftover indexing bug from the reindex, worth a quick fix in the source file before relying on it.

## Data to collect

Number of interactions per module, percentage of action space covered, switching time between perspectives, waiting time between actions.

## Relationship to Version_0

`../Version_0/` is the previous prototype (Pygame: `game/`, `rendering/`, per-module asset subfolders under `assets/`). Useful as a reference for asset style and for what a module's state machine looked like in practice (e.g. `Version_0/game/objects.py`, `Version_0/game/state.py`), but Version_1 is a deliberate rebuild for architectural coherence — don't just copy Version_0's structure over without evaluating whether it holds up under the tier/module-budget decisions above. In particular, Version_0's assets are organized as flat per-mechanism folders (`heater/`, `press/`, `centrifuge/`, `indicators/`, ...); Version_1 needs assets organized around the block-module abstraction (module → footprint/size → wall placement) described in `docs/design/game-prototype.md`, so expect the asset restructuring to be more than a file move.

## Keeping this file current

Design decisions for this project happen in Laura's Claude.ai chat/Notion project, not here. When a design session there changes something that affects implementation (a new module, a tier decision, a requirement reinterpreted), that should get folded back into this file or `docs/design/` before Code sessions rely on it — treat this file as a snapshot, not a live feed, and flag to Laura if something you're being asked to build seems to contradict what's written here.
