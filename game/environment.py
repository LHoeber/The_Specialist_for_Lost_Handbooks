from dataclasses import dataclass
from game.enums import *
from game.objects import *
from game.state import *

class Environment:
    def __init__(self):
        self.state = None
        self.fps = 60
        self.max_time = 600

    def reset(self):
        self.state = self._create_initial_state()

        observation = self.get_observation()

        return observation

    def _create_initial_state(self):
        new_state = GameState()
        new_state.time_remaining = self.max_time
        return new_state
    def step(self, action, elapsed_seconds=None):

        # 1. Apply action
        self._apply_action(action)

        # 2. Advance time and update continuous state
        if elapsed_seconds is None:
            elapsed_seconds = 1 / self.fps
        self._update_continuous_state(elapsed_seconds)

        # 4. Calculate reward
        reward = self._calculate_reward()

        # 5. Check whether episode ended
        terminated = self._check_termination()

        # 6. Generate observation
        observation = self.get_observation()

        info = {}

        return observation, reward, terminated, info

    def update(self, elapsed_seconds):
        """Advance the interactive game clock independently of player input."""
        self._update_continuous_state(elapsed_seconds)
        return self._check_termination()

    
    def _apply_action(self, action):

      if action == Action.ADD_ACID:
          self.state.add_material(Material(Color.RED, MaterialType.ACID))

      elif action == Action.ADD_ALKALINE:
          self.state.add_material(Material(Color.BLUE, MaterialType.ALKALINE))

      elif action == Action.ADD_POWDER:
          self.state.add_material(Material(Color.WHITE, MaterialType.POWDER))

      elif action == Action.MOVE_TO_HEATER:
          self.state.move_container(self.state.mix_container.location,Location.HEATER)

      elif action == Action.MOVE_TO_START:
            self.state.move_container(self.state.mix_container.location,Location.START)

      elif action == Action.MOVE_TO_END:
            self.state.move_container(self.state.mix_container.location,Location.END)

      elif action == Action.MOVE_TO_CENTRIFUGE:
          self.state.move_container(self.state.mix_container.location,Location.CENTRIFUGE)

      elif action == Action.MOVE_TO_PRESS:
          self.state.move_container(self.state.mix_container.location,Location.PRESS)

      elif action == Action.MOVE_TO_BIN:
          self.state.move_container(self.state.mix_container.location,Location.BIN)
          #only emptied, but not broken
          self.state.beaker_available = max(0,self.state.beaker_available-1)
          if self.state.beaker_available>0:
            self.state.mix_container.reset()

      elif action == Action.HEATER_INCREASE:
        self.state.check_heater_level(self.state.heater.level.value+1)
      elif action == Action.HEATER_DECREASE:
          self.state.heater.level = Level(max(self.state.heater.level.value-1,Level.OFF.value))

      elif action == Action.HEATER_OPEN:
          self.state.heater.open =True
          self.state.heater.max_level = Level.MEDIUM
      elif action == Action.HEATER_CLOSE:
          self.state.heater.open = False
          self.state.heater.max_level = Level.HIGH

      elif action == Action.CENTRIFUGE_INCREASE:
           self.state.centrifuge.level = Level(min(self.state.centrifuge.level.value+1,Level.HIGH.value))
      elif action == Action.CENTRIFUGE_DECREASE:
           self.state.centrifuge.level = Level(max(self.state.centrifuge.level.value-1,Level.OFF.value))

      elif action == Action.CENTRIFUGE_START:
           if not(self.state.centrifuge.open):
            self.state.mix_container.mixture.mix()
            self.state.centrifuge.active = True
      elif action == Action.CENTRIFUGE_STOP:
           self.state.centrifuge.active = False

      elif action == Action.CENTRIFUGE_FILL:
          if self.state.centrifuge.open:
              self.state.transfer_mixture(Location.CENTRIFUGE)

      elif action == Action.CENTRIFUGE_EMPTY:
          if self.state.centrifuge.open:
            self.state.transfer_mixture(Location.CONTAINER)

      elif action == Action.CENTRIFUGE_OPEN:
           if not(self.state.centrifuge.active):
            self.state.centrifuge.open = True
      elif action == Action.CENTRIFUGE_CLOSE:
           self.state.centrifuge.open = False

      elif action == Action.PRESS_START:
                self.state.compress_start()
      elif action == Action.PRESS_STOP:
                self.state.compress_stop()

      elif action == Action.PRESS_FILL:
          if self.state.centrifuge.open:
              self.state.transfer_mixture(Location.PRESS)

      elif action == Action.PRESS_EMPTY:
          if self.state.centrifuge.open:
            self.state.transfer_mixture(Location.CONTAINER)
 
    def get_observation(self):
        return {
            "container_location": self.state.mix_container.location,
            "mixture_color_1": self.state.mix_container.mixture.material_1.color,
            "mixture_color_2": self.state.mix_container.mixture.material_2.color,
            "mixture_color_3": self.state.mix_container.mixture.material_3.color,
            "mixture_shape": self.state.mix_container.mixture.shape,
            "heater_level": self.state.heater.level,
            "centrifuge_level": self.state.centrifuge.level,
            "press_level": self.state.press.level,
            "time_remaining": self.state.time_remaining,
            "press_state": "ON" if self.state.press.active else "OFF",
        }

    def _advance_time(self, elapsed_seconds):
        self.state.time_remaining = max(
            0, self.state.time_remaining - elapsed_seconds
        )

    def _update_continuous_state(self, elapsed_seconds):
        self._advance_time(elapsed_seconds)
        self.state.compress_check()
        self.state.check_heater_level()
        
    def _calculate_reward(self):
        return None

    def _check_termination(self):
      if self.state.time_remaining <=0:
        return True
    #   elif self.state.mix_container.location == Location.END:
    #     return True
      elif self.state.beaker_available == 0:
        return True
      else:
        return False
