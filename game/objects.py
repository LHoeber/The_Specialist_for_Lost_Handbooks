from dataclasses import dataclass,field
from game.enums import *
import random

@dataclass
class Material:
  color: Color | None = None
  material_type: MaterialType | None = None

@dataclass
class Mixture:
  material_1: Material = field(default_factory=Material)
  material_2: Material = field(default_factory=Material)
  material_3: Material = field(default_factory=Material)
  mixed: bool = False
  shape: Shape = Shape.LIQUID
  current_container: Location = Location.CONTAINER

  def empty(self):
    self.material_1 = Material()
    self.material_2 = Material()
    self.material_3 = Material()

  def add(self, new_material: Material) -> bool:
      if self.material_1.color is None:
          self.material_1 = new_material
          return True

      if self.material_2.color is None:
          self.material_2 = new_material
          return True

      if self.material_3.color is None:
          self.material_3 = new_material
          return True

      return False

  mix_color_assignment = {
    Color.PURPLE: [MaterialType.ALKALINE,MaterialType.ACID],
    Color.LIGHT_BLUE: [MaterialType.POWDER,MaterialType.ALKALINE],
    Color.PINK: [MaterialType.POWDER,MaterialType.ACID],
    Color.LAVENDER:[MaterialType.POWDER,MaterialType.ACID,MaterialType.ALKALINE],
  }

  heat_color_assignment = {
    Color.ORANGE: [MaterialType.ALKALINE,MaterialType.ACID],
    Color.PURPLE: [MaterialType.POWDER,MaterialType.ACID,MaterialType.ALKALINE],
  }

  def mix(self):
    materials = [self.material_1,self.material_2,self.material_3]
    material_types = {material.material_type for material in materials if material.material_type is not None}

    if not(self.mixed):
      #TODO: ignore None materials
      for result_color, mix in self.mix_color_assignment.items():
        if set(mix)==material_types:
          for material in materials:
            if material.color is not None:
              material.color = result_color
      self.mixed = True

  def heat(self,level: Level):
    materials = [self.material_1,self.material_2,self.material_3]
    material_types = {material.material_type for material in materials if material is not None}
    #if level is too high, burn everything
    if level>=Level.HIGH:
      for material in materials:
        material.color = Color.BLACK
    #if materials are already mixed, react to other colors
    elif self.mixed:
      for result_color, mix in self.heat_color_assignment.items():
        if set(mix)==material_types:
          for material in materials:
            material.color = result_color



@dataclass
class Container:
  type: ContainerType = ContainerType.BEAKER
  heat_stability: Level = random.choice([Level.MEDIUM,Level.HIGH,Level.ABOVE_ALL])
  centrifuge_stability: Level= random.choice(list(Level))
  compression_time_max: float= 1+random.random()*10
  compression_time_start: float = 0
  mixture: Mixture = field(default_factory=Mixture)
  location: Location = Location.START

  def reset(self):
   self.location = Location.START
   self.mixture.empty()

@dataclass
class Bin:
  pass

@dataclass
class Heater:
  level: Level = Level.OFF
  to_clean: bool = False
  open: bool = False
  max_level: Level = Level.HIGH
  
@dataclass
class Centrifuge:
  level: Level = Level.OFF
  to_clean: bool = False
  open: bool = False
  active: bool = False

@dataclass
class Press:
  level: Level = Level.OFF
  leaking: bool = False
  to_clean: bool = False
  shape: Shape = Shape.LIQUID
  active: bool = False


