"""
Wall layout definitions for the machine room (Version_1, Phase 1).

Each wall is just a list of PlacedDevice entries: (type, anchor, kwargs) where
`anchor` is the device's top-left (row, column) cell -- its full footprint is
inferred from its sprite's pixel size at render time (width/32,
(height-6)/32), see ModuleBase -- and `kwargs` is an optional dict of extra
constructor arguments for the rare device that needs per-instance
configuration (e.g. a specific Workbench's hidden contents; see
objects.Workbench). Leave `kwargs` unset everywhere else.

A device's own interactables (buttons, dials, ...) are NOT listed here --
each module class builds the ones intrinsic to it in its own __init__ (e.g.
every Centrifuge owns a Button), so there is nothing to keep in sync with
this file when devices are added, removed or reordered. The only
interactables still declared as data are the room-level ones with no device
of their own -- see ROOM_INTERACTABLES at the bottom.

Grid convention: (row, column), origin top-left. Each wall is 3 rows (0-2)
wide enough for a 4-column grid (0-3); a 0.5-cell floor strip sits below row 2
but is not part of this module grid.

Wall numbering: the "Wall Designs" diagram in Notion labels walls 1-4;
this file is 0-indexed (WALL_0 = diagram wall 1, WALL_1 = diagram wall 2,
WALL_2 = diagram wall 3, WALL_3 = diagram wall 4), matching the room
orientation mechanics (wall 0 shown initially, sequential 0->1->2->3->0).

"""

from dataclasses import dataclass, field
from enum import Enum, auto


class ModuleType(Enum):
    """Machine modules / devices. See the "Machine modules" table in the
    Game Prototype Notion page for each type's states, actions and size.
    DOOR and WORKBENCH are plain furniture pieces that show up in the wall
    diagrams but aren't part of that table."""
    FURNACE = auto()
    PRESS = auto()
    PRESSURE_TANK = auto()
    CENTRIFUGE = auto()
    MIXER = auto()
    PACKAGING_STATION = auto()
    FILTER = auto()
    FUME_HOOD = auto()
    CONNECTOR_BOX = auto()
    FUSE_BOX = auto()
    GENERATOR = auto()
    ELECTROLYZER = auto()
    FLASK_HOLDER = auto()
    DISHES = auto()
    BIN = auto()
    SHELF = auto()
    PIPES_WITH_VALVE = auto()
    PRESSURE_TANK_PIPES = auto()
    WIDE_PIPE = auto()
    TOOLBOX = auto()
    BEAKER_HOLDER = auto()
    SINK = auto()
    FAUCET = auto()
    COMPOSITION_SCANNER = auto()
    CONTROL_PANEL = auto()
    DOOR = auto()
    WORKBENCH = auto()
    CLOCK = auto()


class InteractableType(Enum):
    """Small UI elements attached to a device (or, for the movement arrows,
    standalone at the room level). See the "Interactables" table in the
    Game Prototype Notion page. LEVEL_INDICATOR, POWER_PLUG and COMPRESSOR
    appear in the wall diagrams but aren't described in that table yet --
    worth adding their states/actions there once their behavior is defined."""
    BUTTON = auto()
    LEVER = auto()
    DIAL = auto()
    MOVE_ARROW_LEFT = auto()
    MOVE_ARROW_RIGHT = auto()
    LEVEL_INDICATOR = auto()  # "Levels" (wall 0) / "Pressure Indicator" (wall 3) -- undocumented, verify
    POWER_PLUG = auto()       # wall 2 -- undocumented, verify
    COMPRESSOR = auto()       # a possible Workbench content -- undocumented, verify
    CABINET_DOOR = auto()     # a Workbench's own door; see objects.Workbench/CabinetDoor


@dataclass(frozen=True)
class PlacedDevice:
    type: ModuleType
    anchor: tuple[int, int]  # (row, column) of the device's top-left cell
    kwargs: dict = field(default_factory=dict)  # extra per-instance constructor args, rarely needed


@dataclass(frozen=True)
class PlacedInteractable:
    type: InteractableType
    offset: tuple[float, float]  # (row, column), relative to the room origin


# --- Wall 0 (diagram wall 1) ---------------------------------------------

WALL_0_DEVICES = [
    PlacedDevice(ModuleType.SHELF, (0, 1)),          # [0] 
    PlacedDevice(ModuleType.SHELF, (0, 2)),          # [0] 
    PlacedDevice(ModuleType.SHELF, (0, 3)),          # [0] 
    PlacedDevice(ModuleType.SHELF, (1, 0)),          # [0] 
    PlacedDevice(ModuleType.MIXER, (1, 0)),          # [1] spans down into row 1
    PlacedDevice(ModuleType.DISHES, (0, 1)),         # [2]
    PlacedDevice(ModuleType.FLASK_HOLDER, (0, 2)),   # [3]
    PlacedDevice(ModuleType.FLASK_HOLDER, (0, 3)),   # [4]
    PlacedDevice(ModuleType.SHELF, (1, 1)),          # [5]
    PlacedDevice(ModuleType.DOOR, (1, 2)),           # [6] spans down into row 2
    PlacedDevice(ModuleType.BEAKER_HOLDER, (1, 3)),  # [7]
    PlacedDevice(ModuleType.TOOLBOX, (2, 0)),        # [8]
    PlacedDevice(ModuleType.WORKBENCH, (2, 3)),      # [9]
]

