from dataclasses import dataclass, field
from game.enums import *
from game.objects import *
from rendering.renderer import center_offsets

@dataclass
class GameState:
    status: GameStatus = GameStatus.RUNNING
    
    # Ingredients
    powder_available: int = 3
    acid_available: int = 3
    alkaline_available: int = 3
    beaker_available: int = 3

    # Container for the main mixture handling
    mix_container: Container = field(default_factory=Container)

    # Heater
    heater: Heater = field(default_factory=Heater)
    # Centrifuge
    centrifuge: Centrifuge = field(default_factory=Centrifuge)
    # Press
    press: Press = field(default_factory=Press)
    # Bin
    bin: Bin = field(default_factory=Bin)

    # Resources
    time_remaining: float = 0
    money_remaining: float = 0

        
    def check_heater_level(self,level_new: Level = None):
        container = self.mix_container
        if level_new == None:
          level_new = self.heater.level

        level_new = Level(min(level_new,self.heater.max_level.value))
        self.heater.level = level_new

        if container.location==Location.HEATER:
          if level_new.value>=container.heat_stability.value:
              container.reset()
              self.beaker_available = max(0,self.beaker_available-1)
              self.heater.to_clean = True
          else:
            container.mixture.heat(level_new)

    def mix(self,level: Level):
        container = self.mix_container
        if container.location==Location.CENTRIFUGE:
          if level.value>=container.centrifuge_stability.value:
            container.reset()
            self.beaker_available = max(0,self.beaker_available-1)
            self.centrifuge.to_clean = True
          else:
            container.mixture.mix()

    def add_material(self,material: Material):
      if self.mix_container.location==Location.START:
        added = self.mix_container.mixture.add(material)
        if added:
            if material.material_type == MaterialType.ACID:
              self.acid_available = max(0,self.acid_available-1)
            elif material.material_type == MaterialType.ALKALINE:
              self.alkaline_available = max(0,self.alkaline_available-1)
            else:
              self.powder_available = max(0,self.powder_available-1)

    def transfer_mixture(self,target_loc: Location = Location.CONTAINER):
      if target_loc in [Location.PRESS,Location.CENTRIFUGE]:
        #only move to other location if mixture is currently in container
        if self.mix_container.mixture.current_container == Location.CONTAINER and self.mix_container.location in [target_loc]:
          self.mix_container.mixture.current_container = target_loc
      elif target_loc == Location.CONTAINER and self.mix_container.mixture.current_container == self.mix_container.location:
        #only move back into container, if container is close by
        self.mix_container.mixture.current_container = target_loc
        
    def compress_start(self):
      if self.press.active:
        return

      self.press.active = True
      if self.mix_container.location == Location.PRESS:
        self.mix_container.compression_time_start = self.time_remaining

    def compress_check(self):
      if not self.press.active or self.mix_container.location != Location.PRESS:
        return

      compression_time = (self.mix_container.compression_time_start - self.time_remaining)
      if compression_time > self.mix_container.compression_time_max:
        self.mix_container.reset()
        self.beaker_available = max(0,self.beaker_available-1)
        self.compress_stop()

    def compress_stop(self):
        if self.mix_container.location == Location.PRESS:
          if self.press.shape !=Shape.LIQUID and self.press.level==Level.HIGH:
              self.mix_container.mixture.shape = self.press.shape
        self.press.active = False

    def move_container(self,loc_from: Location, loc_to: Location):
      if loc_from == self.mix_container.location:
        self.mix_container.location = loc_to

