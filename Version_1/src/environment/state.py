"""Room state: builds the four walls' modules and interactables once at
startup (so module state can persist across visits once modules have real
behavior) and tracks which wall is currently being viewed."""

from environment.enums import Direction, InteractableType
from environment.objects import INTERACTABLE_CLASSES, MODULE_CLASSES
from environment.wall_layouts import ROOM_INTERACTABLES, WALLS


class Wall:
    """One wall's live modules and interactables, built from its
    wall_layouts.py template."""

    def __init__(self, wall_index, devices, interactables):
        self.modules = [
            MODULE_CLASSES[device.type](wall_index, device.anchor)
            for device in devices
        ]
        self.interactables = []
        for item in interactables:
            parent = (
                self.modules[item.parent_index]
                if item.parent_index is not None
                else None
            )
            # The Compressor sits inside the Workbench and is only meant to
            # be visible once the Workbench can be opened -- that mechanic
            # isn't built yet, so it stays hidden for now.
            visible = item.type != InteractableType.COMPRESSOR
            self.interactables.append(
                INTERACTABLE_CLASSES[item.type](item.offset, parent=parent, visible=visible)
            )


class RoomState:
    """All four walls plus the currently-viewed wall index."""

    def __init__(self):
        self.walls = [
            Wall(index, devices, interactables)
            for index, (devices, interactables) in enumerate(WALLS)
        ]
        # Movement arrows are room-level and identical on every wall, so
        # they're built once here rather than per-wall.
        self.room_interactables = [
            INTERACTABLE_CLASSES[item.type](item.offset, parent=None)
            for item in ROOM_INTERACTABLES
        ]
        self.current_wall_index = 0

    @property
    def current_wall(self):
        return self.walls[self.current_wall_index]

    def rotate(self, direction):
        step = 1 if direction == Direction.RIGHT else -1
        self.current_wall_index = (self.current_wall_index + step) % len(self.walls)
