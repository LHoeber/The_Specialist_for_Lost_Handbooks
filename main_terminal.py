from game.environment import Environment
from game.enums import Action


def print_observation(obs):
    print("\n--- GAME STATE ---")
    for key, value in obs.items():
        print(f"{key}: {value}")


def main():
    env = Environment()

    observation = env.reset()
    print_observation(observation)

    while True:
        command = input("\nAction: ")

        try:
            action = Action[command.upper()]
        except KeyError:
            print("Unknown action.")
            print("Available actions:")
            for action in Action:
                print(" ", action.name)
            continue

        observation, reward, terminated, info = env.step(action)

        print_observation(observation)
        print("Reward:", reward)

        if terminated:
            print("GAME OVER")
            break


if __name__ == "__main__":
    main()