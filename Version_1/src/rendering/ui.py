"""Direct player input: translates mouse clicks into interactable actions."""

import pygame


class UIController:
    def __init__(self, renderer):
        self.renderer = renderer

    def handle_event(self, event, room_state):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            logical_pos = self.renderer.screen_to_logical(event.pos)
            interactable = self.renderer.find_interactable_at(logical_pos, room_state)
            if interactable is not None:
                interactable.on_click(room_state)
