"""Module and interactable classes placed on the machine-room walls.

Every concrete class below is a Phase 1 placeholder: it only carries the
structural state (position, sprites) needed to render the room and rotate
between walls. Device-specific behavior (heating, mixing, breakage, ...)
gets added to these classes as each one's mechanics are designed -- see
docs/design/game-prototype.md.
"""

from config import TILE_SIZE, TOP_FACE_OVERHANG
from environment.enums import Direction, InteractableType, ModuleType
from rendering.assets import INTERACTABLE_SPRITES, MODULE_SPRITES, load_image


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
        self.sprites = [load_image(name) for name in self.sprite_names]
        # Relative (row, column) offset of each sprite from the anchor cell;
        # all layers share the same anchor by default (e.g. Mixer's back/
        # front pair), but a module could offset one later if needed.
        self.sprite_offsets = [(0.0, 0.0) for _ in self.sprites]

    @property
    def width_cells(self):
        return self.sprites[0].get_width() / TILE_SIZE

    @property
    def height_cells(self):
        return (self.sprites[0].get_height() - TOP_FACE_OVERHANG) / TILE_SIZE


class Furnace(ModuleBase):
    module_type = ModuleType.FURNACE
    sprite_names = MODULE_SPRITES[ModuleType.FURNACE]


class Press(ModuleBase):
    module_type = ModuleType.PRESS
    sprite_names = MODULE_SPRITES[ModuleType.PRESS]


class PressureTank(ModuleBase):
    module_type = ModuleType.PRESSURE_TANK
    sprite_names = MODULE_SPRITES[ModuleType.PRESSURE_TANK]


class Centrifuge(ModuleBase):
    module_type = ModuleType.CENTRIFUGE
    sprite_names = MODULE_SPRITES[ModuleType.CENTRIFUGE]


class Mixer(ModuleBase):
    module_type = ModuleType.MIXER
    sprite_names = MODULE_SPRITES[ModuleType.MIXER]


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


class Door(ModuleBase):
    module_type = ModuleType.DOOR
    sprite_names = MODULE_SPRITES[ModuleType.DOOR]


class Workbench(ModuleBase):
    module_type = ModuleType.WORKBENCH
    sprite_names = MODULE_SPRITES[ModuleType.WORKBENCH]


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
    ModuleType.TOOLBOX: Toolbox,
    ModuleType.BEAKER_HOLDER: BeakerHolder,
    ModuleType.SINK: Sink,
    ModuleType.FAUCET: Faucet,
    ModuleType.COMPOSITION_SCANNER: CompositionScanner,
    ModuleType.CONTROL_PANEL: ControlPanel,
    ModuleType.DOOR: Door,
    ModuleType.WORKBENCH: Workbench,
}


class InteractableBase:
    """Shared behavior for a UI element attached to a module (or, for the
    movement arrows, standalone at the room level)."""

    interactable_type = None
    sprite_name = ""

    def __init__(self, offset, parent=None, visible=True):
        self.offset = offset  # (row, column) relative to the parent module's anchor
        self.parent = parent  # a ModuleBase instance, or None for room-level
        self.visible = visible
        self.sprite = load_image(self.sprite_name) if self.sprite_name else None

    def on_click(self, room_state):
        """Placeholder: concrete interactables override this once their
        specific action is designed. No-op by default."""

    @property
    def anchor(self):
        parent_anchor = self.parent.anchor if self.parent is not None else (0, 0)
        return (parent_anchor[0] + self.offset[0], parent_anchor[1] + self.offset[1])

    @property
    def width_cells(self):
        return self.sprite.get_width() / TILE_SIZE if self.sprite else 0

    @property
    def height_cells(self):
        return self.sprite.get_height() / TILE_SIZE if self.sprite else 0


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
    InteractableType.MOVE_ARROW_LEFT: MoveArrowLeft,
    InteractableType.MOVE_ARROW_RIGHT: MoveArrowRight,
}
