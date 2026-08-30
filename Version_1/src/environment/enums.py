"""General enums for the game environment.

ModuleType and InteractableType are the wall-placement vocabulary and live
in wall_layouts.py (the machine-readable source of truth for exact
placements, see docs/design/game-prototype.md) -- re-exported here so the
rest of the environment/rendering code can import them from one place
alongside enums that aren't about placement.
"""

from enum import Enum, auto

from environment.wall_layouts import InteractableType, ModuleType

__all__ = ["ModuleType", "InteractableType", "Direction"]


class Direction(Enum):
    """Which way the player rotates through the room's four walls."""

    LEFT = auto()
    RIGHT = auto()
