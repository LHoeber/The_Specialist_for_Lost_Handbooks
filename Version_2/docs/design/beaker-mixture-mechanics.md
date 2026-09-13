# Beaker, mixture and placeable-object mechanics

Captured from a Cowork conversation (2026-09-13) that worked out how the
Beaker gets picked up, filled, carried, and set down at other stations, and
how its contents render. This introduces a genuinely new, reusable concept
(**placeable objects** and **placeable slots**) on top of the existing
grid-navigation mechanic (see `grid-navigation.md`) — the Beaker is just the
first thing that uses it.

## Why this exists

The Beaker is meant to be the one object that can show up in a large number
of different situations (filled at the flask/dish stations, set down at
almost every processing device, eventually poured and processed) rather than
being a one-off. Building it as a generic "placeable object in a placeable
slot" system now — instead of hard-coding "the Beaker can go in the
BeakerHolder" — means the next carryable object (if one is ever needed)
reuses the same mechanism instead of a second bespoke one.

## Scope of this pass

Explicitly **in scope**: picking the Beaker up into the single inventory
slot, carrying it, placing it into any station that declares a placeable
slot, filling it at the flask/dish stations (only while it's sitting in the
BeakerHolder), the overflow/no-beaker spill visual, and rendering the
Beaker's contents in the order ingredients were added.

Explicitly **deferred** (do not build these now, just don't design against
them being impossible later):

- **Breaking/shattering** the Beaker (a drop, an accident, a failed
  process) is a *separate* mechanic from the overflow/no-beaker spill below
  — it has its own trigger and its own cleanup story, neither of which is
  designed yet. Don't conflate the two.
- **Cleaning up** any spillage (overflow spill or a future breakage spill)
  — no mechanic for this exists yet. A spill, once it happens, stays
  rendered indefinitely for this pass.
- **Pouring/transferring** the mixture between containers, and **emptying**
  a beaker (or any other container) — not built this pass. Only adding
  ingredients to a beaker sitting in the BeakerHolder, and moving a beaker
  (filled or empty) between placeable slots, are in scope.
- **Actual processing** of the mixture at any device (heating, pressing,
  mixing, etc.) — a beaker can already be placed at and picked back up from
  several processing stations this pass (see below), but nothing happens to
  its contents yet. The data model should leave room for a future "form"
  change (liquid → some processed, non-liquid representation with different
  mask art) without wiring up *when* or *how* that transition happens.
- **Restocking a depleted flask/dish holder.** Depletion itself is now in
  scope (see "Filling: FlaskHolder and Dishes" below) — what's still
  deferred is any way to refill a holder once all 3 of its slots are used
  up. Once empty, it stays empty; no restock mechanic exists yet.

## Placeable objects and placeable slots (new, general mechanism)

- A **placeable object** is anything that can be picked up into the single
  inventory slot and later set back down. For this pass, the only placeable
  object is the `Beaker`. Mark it with a simple flag (e.g.
  `static isPlaceable = true` on the class, or an instance flag) rather than
  checking `instanceof Beaker` at call sites, so a second placeable object
  later doesn't require touching the dispatch logic.
- A **placeable slot** is a capability a module declares on one of its own
  occupied tiles: "an object can be set down here." Add a `placeableSlots`
  array to `ModuleBase` (parallel to the existing `subGrids` array), each
  entry roughly:
  ```
  {
    offset: [row, col],       // relative to the module's own anchor
    anchorPoint: [0.5, 0.5],  // default: center of the tile's lower 32x32
                               // area (i.e. below TOP_FACE_OVERHANG); pass
                               // a different fraction to override per slot
    layerIndex: <int>,        // where in this module's own sprite stack to
                               // draw the occupant -- see "Rendering" below
    occupant: null,           // the placeable object currently here, or null
  }
  ```
  A slot's absolute position is the module's anchor plus its offset, same
  convention as `subGrids` entries and interactable offsets elsewhere.
