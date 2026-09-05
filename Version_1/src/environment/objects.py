"""Module and interactable classes placed on the machine-room walls.

Every concrete class below is a Phase 1 placeholder: it only carries the
structural state (position, sprites) needed to render the room and rotate
between walls. Device-specific behavior (heating, mixing, breakage, ...)
gets added to these classes as each one's mechanics are designed -- see
docs/design/game-prototype.md.
"""

from config import TILE_SIZE, TOP_FACE_OVERHANG
from environment.enums import Direction, InteractableType, ModuleType
from rendering.assets import CABINET_DOOR_SPRITES, INTERACTABLE_SPRITES, MODULE_SPRITES, load_image


class ModuleBase:
    """Shared behavior for every machine module / furniture piece.

    Size is inferred from the module's own (first) sprite: sprites use a
    top-down perspective where a module n cells tall has a sprite
    TILE_SIZE px wide by (38 + (n-1)*32) px tall -- see config.TOP_FACE_OVERHANG.
    """

    module_type = None
    sprite_names = ()

    def __init__(self, wall_index, anchor):
        self.wall_index = wall_index
        self.anchor = anchor  # (row, column) of the top-left occupied cell
        # All module sprites use the top-down-perspective convention.
        self.sprites = [load_image(name, has_overhang=True) for name in self.sprite_names]
        # Relative (row, column) offset of each sprite from the anchor cell;
        # all layers share the same anchor by default (e.g. Mixer's back/
        # front pair), but a module could offset one later if needed.
        self.sprite_offsets = [(0.0, 0.0) for _ in self.sprites]
        # Interactables this module owns (buttons, dials, ...), positioned
        # relative to its own anchor. Empty unless a subclass adds its own.
        self.interactables = []

    @property
    def width_cells(self):
        return self.sprites[0].surface.get_width() / TILE_SIZE

    @property
    def height_cells(self):
        return (self.sprites[0].surface.get_height() - TOP_FACE_OVERHANG) / TILE_SIZE


class Furnace(ModuleBase):
    module_type = ModuleType.FURNACE
    sprite_names = MODULE_SPRITES[ModuleType.FURNACE]

    def __init__(self, wall_index, anchor):
        super().__init__(wall_index, anchor)
        self.interactables = [Dial((1.0, 0.5), parent=self)]


class Press(ModuleBase):
    module_type = ModuleType.PRESS
    sprite_names = MODULE_SPRITES[ModuleType.PRESS]

    def __init__(self, wall_index, anchor):
        super().__init__(wall_index, anchor)
        self.interactables = [Lever((1.0, 0.0), parent=self)]


class PressureTank(ModuleBase):
    module_type = ModuleType.PRESSURE_TANK
    sprite_names = MODULE_SPRITES[ModuleType.PRESSURE_TANK]

    def __init__(self, wall_index, anchor):
        super().__init__(wall_index, anchor)
        self.interactables = [LevelIndicator((0.0, 0.0), parent=self)]


class Centrifuge(ModuleBase):
    module_type = ModuleType.CENTRIFUGE
    sprite_names = MODULE_SPRITES[ModuleType.CENTRIFUGE]

    def __init__(self, wall_index, anchor):
        super().__init__(wall_index, anchor)
        self.interactables = [Button((1.0, 0.0), parent=self)]


class Mixer(ModuleBase):
    module_type = ModuleType.MIXER
    sprite_names = MODULE_SPRITES[ModuleType.MIXER]

    def __init__(self, wall_index, anchor):
        super().__init__(wall_index, anchor)
        self.interactables = [
            Button((1.0, 0.0), parent=self),
            LevelIndicator((1.0, 0.5), parent=self),  # VERIFY: exact offset
        ]


class PackagingStation(ModuleBase):
    module_type = ModuleType.PACKAGING_STATION
    sprite_names = MODULE_SPRITES[ModuleType.PACKAGING_STATION]


class Filter(ModuleBase):
    module_type = ModuleType.FILTER
    sprite_names = MODULE_SPRITES[ModuleType.FILTER]


class FumeHood(ModuleBase):
    module_type = ModuleType.FUME_HOOD
    sprite_names = MODULE_SPRITES[ModuleType.FUME_HOOD]


class ConnectorBox(ModuleBase):
    module_type = ModuleType.CONNECTOR_BOX
    sprite_names = MODULE_SPRITES[ModuleType.CONNECTOR_BOX]


class FuseBox(ModuleBase):
    module_type = ModuleType.FUSE_BOX
    sprite_names = MODULE_SPRITES[ModuleType.FUSE_BOX]


class Generator(ModuleBase):
    module_type = ModuleType.GENERATOR
    sprite_names = MODULE_SPRITES[ModuleType.GENERATOR]


