import pygame
from dotmap import DotMap
from collections import defaultdict
from rendering.assets import *
from types import SimpleNamespace

from game.enums import (
    Location,
    Color,
    GameStatus,
    Shape,
    Level
)
#### Helpers ####
def scale_by_factor(surface, factor):
    w, h = surface.get_size()
    new_size = (int(w * factor), int(h * factor))
    return pygame.transform.scale(surface, new_size)

def tint_mask(mask_surface, color):
    # Create a solid color surface
    color_surface = pygame.Surface(mask_surface.get_size(), pygame.SRCALPHA)
    color_surface.fill(color)

    # Multiply color with mask alpha
    tinted = mask_surface.copy()
    tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return tinted


class AutoNamespace:
    def __init__(self):
        pass
    def __getattr__(self, name):
        value = AutoNamespace()
        setattr(self, name, value)
        return value
####    ####
INITIAL_LOGICAL_WIDTH = 1000
INITIAL_LOGICAL_HEIGHT = 700

INITIAL_SCALE =0.5
GLOBAL_FACTOR = 3

COLOR_RGB = {
    Color.WHITE: (255,255,255),
    Color.RED: (220, 40, 40),
    Color.BLUE: (50, 100, 220),
    Color.WHITE: (245, 245, 245),
    Color.PURPLE: (150, 70, 180),
    Color.LIGHT_BLUE: (100, 180, 230),
    Color.LAVENDER: (190, 150, 220),
    Color.ORANGE: (240, 150, 40),
    Color.YELLOW: (240, 220, 50),
    Color.PINK: (240, 130, 170),
    Color.BLACK: (20, 20, 20),
    None: None
}
sizes = {
    Location.CENTRIFUGE: {"x": 220, "y": 200},
    Location.HEATER:     {"x": 220, "y": 200},
    Location.PRESS:      {"x": 220, "y": 200},
    Location.START:      {"x": 100, "y": 100},
    Location.END:        {"x": 100, "y": 100},
    "mix_container": {"x": 60, "y": 80},
}

positions = {
    Location.CENTRIFUGE: {"x": 400, "y": 60},
    Location.HEATER:     {"x": 380, "y": 250},
    Location.PRESS:      {"x": 680, "y": 250},
    Location.BIN:        {"x": 250, "y": 520},
    Location.SHELF:      {"x": 0, "y": 120},
    Location.START:      {"x": 250, "y": 400},
    Location.END:        {"x": 800, "y": 400},
}
center_offsets = defaultdict(lambda: {"x":0,"y":0},{
    Location.CENTRIFUGE: {"x": 150, "y": 150},
    Location.HEATER:     {"x": 85, "y": 133},
    Location.PRESS:      {"x": 50, "y": 50},
    Location.BIN:        {"x": 50, "y": 50},
    Location.SHELF:      {"x": 0, "y": 0},
    Location.START:      {"x": 0, "y": 0},
    Location.END:        {"x": 0, "y": 0},
})

positions = DotMap(positions)
sizes =DotMap(sizes)
center_offsets = DotMap(center_offsets)

#relative positions
rel_shelf = positions[Location.SHELF]
positions[Location.ACID] =         {"x": rel_shelf.x+45, "y": rel_shelf.y+65}
positions[Location.ALKALINE] =         {"x": rel_shelf.x+45, "y": rel_shelf.y+185}
positions[Location.POWDER] =         {"x": rel_shelf.x+30, "y": rel_shelf.y+340}
positions = DotMap(positions)
sizes =DotMap(sizes)
 
