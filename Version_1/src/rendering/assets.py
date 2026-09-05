"""Sprite loading and the type-to-sprite-filename lookup tables.

Loading requires a display surface to already exist (pygame.display.set_mode),
since sprites are alpha-converted for fast blitting -- callers must construct
the Renderer (which sets up the display) before anything that calls
load_image().
"""

from dataclasses import dataclass
from pathlib import Path

import pygame

from environment.wall_layouts import InteractableType, ModuleType

ASSET_DIR = Path(__file__).resolve().parent.parent.parent / "assets"


@dataclass(frozen=True)
class Sprite:
    """A loaded image plus whether it was drawn with the top-down-perspective
    convention (a 6px top-face strip above the front face -- see
    config.TOP_FACE_OVERHANG). Set explicitly at load time rather than
    guessed from pixel size, since a flat icon could coincidentally be sized
    the same as a headered one."""

    surface: pygame.Surface
    has_overhang: bool = False


def load_image(relative_path, has_overhang=False):
    surface = pygame.image.load(ASSET_DIR / relative_path).convert_alpha()
    return Sprite(surface, has_overhang)


# One sprite list per module type, in back-to-front draw order. Most modules
# are a single sprite; a few (Mixer, Flask holder, Dishes) are modeled as a
# back/front pair so a future mixture-visibility layer can sit between them.
MODULE_SPRITES = {
    ModuleType.FURNACE: ["devices/furnace.png"],
    ModuleType.PRESS: ["devices/press.png"],
    ModuleType.PRESSURE_TANK: ["devices/pressure_tank_big.png"],
    ModuleType.CENTRIFUGE: ["devices/centrifuge.png"],
    ModuleType.MIXER: ["devices/mixer_back.png", "devices/mixer_front.png"],
    ModuleType.PACKAGING_STATION: ["devices/packaging_station.png"],
    ModuleType.FILTER: ["devices/filter.png"],
    ModuleType.FUME_HOOD: ["devices/fume_hood.png"],
    ModuleType.CONNECTOR_BOX: ["devices/connector_box.png"],
    ModuleType.FUSE_BOX: ["devices/fuse_box.png"],
    ModuleType.GENERATOR: ["devices/generator.png"],
    ModuleType.ELECTROLYZER: ["devices/electrolyzer.png"],
    ModuleType.FLASK_HOLDER: [
        "containers/flask_holder_back.png",
        "containers/flask_holder_front.png",
    ],
    ModuleType.DISHES: [
        "containers/dish_holder_back.png",
        "containers/dish_holder_front.png",
    ],
    ModuleType.BIN: ["devices/bin.png"],
    ModuleType.SHELF: ["furniture/shelf_0.png"],
    ModuleType.PIPES_WITH_VALVE: ["devices/pipes_down.png"],
    ModuleType.PRESSURE_TANK_PIPES: ["devices/pressure_tank_big_pipes.png"],
    ModuleType.WIDE_PIPE: ["devices/wide_pipe.png"],
    ModuleType.TOOLBOX: ["devices/toolbox.png"],
    ModuleType.BEAKER_HOLDER: ["containers/beaker_holder.png"],
    ModuleType.SINK: ["devices/sink.png"],
    ModuleType.FAUCET: ["devices/faucet.png"],
    ModuleType.COMPOSITION_SCANNER: ["devices/analyzer.png"],
    ModuleType.CONTROL_PANEL: ["devices/control_panel_off.png"],
    ModuleType.DOOR: ["furniture/door.png"],
    ModuleType.WORKBENCH: ["furniture/counter.png"],
    ModuleType.CLOCK: ["devices/clock.png"],
}

# One default sprite per interactable type. POWER_PLUG is intentionally
# absent: per docs/design/game-prototype.md it isn't placed on any wall yet
# and no sprite has been decided for it.
INTERACTABLE_SPRITES = {
    InteractableType.BUTTON: "indicators/button_off.png",
    InteractableType.LEVER: "indicators/lever_up.png",
    InteractableType.DIAL: "indicators/dial_0.png",
    InteractableType.MOVE_ARROW_LEFT: "indicators/move_left.png",
    InteractableType.MOVE_ARROW_RIGHT: "indicators/move_right.png",
    InteractableType.LEVEL_INDICATOR: "indicators/levels_off.png",
    InteractableType.COMPRESSOR: "devices/counter_compressor.png",
}

BACKGROUND_SPRITES = {
    "wall_tile": "background/wall_tiles.png",
    "floor_tile": "background/floor_plate.png",
    "icon": "background/icon.png",
}

# A Workbench's door has two states rather than one fixed sprite, so it
# doesn't fit INTERACTABLE_SPRITES above -- see objects.CabinetDoor.
CABINET_DOOR_SPRITES = {
    "closed": "furniture/counter_doors_closed.png",
    "open": "furniture/counter_doors_opened.png",
}