- **Rendering a slot's occupant**: a module's own sprites already draw as an
  ordered stack (see `SpriteOwner.sprites`/`spriteOffsets`). `layerIndex`
  says how many of that stack's *own* layers to draw before the occupant,
  e.g. `layerIndex: 1` for a back/front module (BeakerHolder, FlaskHolder,
  Dishes) draws back, then the occupant, then front — matching the
  `assets.js` comment that these back/front pairs exist specifically "so a
  future mixture-visibility layer can sit between them." Default
  `layerIndex` to the full length of the module's own sprite stack (i.e. on
  top of everything) when not specified — only the back/front modules need
  an explicit override of 1.
- **"do" dispatch priority** — this changes `RoomState._performRoomDo`
  itself, ahead of the existing interactable → sub-grid-entry → module chain
  (which stays exactly as-is as the fallback):
  1. **If the inventory slot is occupied**: "do" always means "place the
     carried object here, if this position has an empty placeable slot."
     If it does, move the object there and empty the inventory. If this
     position has no placeable slot (or its slot is already occupied),
     **nothing else happens** — do not fall through to whatever this
     position's normal action would otherwise be. Carrying something
     takes over "do" completely at every position until it's set down.
  2. **Else, if the inventory slot is empty and this position has an
     occupied placeable slot**: "do" means "pick that object up" — move
     the slot's occupant into the inventory, empty the slot. This takes
     priority over that position's own interactable/module action, exactly
     like step 1 does for placing.
  3. **Else**: fall through to the existing dispatch chain unchanged.
- **Single inventory slot**: add `this.inventory = null` to `RoomState`.
  Only one object at a time, matching the existing single-slot UI concept.
- **Inventory UI rendering**: a 32×32 semi-transparent white square, fixed
  to the bottom-right corner of the *rendered window* (not tied to any wall
  or grid cell — same visual size as one tile, but positioned by screen
  space, always visible regardless of which wall is shown or where the
  player stands). When `roomState.inventory` isn't null, draw that object's
  **icon sprite** centered in the square — for the Beaker this is the
  standalone `containers/beaker.png` (the flat single-sprite version,
  distinct from the `beaker_back.png`/`beaker_front.png` pair used when it's
  actually placed in the world).

## BeakerHolder (new module)

- New `ModuleType.BEAKER_HOLDER`; sprites
  `["containers/beaker_holder_back.png", "containers/beaker_holder_front.png"]`
  (already in `assets/containers/`); new `BeakerHolder` class in
  `objects.js`, same shape as any other simple `ModuleBase` subclass.
- Placed on **Wall 0, anchor `[1, 3]`** in `wall_layouts.js`.
- One placeable slot at offset `[0, 0]` (its own anchor tile),
  `layerIndex: 1` (sandwiched between back and front, same as the other
  container modules). Its constructor creates the game's one `Beaker`
  instance and sets it as that slot's initial occupant — this is the
  Beaker's starting position, per the original request.
- No `doAction` of its own — the general placement/pickup priority rule
  above already handles "do" at this tile for free, since it's just a
  module with one placeable slot.

## Beaker

- `ingredients`: ordered array, up to 3 entries, each identifying which
  material was added (e.g. `"acid" | "alkaline" | "powder"`). Order = add
  order, oldest first.
- A shared lookup, e.g. `MATERIAL_COLORS = { acid: [255,0,0], alkaline:
  [0,0,255], powder: [255,255,255] }` (adjust exact RGB to taste) — the
  single source of truth for which color a material tints to, used by both
  the Beaker's own mixture masks and the FlaskHolder's flask masks.
- `form`: add the field now (default `"liquid"`), but nothing sets it to
  anything else yet — this is the hook a future processing pass will use to
  swap in a non-liquid mask set. Don't build the transition logic itself.
- **Rendering order**: `beaker_back.png`, then one tinted mask layer per
  ingredient present so far — `masks/beaker_mix_mask_1.png` for the first
  ingredient added, `_2` for the second, `_3` for the third, each tinted to
  that ingredient's `MATERIAL_COLORS` entry (see "Tinted-mask rendering"
  below) — then `beaker_front.png`. Zero, one, two or three mask layers
  draw depending on `ingredients.length`; never more than three.