class Electrolyzer(ModuleBase):
    module_type = ModuleType.ELECTROLYZER
    sprite_names = MODULE_SPRITES[ModuleType.ELECTROLYZER]

    def __init__(self, wall_index, anchor):
        super().__init__(wall_index, anchor)
        self.interactables = [Button((1.0, 0.0), parent=self)]


class FlaskHolder(ModuleBase):
    module_type = ModuleType.FLASK_HOLDER
    sprite_names = MODULE_SPRITES[ModuleType.FLASK_HOLDER]


class Dishes(ModuleBase):
    module_type = ModuleType.DISHES
    sprite_names = MODULE_SPRITES[ModuleType.DISHES]


class Bin(ModuleBase):
    module_type = ModuleType.BIN
    sprite_names = MODULE_SPRITES[ModuleType.BIN]


class Shelf(ModuleBase):
    module_type = ModuleType.SHELF
    sprite_names = MODULE_SPRITES[ModuleType.SHELF]


class PipesWithValve(ModuleBase):
    module_type = ModuleType.PIPES_WITH_VALVE
    sprite_names = MODULE_SPRITES[ModuleType.PIPES_WITH_VALVE]

class PressureTankPipes(ModuleBase):
    module_type = ModuleType.PRESSURE_TANK_PIPES
    sprite_names = MODULE_SPRITES[ModuleType.PRESSURE_TANK_PIPES]

class WidePipe(ModuleBase):
    module_type = ModuleType.WIDE_PIPE
    sprite_names = MODULE_SPRITES[ModuleType.WIDE_PIPE]


class Toolbox(ModuleBase):
    module_type = ModuleType.TOOLBOX
    sprite_names = MODULE_SPRITES[ModuleType.TOOLBOX]


class BeakerHolder(ModuleBase):
    module_type = ModuleType.BEAKER_HOLDER
    sprite_names = MODULE_SPRITES[ModuleType.BEAKER_HOLDER]


class Sink(ModuleBase):
    module_type = ModuleType.SINK
    sprite_names = MODULE_SPRITES[ModuleType.SINK]

class Faucet(ModuleBase):
    module_type = ModuleType.FAUCET
    sprite_names = MODULE_SPRITES[ModuleType.FAUCET]

class CompositionScanner(ModuleBase):
    module_type = ModuleType.COMPOSITION_SCANNER
    sprite_names = MODULE_SPRITES[ModuleType.COMPOSITION_SCANNER]


class ControlPanel(ModuleBase):
    module_type = ModuleType.CONTROL_PANEL
    sprite_names = MODULE_SPRITES[ModuleType.CONTROL_PANEL]

class Clock(ModuleBase):
    module_type = ModuleType.CLOCK
    sprite_names = MODULE_SPRITES[ModuleType.CLOCK]


class Door(ModuleBase):
    module_type = ModuleType.DOOR
    sprite_names = MODULE_SPRITES[ModuleType.DOOR]


class Workbench(ModuleBase):
    module_type = ModuleType.WORKBENCH
    sprite_names = MODULE_SPRITES[ModuleType.WORKBENCH]

    def __init__(self, wall_index, anchor, contents=()):
        super().__init__(wall_index, anchor)
        door = CabinetDoor((0.0, 0.0), parent=self)
        # Placeholder: `contents` is just a list of (InteractableType, offset)
        # handed in from wall_layouts.py, hidden until the door opens. Which
        # workbenches get what -- and whether it's randomized -- isn't
        # designed yet; this only proves the door/reveal mechanism works.
        door.contents = [
            INTERACTABLE_CLASSES[content_type](offset, parent=self, visible=False)
            for content_type, offset in contents
        ]
        self.interactables = [*door.contents, door]


MODULE_CLASSES = {
    ModuleType.FURNACE: Furnace,
    ModuleType.PRESS: Press,
    ModuleType.PRESSURE_TANK: PressureTank,
    ModuleType.CENTRIFUGE: Centrifuge,
    ModuleType.MIXER: Mixer,
    ModuleType.PACKAGING_STATION: PackagingStation,
    ModuleType.FILTER: Filter,
    ModuleType.FUME_HOOD: FumeHood,
    ModuleType.CONNECTOR_BOX: ConnectorBox,
    ModuleType.FUSE_BOX: FuseBox,
    ModuleType.GENERATOR: Generator,
    ModuleType.ELECTROLYZER: Electrolyzer,
    ModuleType.FLASK_HOLDER: FlaskHolder,
    ModuleType.DISHES: Dishes,
    ModuleType.BIN: Bin,
    ModuleType.SHELF: Shelf,
    ModuleType.PIPES_WITH_VALVE: PipesWithValve,
    ModuleType.PRESSURE_TANK_PIPES: PressureTankPipes,
    ModuleType.WIDE_PIPE: WidePipe,
    ModuleType.TOOLBOX: Toolbox,
    ModuleType.BEAKER_HOLDER: BeakerHolder,
    ModuleType.SINK: Sink,
    ModuleType.FAUCET: Faucet,
    ModuleType.COMPOSITION_SCANNER: CompositionScanner,
    ModuleType.CONTROL_PANEL: ControlPanel,
    ModuleType.DOOR: Door,
    ModuleType.WORKBENCH: Workbench,
    ModuleType.CLOCK: Clock,
}


