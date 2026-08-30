"""
Wall layout definitions for the machine room (Version_1, Phase 1).

Each wall specifies:
  - a list of PlacedDevice entries: (type, anchor) where `anchor` is only the
    device's top-left (row, column) cell. Its full footprint is inferred from
    its sprite's pixel size at render time (width/32, (height-6)/32) -- see
    ModuleBase and the "initialize all objects" row of the Phase 1 spec in
    the Game Prototype Notion page.
  - a list of PlacedInteractable entries: (type, offset, parent_index) where
    `offset` is a (row, column) position relative to its parent device's
    anchor, and `parent_index` is that device's index in the wall's device
    list. The movement arrows are the one standalone case (parent_index=None)
    since they belong to the room, not to a specific device.

Grid convention: (row, column), origin top-left. Each wall is 3 rows (0-2)
wide enough for a 4-column grid (0-3); a 0.5-cell floor strip sits below row 2
but is not part of this module grid.

Wall numbering: the "Wall Designs" diagram in Notion labels walls 1-4;
this file is 0-indexed (WALL_0 = diagram wall 1, WALL_1 = diagram wall 2,
WALL_2 = diagram wall 3, WALL_3 = diagram wall 4), matching the room
orientation mechanics (wall 0 shown initially, sequential 0->1->2->3->0).

"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


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
    TOOLBOX = auto()
    BEAKER_HOLDER = auto()
    SINK = auto()
    FAUCET = auto()
    COMPOSITION_SCANNER = auto()
    CONTROL_PANEL = auto()
    DOOR = auto()
    WORKBENCH = auto()


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
    COMPRESSOR = auto()       # wall 3, "Compressor in Workbench" -- undocumented, verify


@dataclass(frozen=True)
class PlacedDevice:
    type: ModuleType
    anchor: tuple[int, int]  # (row, column) of the device's top-left cell


@dataclass(frozen=True)
class PlacedInteractable:
    type: InteractableType
    offset: tuple[float, float]       # (row, column), relative to parent anchor
    parent_index: Optional[int] = None  # index into this wall's device list


# --- Wall 0 (diagram wall 1) ---------------------------------------------

WALL_0_DEVICES = [
    PlacedDevice(ModuleType.SHELF, (0, 1)),          # [0] 
    PlacedDevice(ModuleType.SHELF, (0, 2)),          # [0] 
    PlacedDevice(ModuleType.SHELF, (0, 3)),          # [0] 
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

WALL_0_INTERACTABLES = [
    PlacedInteractable(InteractableType.BUTTON, (1.0, 0.0), parent_index=0),
    PlacedInteractable(InteractableType.LEVEL_INDICATOR, (1.0, 0.5), parent_index=0),  # VERIFY: exact offset
]


# --- Wall 1 (diagram wall 2) ---------------------------------------------

WALL_1_DEVICES = [
    PlacedDevice(ModuleType.COMPOSITION_SCANNER, (0, 0)),  # [0] spans down into row 1; "Mixture/Analyzer/Shutter" labels in diagram are its own state, not a separate object
    PlacedDevice(ModuleType.SHELF, (0, 1)),                # [1]
    PlacedDevice(ModuleType.FUSE_BOX, (0, 3)),              # [2]
    PlacedDevice(ModuleType.PACKAGING_STATION, (1, 1)),     # [3] spans right into column 2
    PlacedDevice(ModuleType.CONTROL_PANEL, (1, 3)),         # [4]
    PlacedDevice(ModuleType.WORKBENCH, (2, 0)),             # [5]
    PlacedDevice(ModuleType.BIN, (2, 1)),                   # [6]
    PlacedDevice(ModuleType.CONNECTOR_BOX, (2, 2)),         # [7]
    PlacedDevice(ModuleType.GENERATOR, (2, 3)),             # [8]
]

WALL_1_INTERACTABLES: list[PlacedInteractable] = [
]


# --- Wall 2 (diagram wall 3) ---------------------------------------------

WALL_2_DEVICES = [
    PlacedDevice(ModuleType.SHELF, (0, 0)),               # [0] 
    PlacedDevice(ModuleType.SHELF, (0, 1)),                # [1]
    PlacedDevice(ModuleType.PIPES_WITH_VALVE, (0, 2)),     # [2] spans down into row 1
    PlacedDevice(ModuleType.FILTER, (0, 3)),               # [3] spans down into row 1
    PlacedDevice(ModuleType.CENTRIFUGE, (1, 0)),           # [4]
    PlacedDevice(ModuleType.ELECTROLYZER, (1, 1)),         # [5]
    PlacedDevice(ModuleType.PRESS, (1, 2)),                # [6]
    PlacedDevice(ModuleType.WORKBENCH, (2, 0)),            # [7]
    PlacedDevice(ModuleType.WORKBENCH, (2, 1)),            # [8]
    PlacedDevice(ModuleType.WORKBENCH, (2, 2)),            # [9]
]

WALL_2_INTERACTABLES = [
    PlacedInteractable(InteractableType.BUTTON, (1.0, 0.0), parent_index=4),        # on Centrifuge
    PlacedInteractable(InteractableType.BUTTON, (1.0, 0.0), parent_index=5),        # on Electrolyzer
    PlacedInteractable(InteractableType.LEVER, (1.0, 0.0), parent_index=6),         # on Press
]


# --- Wall 3 (diagram wall 4) ---------------------------------------------

WALL_3_DEVICES = [
    PlacedDevice(ModuleType.PRESSURE_TANK, (0, 0)),   # [0]
    PlacedDevice(ModuleType.SHELF, (0, 1)),            # [1]
    PlacedDevice(ModuleType.FUME_HOOD, (0, 2)),        # [2]
    PlacedDevice(ModuleType.FUME_HOOD, (0, 3)),        # [3]
    PlacedDevice(ModuleType.PIPES_WITH_VALVE, (1, 0)), # [4]
    PlacedDevice(ModuleType.SINK, (2, 1)),              # [5]
    PlacedDevice(ModuleType.FAUCET, (1, 1)),              # [6]
    PlacedDevice(ModuleType.FURNACE, (1, 2)),           # [7]
    PlacedDevice(ModuleType.WORKBENCH, (2, 0)),         # [8]
]

WALL_3_INTERACTABLES = [
    PlacedInteractable(InteractableType.LEVEL_INDICATOR, (0.0, 0.0), parent_index=0),  #
    PlacedInteractable(InteractableType.DIAL, (1.0, 0.5), parent_index=6),              #
    PlacedInteractable(InteractableType.COMPRESSOR, (0.5, 0.0), parent_index=7),        # inside workbench, only visible if open
]


WALLS = [
    (WALL_0_DEVICES, WALL_0_INTERACTABLES),
    (WALL_1_DEVICES, WALL_1_INTERACTABLES),
    (WALL_2_DEVICES, WALL_2_INTERACTABLES),
    (WALL_3_DEVICES, WALL_3_INTERACTABLES),
]

# The movement arrows are standalone room-level interactables, not attached
# they sit at the wall's middle row, leftmost and rightmost columns.
ROOM_INTERACTABLES = [
    PlacedInteractable(InteractableType.MOVE_ARROW_LEFT, (1, 0), parent_index=None),
    PlacedInteractable(InteractableType.MOVE_ARROW_RIGHT, (1, 3), parent_index=None),
]
