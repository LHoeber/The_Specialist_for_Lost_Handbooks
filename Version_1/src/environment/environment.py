"""Top-level orchestrator tying room state to the rest of the game (mirrors
Version_0's Environment, trimmed to what Phase 1 needs -- no reward/step
loop yet, just room state)."""

from environment.state import RoomState


class Environment:
    def __init__(self):
        self.state = RoomState()

    def reset(self):
        self.state = RoomState()
        return self.state
