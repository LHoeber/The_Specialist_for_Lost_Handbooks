"""Room state: builds the four walls' modules once at startup (so module
state can persist across visits once modules have real behavior) and tracks
which wall is currently being viewed."""

from environment.enums import Direction
from environment.objects import INTERACTABLE_CLASSES, MODULE_CLASSES
from environment.wall_layouts import ROOM_INTERACTABLES, WALLS


class Wall:
    """One wall's live modules, built from its wall_layouts.py device list.
    Each module owns its own interactables (see objects.ModuleBase); this
    just flattens them for rendering/hit-testing."""

    def __init__(self, wall_index, devices):
        self.wall_index = wall_index
        self.modules = [
            MODULE_CLASSES[device.type](wall_index, device.anchor, **device.kwargs)
            for device in devices
        ]
        self.interactables = [
            interactable for module in self.modules for interactable in module.interactables
        ]


class RoomState:
    """All four walls plus the currently-viewed wall index."""

    def __init__(self):
        self.walls = [Wall(index, devices) for index, devices in enumerate(WALLS)]
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