# --- Wall 1 (diagram wall 2) ---------------------------------------------

WALL_1_DEVICES = [
    PlacedDevice(ModuleType.COMPOSITION_SCANNER, (0, 0)),  # [0] spans down into row 1; "Mixture/Analyzer/Shutter" labels in diagram are its own state, not a separate object
    PlacedDevice(ModuleType.SHELF, (0, 1)),                # [1]
    PlacedDevice(ModuleType.FUSE_BOX, (0, 3)),              # [2]
    PlacedDevice(ModuleType.SHELF, (1, 1)),                # [1]
    PlacedDevice(ModuleType.SHELF, (1, 2)),                # [1]
    PlacedDevice(ModuleType.PACKAGING_STATION, (1, 1)),     # [3] spans right into column 2
    PlacedDevice(ModuleType.CONTROL_PANEL, (1, 3)),         # [4]
    PlacedDevice(ModuleType.WORKBENCH, (2, 0)),             # [5]
    PlacedDevice(ModuleType.BIN, (2, 1)),                   # [6]
    PlacedDevice(ModuleType.CONNECTOR_BOX, (2, 2)),         # [7]
    PlacedDevice(ModuleType.GENERATOR, (2, 3)),             # [8]
]

# --- Wall 2 (diagram wall 3) ---------------------------------------------

WALL_2_DEVICES = [
    PlacedDevice(ModuleType.SHELF, (0, 0)),               # [0] 
    PlacedDevice(ModuleType.SHELF, (0, 1)),                # [1]
    PlacedDevice(ModuleType.CLOCK, (0, 1)),                # [1]
    PlacedDevice(ModuleType.WIDE_PIPE, (0, 3)),     # [2] spans down into row 1
    PlacedDevice(ModuleType.FILTER, (0, 2)),               # [3] spans down into row 1
    PlacedDevice(ModuleType.CENTRIFUGE, (1, 0)),           # [4]
    PlacedDevice(ModuleType.ELECTROLYZER, (1, 1)),         # [5]
    PlacedDevice(ModuleType.PRESS, (1, 3)),                # [6]
    PlacedDevice(ModuleType.WORKBENCH, (2, 0)),            # [7]
    PlacedDevice(ModuleType.WORKBENCH, (2, 1)),            # [8]
    PlacedDevice(ModuleType.WORKBENCH, (2, 2)),            # [9]
]

# --- Wall 3 (diagram wall 4) ---------------------------------------------

WALL_3_DEVICES = [
    PlacedDevice(ModuleType.PRESSURE_TANK, (0, 0)),   # [0]
    PlacedDevice(ModuleType.PRESSURE_TANK_PIPES, (0, 0)),   # [0]
    PlacedDevice(ModuleType.SHELF, (0, 1)),            # [1]
    PlacedDevice(ModuleType.FUME_HOOD, (0, 2)),        # [2]
    PlacedDevice(ModuleType.FUME_HOOD, (0, 3)),        # [3]
    PlacedDevice(ModuleType.PIPES_WITH_VALVE, (1, 0)), # [4]
    PlacedDevice(ModuleType.SINK, (2, 1)),              # [5]
    PlacedDevice(ModuleType.FAUCET, (1, 1)),              # [6]
    PlacedDevice(ModuleType.FURNACE, (1, 2)),           # [7]
    # Placeholder content assignment: this is the one Workbench with
    # something hidden behind its door. Which workbenches get what (and
    # whether it's randomized) isn't designed yet -- see objects.Workbench.
    PlacedDevice(
        ModuleType.WORKBENCH, (2, 0),
        kwargs={"contents": [(InteractableType.COMPRESSOR, (0.0, 0.0))]},
    ),  # [8]
]


WALLS = [
    WALL_0_DEVICES,
    WALL_1_DEVICES,
    WALL_2_DEVICES,
    WALL_3_DEVICES,
]

# The movement arrows are standalone room-level interactables, not attached
# to a device. They sit at the wall's middle row, in the half-cell side
# margins outside the 4-column device grid (column -0.5 and 3.5), so they
# never overlap a placed module.
ROOM_INTERACTABLES = [
    PlacedInteractable(InteractableType.MOVE_ARROW_LEFT, (1, -0.5)),
    PlacedInteractable(InteractableType.MOVE_ARROW_RIGHT, (1, 3.5)),
]
