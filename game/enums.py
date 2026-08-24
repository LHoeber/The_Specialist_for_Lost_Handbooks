from enum import Enum,auto,IntEnum

class GameStatus(Enum):
    MENU = 0
    RUNNING = 1
    GAMEOVER = 2

class MaterialType(Enum):
    POWDER = 0
    ACID = 1
    ALKALINE = 2
    NONE = 3

class Color(Enum):
    RED = 0
    BLUE = 1
    WHITE = 2
    ORANGE = 3
    PURPLE = 4
    LIGHT_BLUE = 6
    LAVENDER = 7
    YELLOW = 8
    BLACK = 9
    PINK = 10

class Shape(Enum):
    DIAMOND = 0
    RUBY = 1
    BLOCK = 2
    LIQUID = 3

class Level(IntEnum):
    OFF= 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    ABOVE_ALL = 4

class ContainerType(Enum):
    TUBE = 0
    BEAKER = 1

class Location(Enum):
    START = 0
    END = 1
    HEATER = 2
    CENTRIFUGE = 3
    PRESS = 4
    BIN = 5
    SHELF = 6
    ACID = 7
    ALKALINE = 8
    POWDER = 9
    CONTAINER = 10

class Action(Enum):
    ADD_ACID = auto()
    ADD_ALKALINE = auto()
    ADD_POWDER = auto()

    MOVE_TO_START = auto()
    MOVE_TO_END = auto()
    MOVE_TO_HEATER = auto()
    MOVE_TO_CENTRIFUGE = auto()
    MOVE_TO_PRESS = auto()
    MOVE_TO_PRESENTATION = auto()
    MOVE_TO_BIN = auto()

    HEATER_INCREASE= auto()
    HEATER_DECREASE = auto()
    HEATER_OPEN= auto()
    HEATER_CLOSE = auto()
    HEATER_LEVEL_CYCLE = auto()

    CENTRIFUGE_INCREASE = auto()
    CENTRIFUGE_DECREASE = auto()
    CENTRIFUGE_LEVEL_CYCLE = auto()

    CENTRIFUGE_START = auto()
    CENTRIFUGE_STOP = auto()    
    CENTRIFUGE_OPEN = auto()
    CENTRIFUGE_CLOSE = auto()
    CENTRIFUGE_FILL = auto()
    CENTRIFUGE_EMPTY = auto()

    SET_PRESS_SHAPE_INCREASE = auto()
    SET_PRESS_SHAPE_DECREASE = auto()

    PRESS_START = auto()
    PRESS_STOP = auto()
    PRESS_LEVEL_CYCLE = auto()
    PRESS_OPEN = auto()
    PRESS_CLOSE = auto()    
    PRESS_FILL = auto()
    PRESS_EMPTY = auto()

    HEATER_CLEAN = auto()
    CENTRIFUGE_CLEAN = auto()
    PRESS_CLEAN = auto()