class Renderer:

    def __init__(self, scale = INITIAL_SCALE):
     
        self.SCALE = scale
        self.LOGICAL_WIDTH = INITIAL_LOGICAL_WIDTH
        self.LOGICAL_HEIGHT = INITIAL_LOGICAL_HEIGHT

        # Internal game resolution
        self.game_surface = pygame.Surface(
            (self.LOGICAL_WIDTH, self.LOGICAL_HEIGHT)
        )

        # Actual window
        self.window = pygame.display.set_mode(
            (
                int(self.LOGICAL_WIDTH * self.SCALE),
                int(self.LOGICAL_HEIGHT * self.SCALE)
            ),
            pygame.RESIZABLE
        )

        pygame.display.set_caption("The Expert for Lost Handbooks")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 28)
        self.large_font = pygame.font.SysFont(None, 40)
        self.debug_grid_enabled = False
        self.debug_grid_step = 50

        self.heater = AutoNamespace()
        self.centrifuge = AutoNamespace()
        self.press = AutoNamespace()
        self.bin = AutoNamespace()
        self.indicators = AutoNamespace()
        self.background = AutoNamespace()
        self.shelf = AutoNamespace()
        self.tools = AutoNamespace()
        self.mixture = AutoNamespace()
        self.containers = AutoNamespace()
        self.fuse_box = AutoNamespace()

        self.load_sprites()
        
    def render(self, state):
        self.game_surface.fill(COLOR_RGB[Color.WHITE])

        self.draw_background(state)
        self.draw_machine(state)
        self.draw_container(state)
        self.draw_mixture(state)
        self.draw_resources(state)
        self.draw_forefront(state)
        self.draw_status(state)

        if state.status == GameStatus.GAMEOVER:
            self.draw_gameover()

        if self.debug_grid_enabled:
            self.draw_debug_grid()

        # Scale the complete image to the window
        scaled_surface = pygame.transform.scale(
            self.game_surface,
            self.window.get_size()
        )
        self.window.blit(scaled_surface, (0, 0))

        pygame.display.flip()

    def toggle_debug_grid(self):
        self.debug_grid_enabled = not self.debug_grid_enabled

    def draw_debug_grid(self):
        grid = pygame.Surface(self.game_surface.get_size(), pygame.SRCALPHA)
        grid_step = self.debug_grid_step

        for x in range(0, self.LOGICAL_WIDTH, grid_step):
            pygame.draw.line(grid, (255, 255, 255, 150), (x, 0), (x, self.LOGICAL_HEIGHT), 2)
            label = self.font.render(str(x), True, (255, 255, 255))
            grid.blit(label, (x + 3, 3))

        for y in range(0, self.LOGICAL_HEIGHT, grid_step):
            pygame.draw.line(grid, (255, 255, 255, 150), (0, y), (self.LOGICAL_WIDTH, y), 2)
            label = self.font.render(str(y), True, (255, 255, 255))
            grid.blit(label, (3, y + 3))

        self.game_surface.blit(grid, (0, 0))

    #for transforming mouse clicks to the right position
    def screen_to_game_transform(self, pos):
        pos_x, pos_y = pos

        window_width, window_height = self.window.get_size()

        scale_x = window_width / self.LOGICAL_WIDTH
        scale_y = window_height / self.LOGICAL_HEIGHT

        game_x = pos_x / scale_x
        game_y = pos_y / scale_y

        return game_x, game_y

    def draw_background(self,state):
        self.game_surface.blit(
                    self.background,
                    (0,0)
                )
        self.game_surface.blit(
                    self.shelf,
                    (positions[Location.SHELF].x,positions[Location.SHELF].y)
                )

    def draw_resources(self,state):
        #flasks
        acid_cases = [self.containers.flask_holder,self.containers.acid_1,self.containers.acid_2,self.containers.acid_3]
        acid_case = acid_cases[state.acid_available]    
        self.game_surface.blit(
                    acid_case,
                    (positions[Location.ACID].x,positions[Location.ACID].y)
                ) 
        alkaline_cases = [self.containers.flask_holder,self.containers.alkaline_1,self.containers.alkaline_2,self.containers.alkaline_3]
        alkaline_case = alkaline_cases[state.alkaline_available]     
        self.game_surface.blit(
                    alkaline_case,
                    (positions[Location.ALKALINE].x,positions[Location.ALKALINE].y)
                )        
        #dishes
        powder_cases = [self.containers.dishes,self.containers.powder_1,self.containers.powder_2,self.containers.powder_3]
        powder_case = powder_cases[state.powder_available]
        self.game_surface.blit(
                    powder_case,
                    (positions[Location.POWDER].x,positions[Location.POWDER].y)
                )

        #beakers
        for bk in range(state.beaker_available-1):
            self.game_surface.blit(
                        self.containers.beaker,
                        (positions[Location.SHELF].x+70*bk+30,positions[Location.SHELF].y-50)
                    )

    def draw_machine(self, state):
        # Heater
        self.draw_heater(state)

        # Centrifuge
        self.draw_centrifuge(state)

        # Press
        self.draw_press(state)

        # Bin
        # Centrifuge
        self.game_surface.blit(
            self.bin,
            (positions[Location.BIN].x,positions[Location.BIN].y)
        )

        self.draw_text("HEATER", positions[Location.HEATER].x, positions[Location.HEATER].y)
        self.draw_text("CENTRIFUGE", positions[Location.CENTRIFUGE].x, positions[Location.CENTRIFUGE].y)
        self.draw_text("PRESS", positions[Location.PRESS].x, positions[Location.PRESS].y)

    def draw_text(self, text, x, y, font=None):
        if font is None:
            font = self.font

        surface = font.render(
            str(text),
            True,
            (255, 255, 255)
        )

        self.game_surface.blit(surface, (x, y))

    def draw_forefront(self, state):
        # Start
        self.game_surface.blit(
                    self.containers.beaker_holder,
                    (positions[Location.START].x,positions[Location.START].y)
                )

        # End
        self.game_surface.blit(
                            self.containers.beaker_holder,
                            (positions[Location.END].x,positions[Location.END].y)
                        )

    def draw_heater(self,state):
        if state.heater.level == Level.OFF:
            heater_case = self.heater.body.off
            heater_window_case = self.heater.window.off
        elif state.heater.level == Level.LOW:
            heater_case = self.heater.body.low
            heater_window_case = self.heater.window.low
        elif state.heater.level == Level.MEDIUM:
            heater_case = self.heater.body.medium
            heater_window_case = self.heater.window.medium
        else:
            heater_case = self.heater.body.high
            heater_window_case = self.heater.window.high
        
        self.game_surface.blit(
            heater_case,
            (positions[Location.HEATER].x,positions[Location.HEATER].y)
        )
        x_offset = 34
        if state.heater.open:
            heater_window_case = self.heater.window.open
            x_offset = 34-165

        self.game_surface.blit(
                    heater_window_case,
                    (positions[Location.HEATER].x+x_offset,positions[Location.HEATER].y+117)
                )

    def draw_centrifuge(self,state):
        if state.centrifuge.open:
            centrifuge_case = self.centrifuge.body.open
        else:
            centrifuge_case = self.centrifuge.body.closed
        self.game_surface.blit(
                centrifuge_case,
                (positions[Location.CENTRIFUGE].x,positions[Location.CENTRIFUGE].y)
            )

    def draw_press(self,state):
        self.game_surface.blit(
                                    self.press.platform,
                                    (positions[Location.PRESS].x,positions[Location.PRESS].y)
                                )
        p_offset = 0
        if state.press.active:
            p_offset = 50
        self.game_surface.blit(
                                self.press.piston,
                                (positions[Location.PRESS].x,positions[Location.PRESS].y+p_offset)
                            )

    def draw_container(self, state):

        location = state.mix_container.location
        #don't draw container at all if it was thrown in bin
        if location == Location.BIN:
            return

        if location not in positions:
            return

        # Simple flask
        x_loc = positions[state.mix_container.location].x+center_offsets[state.mix_container.location].x
        y_loc = positions[state.mix_container.location].y+center_offsets[state.mix_container.location].y
        self.game_surface.blit(
            self.containers.beaker,
            (x_loc, y_loc)
        ) 

    def draw_bin(self,state):
        location = state.bin.location
        
        if location not in positions:
            return

        # Simple bin
        x_loc = positions[state.bin.location].x
        y_loc = positions[state.bin.location].y
        self.game_surface.blit(
            self.bin,
            (x_loc, y_loc)
        )    


    def draw_mixture(self, state):
        container_mix = state.mix_container.mixture

        materials = [
            container_mix.material_1,
            container_mix.material_2,
            container_mix.material_3,
        ]

        # Filter out empty slots
        materials = [m for m in materials if m is not None]


        if container_mix.current_container == Location.CONTAINER:
            # Mask surfaces
            masks = [ self.mixture.mask_1_beaker,self.mixture.mask_2_beaker,self.mixture.mask_3_beaker]

            # Position of the beaker
            x_loc = positions[state.mix_container.location].x+center_offsets[state.mix_container.location].x
            y_loc = positions[state.mix_container.location].y+center_offsets[state.mix_container.location].y

            # Draw each material using its mask
            for i, mat in enumerate(materials):
                if mat.color is None:
                    continue

                color = COLOR_RGB[mat.color]

                # Tint mask with material color
                tinted = tint_mask(masks[i], color)
                # Blit into the container
                self.game_surface.blit(tinted, (x_loc, y_loc))

        elif container_mix.current_container == Location.CENTRIFUGE:
            # Mask surfaces
            masks = [ self.mixture.mask_1_centrifuge,self.mixture.mask_2_centrifuge,self.mixture.mask_3_centrifuge]
            # put into centrifuge
            x_loc = positions[container_mix.current_container].x
            y_loc = positions[container_mix.current_container].y
            # Draw each material using its mask
            for i, mat in enumerate(materials):
                if mat.color is None:
                    continue

                color = COLOR_RGB[mat.color]

                # Tint mask with material color
                tinted = tint_mask(masks[i], color)
                # Blit into the container
                self.game_surface.blit(tinted, (x_loc, y_loc))

        elif container_mix.current_container == Location.PRESS:
            # Mask surfaces
            masks = [ self.mixture.mask_1_press,self.mixture.mask_2_press,self.mixture.mask_3_press]
            # put into press
            x_loc = positions[container_mix.current_container].x
            y_loc = positions[container_mix.current_container].y
            # Draw each material using its mask
            for i, mat in enumerate(materials):
                if mat.color is None:
                    continue

                color = COLOR_RGB[mat.color]

                # Tint mask with material color
                tinted = tint_mask(masks[i], color)
                # Blit into the container
                self.game_surface.blit(tinted, (x_loc, y_loc))
        else:
            print("No location")

    def draw_status(self, state):

        x = 30
        y = 30

        self.draw_text( f"Time: {state.time_remaining:.1f}",x, y)

        self.draw_text(f"Heater: {state.heater.level.name}", x, y + 30)

        self.draw_text( f"Centrifuge: {state.centrifuge.level.name}", x, y + 60)

        self.draw_text( f"Press: {state.press.level}", x, y + 90)

        self.draw_text( f"Money: {state.money_remaining}", x, y + 120 )

    def load_sprites(self):

        self.background = scale_by_factor(load_image(f"background/walls_floor_0.png",None),GLOBAL_FACTOR+0.15)
        self.shelf = scale_by_factor(load_image(f"background/shelf.png",None),GLOBAL_FACTOR)

        self.heater.body.off = scale_by_factor(load_image(f"heater/body_off.png", None),GLOBAL_FACTOR)
        self.heater.body.low = scale_by_factor(load_image(f"heater/body_low.png", None),GLOBAL_FACTOR)
        self.heater.body.medium = scale_by_factor(load_image(f"heater/body_medium.png", None),GLOBAL_FACTOR)
        self.heater.body.high = scale_by_factor(load_image(f"heater/body_high.png", None),GLOBAL_FACTOR)
        self.heater.window.off = scale_by_factor(load_image(f"heater/window_off.png", None),GLOBAL_FACTOR)
        self.heater.window.low = scale_by_factor(load_image(f"heater/window_low.png", None),GLOBAL_FACTOR)
        self.heater.window.medium = scale_by_factor(load_image(f"heater/window_medium.png", None),GLOBAL_FACTOR)
        self.heater.window.high = scale_by_factor(load_image(f"heater/window_high.png", None),GLOBAL_FACTOR)
        self.heater.window.open = scale_by_factor(load_image(f"heater/window_open.png", None),GLOBAL_FACTOR)

        self.centrifuge.body.closed = scale_by_factor(load_image(f"centrifuge/body_closed.png", None),GLOBAL_FACTOR)
        self.centrifuge.body.open = scale_by_factor(load_image(f"centrifuge/body_open.png", None),GLOBAL_FACTOR)

        self.containers.beaker_holder =  scale_by_factor(load_image(f"containers/beaker_holder.png", None),GLOBAL_FACTOR)
        self.containers.beaker =  scale_by_factor(load_image(f"containers/beaker.png", None),GLOBAL_FACTOR)
        self.containers.flask_holder =  scale_by_factor(load_image(f"containers/holder_empty.png", None),GLOBAL_FACTOR)
        self.containers.acid_1 =  scale_by_factor(load_image(f"containers/acid_1.png", None),GLOBAL_FACTOR)
        self.containers.acid_2 =  scale_by_factor(load_image(f"containers/acid_2.png", None),GLOBAL_FACTOR)
        self.containers.acid_3 =  scale_by_factor(load_image(f"containers/acid_3.png", None),GLOBAL_FACTOR)
        self.containers.alkaline_1 =  scale_by_factor(load_image(f"containers/alkaline_1.png", None),GLOBAL_FACTOR)
        self.containers.alkaline_2 =  scale_by_factor(load_image(f"containers/alkaline_2.png", None),GLOBAL_FACTOR)
        self.containers.alkaline_3 =  scale_by_factor(load_image(f"containers/alkaline_3.png", None),GLOBAL_FACTOR)
        self.containers.dishes =  scale_by_factor(load_image(f"containers/dishes_empty.png", None),GLOBAL_FACTOR)
        self.containers.powder_1 =  scale_by_factor(load_image(f"containers/powder_1.png", None),GLOBAL_FACTOR)
        self.containers.powder_2 =  scale_by_factor(load_image(f"containers/powder_2.png", None),GLOBAL_FACTOR)
        self.containers.powder_3 =  scale_by_factor(load_image(f"containers/powder_3.png", None),GLOBAL_FACTOR)
        self.bin = scale_by_factor(load_image(f"containers/bin.png",None),GLOBAL_FACTOR)
    

        self.fuse_box.fuses_closed =  scale_by_factor(load_image(f"fuse_box/body_closed_fuses.png", None),GLOBAL_FACTOR)
        self.fuse_box.fuses_open =  scale_by_factor(load_image(f"fuse_box/body_open_fuses.png", None),GLOBAL_FACTOR)
        self.fuse_box.connectors_closed =  scale_by_factor(load_image(f"fuse_box/body_closed_connectors.png", None),GLOBAL_FACTOR)
        self.fuse_box.connectors_open =  scale_by_factor(load_image(f"fuse_box/body_open_connectors.png", None),GLOBAL_FACTOR)

        self.mixture.mask_1_beaker =  scale_by_factor(load_image(f"mixture/mask_1.png", None),GLOBAL_FACTOR)
        self.mixture.mask_2_beaker =  scale_by_factor(load_image(f"mixture/mask_2.png", None),GLOBAL_FACTOR)
        self.mixture.mask_3_beaker =  scale_by_factor(load_image(f"mixture/mask_3.png", None),GLOBAL_FACTOR)
        self.mixture.mask_1_press =  scale_by_factor(load_image(f"mixture/mask_1_press.png", None),GLOBAL_FACTOR)
        self.mixture.mask_2_press =  scale_by_factor(load_image(f"mixture/mask_2_press.png", None),GLOBAL_FACTOR)
        self.mixture.mask_3_press =  scale_by_factor(load_image(f"mixture/mask_3_press.png", None),GLOBAL_FACTOR)
        self.mixture.mask_1_centrifuge =  scale_by_factor(load_image(f"mixture/mask_1_centrifuge.png", None),GLOBAL_FACTOR)
        self.mixture.mask_2_centrifuge =  scale_by_factor(load_image(f"mixture/mask_2_centrifuge.png", None),GLOBAL_FACTOR)
        self.mixture.mask_3_centrifuge =  scale_by_factor(load_image(f"mixture/mask_3_centrifuge.png", None),GLOBAL_FACTOR)

        self.press.tank =  scale_by_factor(load_image(f"press/tank.png", None),GLOBAL_FACTOR)
        self.press.indicator =  scale_by_factor(load_image(f"press/tank.png", None),GLOBAL_FACTOR)
        self.press.valve_0 =  scale_by_factor(load_image(f"press/valve_0.png", None),GLOBAL_FACTOR)
        self.press.valve_1 =  scale_by_factor(load_image(f"press/valve_1.png", None),GLOBAL_FACTOR)
        self.press.needle_off =  scale_by_factor(load_image(f"press/pressure_needle_off.png", None),GLOBAL_FACTOR)
        self.press.needle_low =  scale_by_factor(load_image(f"press/pressure_needle_low.png", None),GLOBAL_FACTOR)
        self.press.needle_medium =  scale_by_factor(load_image(f"press/pressure_needle_medium.png", None),GLOBAL_FACTOR)
        self.press.needle_high =  scale_by_factor(load_image(f"press/pressure_needle_high.png", None),GLOBAL_FACTOR)
        self.press.platform =  scale_by_factor(load_image(f"press/press_plate.png", None),GLOBAL_FACTOR)
        self.press.piston =  scale_by_factor(load_image(f"press/piston.png", None),GLOBAL_FACTOR)

        self.indicators.button.off =  scale_by_factor(load_image(f"indicators/button_off.png", None),GLOBAL_FACTOR)
        self.indicators.button.on =  scale_by_factor(load_image(f"indicators/button_on.png", None),GLOBAL_FACTOR)
        self.indicators.button.pressed =  scale_by_factor(load_image(f"indicators/button_pressed.png", None),GLOBAL_FACTOR)
        self.indicators.dial_0 =  scale_by_factor(load_image(f"indicators/dial_0.png", None),GLOBAL_FACTOR)
        self.indicators.dial_1 =  scale_by_factor(load_image(f"indicators/dial_1.png", None),GLOBAL_FACTOR)
        self.indicators.dial_2 =  scale_by_factor(load_image(f"indicators/dial_2.png", None),GLOBAL_FACTOR)
        self.indicators.dial_3 =  scale_by_factor(load_image(f"indicators/dial_3.png", None),GLOBAL_FACTOR)
        self.indicators.dial_4 =  scale_by_factor(load_image(f"indicators/dial_4.png", None),GLOBAL_FACTOR)
        self.indicators.arrow_cw_off =  scale_by_factor(load_image(f"indicators/arrow_clockwise_off.png", None),GLOBAL_FACTOR)
        self.indicators.arrow_cw_on =  scale_by_factor(load_image(f"indicators/arrow_clockwise_on.png", None),GLOBAL_FACTOR)
        self.indicators.arrow_ccw_off =  scale_by_factor(load_image(f"indicators/arrow_counterclockwise_off.png", None),GLOBAL_FACTOR)
        self.indicators.arrow_ccw_on =  scale_by_factor(load_image(f"indicators/arrow_counterclockwise_on.png", None),GLOBAL_FACTOR)
        self.indicators.levels_off =  scale_by_factor(load_image(f"indicators/levels_off.png", None),GLOBAL_FACTOR)
        self.indicators.levels_low =  scale_by_factor(load_image(f"indicators/levels_low.png", None),GLOBAL_FACTOR)
        self.indicators.levels_medium =  scale_by_factor(load_image(f"indicators/levels_medium.png", None),GLOBAL_FACTOR)
        self.indicators.levels_high =  scale_by_factor(load_image(f"indicators/levels_high.png", None),GLOBAL_FACTOR)

        self.tools.toolbox =  scale_by_factor(load_image(f"tools/toolbox.png", None),GLOBAL_FACTOR)

