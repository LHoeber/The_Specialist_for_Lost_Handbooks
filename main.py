import pygame
from queue import Empty, Queue
from threading import Thread

from game.environment import Environment
from game.enums import Action
from rendering.renderer import Renderer


def print_observation(obs):
    print("\n--- GAME STATE ---")
    for key, value in obs.items():
        print(f"{key}: {value}")


def main():
    pygame.init()

    env = Environment()
    renderer = Renderer()

    observation = env.reset()

    renderer.render(env.state)
    print_observation(observation)

    commands = Queue()

    def read_commands():
        while True:
            try:
                commands.put(input("\nAction: ").strip())
            except EOFError:
                commands.put(None)
                return

    Thread(target=read_commands, daemon=True).start()

    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    renderer.toggle_debug_grid()

            elapsed_seconds = renderer.clock.tick(env.fps) / 1000
            if env.update(elapsed_seconds):
                print("GAME OVER")
                running = False

            try:
                command = commands.get_nowait()
            except Empty:
                command = None

            if command is not None:
                try:
                    action = Action[command.upper()]
                except KeyError:
                    print("Unknown action.")
                    print("Available actions:")
                    for available_action in Action:
                        print(" ", available_action.name)
                else:
                    observation, reward, terminated, info = env.step(
                        action, elapsed_seconds=0
                    )
                    print_observation(observation)
                    print("Reward:", reward)
                    if terminated:
                        print("GAME OVER")
                        running = False

            renderer.render(env.state)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()