class InteractableBase:
    """Shared behavior for a UI element attached to a module (or, for the
    movement arrows, standalone at the room level)."""

    interactable_type = None
    sprite_name = ""
    # Most interactables are flat icons with no top-face strip. Override to
    # True on a subclass whose sprite_name file *does* use that convention
    # (see CabinetDoor for a hand-loaded example, and Compressor below).
    sprite_has_overhang = False

    def __init__(self, offset, parent=None, visible=True):
        self.offset = offset  # (row, column) relative to the parent module's anchor
        self.parent = parent  # a ModuleBase instance, or None for room-level
        self.visible = visible
        self.sprite = (
            load_image(self.sprite_name, has_overhang=self.sprite_has_overhang)
            if self.sprite_name
            else None
        )

    def on_click(self, room_state):
        """Placeholder: concrete interactables override this once their
        specific action is designed. No-op by default."""

    @property
    def anchor(self):
        parent_anchor = self.parent.anchor if self.parent is not None else (0, 0)
        return (parent_anchor[0] + self.offset[0], parent_anchor[1] + self.offset[1])

    @property
    def width_cells(self):
        return self.sprite.surface.get_width() / TILE_SIZE if self.sprite else 0

    @property
    def height_cells(self):
        return self.sprite.surface.get_height() / TILE_SIZE if self.sprite else 0


class Button(InteractableBase):
    interactable_type = InteractableType.BUTTON
    sprite_name = INTERACTABLE_SPRITES[InteractableType.BUTTON]


class Lever(InteractableBase):
    interactable_type = InteractableType.LEVER
    sprite_name = INTERACTABLE_SPRITES[InteractableType.LEVER]


class Dial(InteractableBase):
    interactable_type = InteractableType.DIAL
    sprite_name = INTERACTABLE_SPRITES[InteractableType.DIAL]


class LevelIndicator(InteractableBase):
    interactable_type = InteractableType.LEVEL_INDICATOR
    sprite_name = INTERACTABLE_SPRITES[InteractableType.LEVEL_INDICATOR]


class Compressor(InteractableBase):
    interactable_type = InteractableType.COMPRESSOR
    sprite_name = INTERACTABLE_SPRITES[InteractableType.COMPRESSOR]
    sprite_has_overhang = True  # counter_compressor.png uses the perspective convention


class CabinetDoor(InteractableBase):
    """A container's own door/hatch: toggles open/closed and reveals
    whichever content interactables its owning module attaches afterward
    via `.contents` (see Workbench)."""

    interactable_type = InteractableType.CABINET_DOOR

    def __init__(self, offset, parent=None):
        self.offset = offset
        self.parent = parent
        self.visible = True
        self.open = False
        self.contents = []  # assigned by the owning module after construction
        self._closed_sprite = load_image(CABINET_DOOR_SPRITES["closed"], has_overhang=True)
        self._open_sprite = load_image(CABINET_DOOR_SPRITES["open"], has_overhang=True)
        self.sprite = self._closed_sprite

    def on_click(self, room_state):
        self.open = not self.open
        self.sprite = self._open_sprite if self.open else self._closed_sprite
        for item in self.contents:
            item.visible = self.open


class PowerPlug(InteractableBase):
    """Defined as a type but not yet placed on any wall -- no sprite has
    been decided for it (see docs/design/game-prototype.md)."""

    interactable_type = InteractableType.POWER_PLUG
    sprite_name = ""


class MoveArrowLeft(InteractableBase):
    interactable_type = InteractableType.MOVE_ARROW_LEFT
    sprite_name = INTERACTABLE_SPRITES[InteractableType.MOVE_ARROW_LEFT]

    def on_click(self, room_state):
        room_state.rotate(Direction.LEFT)


class MoveArrowRight(InteractableBase):
    interactable_type = InteractableType.MOVE_ARROW_RIGHT
    sprite_name = INTERACTABLE_SPRITES[InteractableType.MOVE_ARROW_RIGHT]

    def on_click(self, room_state):
        room_state.rotate(Direction.RIGHT)


INTERACTABLE_CLASSES = {
    InteractableType.BUTTON: Button,
    InteractableType.LEVER: Lever,
    InteractableType.DIAL: Dial,
    InteractableType.LEVEL_INDICATOR: LevelIndicator,
    InteractableType.COMPRESSOR: Compressor,
    InteractableType.POWER_PLUG: PowerPlug,
    InteractableType.CABINET_DOOR: CabinetDoor,
    InteractableType.MOVE_ARROW_LEFT: MoveArrowLeft,
    InteractableType.MOVE_ARROW_RIGHT: MoveArrowRight,
}
