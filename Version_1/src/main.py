"""Entry point: wires the environment, renderer, and UI input together."""

import pygame

from config import FPS
from environment.environment import Environment
from rendering.renderer import Renderer
from rendering.ui import UIController


def main():
    # Renderer first: it sets up the display, which sprite loading (done
    # while building the environment's modules) depends on.
    renderer = Renderer()
    env = Environment()
    ui = UIController(renderer)

    clock = pygame.time.Clock()
    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    renderer.handle_resize(event.size)
                else:
                    ui.handle_event(event, env.state)

            renderer.render(env.state)
            clock.tick(FPS)#limits frame rate to max FPS frames per second
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