- Icon sprite (for the inventory square) is the separate flat
  `containers/beaker.png` — simplest to just always show that regardless of
  current contents for this pass (a contents-aware inventory icon can come
  later if wanted).

## Filling: FlaskHolder and Dishes

Both are already placed in `wall_layouts.js` today: `FlaskHolder` at Wall 0
`[0,2]` and `[0,3]`, `Dishes` at Wall 0 `[0,1]`. Per Laura: **keep both
FlaskHolder placements as-is** — `[0,2]` holds 3 flasks all filled with
**acid** (red), `[0,3]` holds 3 flasks all filled with **alkaline** (blue).
The single Dishes module holds all 3 dishes, all filled with **powder**
(white). Since every flask/dish within one holder instance holds the same
material, there's no need for a sub-grid here (unlike the Furnace) — each
holder is a single, ordinary "module without sub-functions" with one
room-level `doAction`, same pattern as `Press`'s lever or `Centrifuge`'s
button.

- **FlaskHolder** constructor takes a `{material}` kwarg (`"acid"` or
  `"alkaline"`), passed from `wall_layouts.js`'s per-instance `kwargs`
  (same mechanism already used for `Workbench`'s `contents`). It draws its
  own 3 flask icons (`flask_1/2/3.png`, each with its matching
  `masks/flask_mask_1/2/3.png` tinted to this instance's one material) at
  fixed positions within its own tile — exact fractional offsets aren't
  critical, Laura will adjust them by eye afterward, same as she did for
  the furnace sub-grid icons.
- **Dishes** needs no material kwarg (there's only ever the one material,
  powder) and draws `powder_1/2/3.png` directly on top of the dish sprite
  at fixed offsets — no tinting, these are already final-color art, per
  the original spec.
- **Each holder has 3 independent slots, each starting occupied** (a
  flask/dish icon + contents, all present at game start). Track this as a
  per-slot boolean (or just: 3 small objects each with a `filled` flag),
  not a single whole-module flag — this is what makes each flask/dish
  visually disappear individually rather than the holder emptying all at
  once.
- **doAction (shared logic for both, updated)**: every "do" here is a
  **transfer** of one unit of material out of this holder, to wherever it
  ends up — the beaker, or the floor (a spill). The transfer's destination
  doesn't change whether the source depletes; only whether *something to
  transfer* exists does:
  1. Find this holder's first still-filled slot, in a fixed order (slot 1,
     then 2, then 3 — index order, not random). If **none** are filled
     (all 3 already used), this "do" is a silent no-op — there's nothing
     left to transfer, so nothing happens at all, not even a spill.
  2. Otherwise, that slot's material transfers:
     - If the BeakerHolder's slot holds a Beaker with fewer than 3
       ingredients: append this material to its `ingredients`.
     - If the BeakerHolder's slot holds a Beaker that already has 3
       ingredients: **spill** at the BeakerHolder instead (see below) —
       the material still left this holder, it just didn't make it into
       the beaker.
     - If the BeakerHolder's slot is empty (no beaker present at all):
       **also spill** at the BeakerHolder, same as the full-beaker case.
  3. Either way (fill or either spill variant), **that one slot now empties**
     — stop drawing its flask/dish icon (and its mask, for a flask) from
     this point on. A successful fill and a spill are both just "the
     material transferred somewhere other than back into this slot," so
     the source empties identically in all three cases — this was
     confirmed explicitly, not assumed.

## Spill rendering at the BeakerHolder

- **Liquid spill**: `masks/liquid_spill_beaker_holder_mask.png`, an alpha
  mask tinted to whichever liquid (acid=red or alkaline=blue) just spilled
  — same tinting mechanism as the Beaker/flask masks. Track this as a
  single color-or-null field on the BeakerHolder (e.g.
  `this.liquidSpillColor`); a second liquid spill simply overwrites it with
  the new color (last-spill-wins — there's no stacking of multiple liquid
  spill instances).
- **Powder spill**: `containers/powder_spill_beaker_holder.png`, a flat
  sprite (not tinted — powder only ever has the one appearance), tracked as
  a boolean (`this.powderSpilled`).
- **Draw order**: BeakerHolder's own back → occupant (if any) → front →
  liquid spill (if `liquidSpillColor` set) → powder spill (if
  `powderSpilled`) on top of that. Both spill layers, when present, draw
  **after/in front of** the module's own front sprite — not sandwiched with
  the occupant.
- **Persistence**: once triggered, a spill stays rendered indefinitely for
  this pass — there's no cleanup mechanic yet (see "Scope" above).

## Tinted-mask rendering (new shared primitive)

Masks (`flask_mask_*`, `beaker_mix_mask_*`, `liquid_spill_beaker_holder_mask`)
are **alpha masks, not pre-colored art**: fully transparent where nothing
should be tinted, and a white shape at some alpha > 0 wherever a color should
be filled in. At the color assigned to whatever material occupies that mask,
tint the white regions using canvas compositing (draw the mask image to an
offscreen canvas, `globalCompositeOperation = "source-in"`, fill with the
target color, use the result as the drawn sprite for that layer) — the same
general technique as Version 0 of the game used. Since the color set is
small and fixed (currently just the 3 `MATERIAL_COLORS`), **cache the tinted
result per (mask path, color) pair** the first time it's needed rather than
recompositing every frame, consistent with how every other sprite in this
codebase is loaded once and reused (see `Assets.loadImage`).

## Placement-accepting processing stations (slot only, no processing yet)

Add a placeable slot (empty, `layerIndex` defaulting to "on top of this
module's own sprites" unless a back/front pair calls for sandwiching, same
as BeakerHolder) to each of the following modules, so the Beaker can already
be carried to, set down at, and picked back up from every one of them —
purely as a resting position, with **no behavior wired to the beaker being
there yet**:

`Shelf`, `Electrolyzer`, `Filter`, `Press`, `Furnace`, `Mixer`, `Sink`,
`CompositionScanner` (the analyzer), `PackagingStation`.

Laura will manually tune each slot's `anchorPoint` afterward to make the
beaker look right against each device's actual art — reasonable defaults
(tile center) are fine to start from, don't spend time hand-fitting these
precisely.

## Where this fits in the existing code

- `objects.js`: `ModuleBase` gains `placeableSlots = []`; new `BeakerHolder`
  class; `FlaskHolder`/`Dishes` constructors gain their material handling
  and `doAction`; `Beaker` gains `ingredients`/`form`/rendering; the 9
  processing modules listed above each get one `placeableSlots` entry
  added in their constructors.
- `state.js`: `RoomState` gains `this.inventory = null`; `_performRoomDo`
  gains the placement/pickup priority tiers described above, ahead of its
  existing chain — this sits alongside (doesn't replace) the
  `foregroundOccupantAt` check already added for the Workbench-door fix.
- `renderer.js`: a new tinted-mask draw helper (cached per mask+color); the
  per-module draw path needs to interleave an occupied placeable slot's
  occupant at the right `layerIndex`; a new draw pass for the fixed-position
  inventory square + icon, independent of wall/grid position.
- `assets.js`: `ModuleType.BEAKER_HOLDER` + its `MODULE_SPRITES` entry;
  path constants for the mask/flask/powder/spill assets already present in
  `assets/containers/` and `assets/containers/masks/`; the shared
  `MATERIAL_COLORS` lookup.
- `wall_layouts.js`: add the `BeakerHolder` placement (Wall 0, `[1,3]`);
  add `{material: "acid"}` / `{material: "alkaline"}` kwargs to the
  existing two `FlaskHolder` placements at `[0,2]`/`[0,3]`.
- Verify `FlaskHolder`'s and `Dishes`' actual sprite pixel width against
  the art before assuming each is exactly one tile wide (the existing
  `wall_layouts.js` placements imply one tile each, but confirm rather than
  assume, same caution as the furnace pass).
