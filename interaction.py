from dataclasses import dataclass

import pygame

from game.enums import Action, Location


@dataclass
class DragState:
    pointer_offset: tuple[float, float]
    origin_location: Location


class MouseInteraction:
    """Translate mouse drags into the same actions exposed to agents."""

    DROP_ACTIONS = {
        Location.START: Action.MOVE_TO_START,
        Location.END: Action.MOVE_TO_END,
        Location.HEATER: Action.MOVE_TO_HEATER,
        Location.CENTRIFUGE: Action.MOVE_TO_CENTRIFUGE,
        Location.PRESS: Action.MOVE_TO_PRESS,
    }

    def __init__(self):
        self.drag: DragState | None = None

    def handle_event(self, event, env, renderer):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start_drag(event.pos, env, renderer)
        elif event.type == pygame.MOUSEMOTION and self.drag is not None:
            self._update_drag(event.pos, renderer)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            return self._finish_drag(event.pos, env, renderer)
        return None

    def _start_drag(self, screen_pos, env, renderer):
        if env.state.mix_container.location == Location.BIN:
            return

        game_pos = renderer.screen_to_game_transform(screen_pos)
        beaker_rect = renderer.get_container_rect(env.state)
        if not beaker_rect.collidepoint(game_pos):
            return

        self.drag = DragState(
            #position relative to the beaker's origin
            pointer_offset=(game_pos[0] - beaker_rect.x, game_pos[1] - beaker_rect.y),
            #beaker's origin at the start of the drag
            origin_location=env.state.mix_container.location,
        )
        renderer.set_drag_position(
            (beaker_rect.x, beaker_rect.y),
        )

    def _update_drag(self, screen_pos, renderer):
        game_pos = renderer.screen_to_game_transform(screen_pos)
        x = game_pos[0] - self.drag.pointer_offset[0]
        y = game_pos[1] - self.drag.pointer_offset[1]
        renderer.set_drag_position((x, y))

    def _finish_drag(self, screen_pos, env, renderer):
        if self.drag is None:
            return None

        game_pos = renderer.screen_to_game_transform(screen_pos)
        target_location = renderer.location_at(game_pos)
        action = self.DROP_ACTIONS.get(target_location)
        self.drag = None
        renderer.clear_drag_position()

        if action is None:
            return None

        observation, reward, terminated, info = env.step(action, elapsed_seconds=0)
        return observation, reward, terminated, info