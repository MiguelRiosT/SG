import pygame
from pygame.locals import *
import sys

# Variables globales
SCREEN_WIDTH = 1738
SCREEN_HEIGHT = 971
sea_level = 50
submarine_direction_x = 0
submarine_image_pos_yLim = 500
submarine_image_pos_y_init = sea_level
g = 9.8
p = 1000
v = 1
dt = 1
b = 250
e = - (p * g * v)

class Reservoir:
    def __init__(self, actual_level, valve_flow, max_capacity, fluid_to_pump):
        self.actual_level = actual_level
        self.valve_flow = valve_flow
        self.max_capacity = max_capacity
        self.fluid_to_pump = fluid_to_pump

    def pumping_air_water(self, fluid_to_pump):
        if fluid_to_pump == 'air':
            if self.actual_level > 0:
                self.actual_level = self.actual_level - self.valve_flow
            else:
                self.actual_level = 0

        if fluid_to_pump == 'water':
            if self.actual_level < self.max_capacity:
                self.actual_level = self.actual_level + self.valve_flow
            else:
                self.actual_level = self.max_capacity

class Submarine:
    def __init__(self, tank, mass, actual_velocity, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mass = mass
        self.actual_velocity = actual_velocity
        self.tank = tank
        self.direction = 1

    def calculate_mass(self):
        self.mass = self.tank.actual_level

    def calculate_velocity(self):
        self.actual_velocity = dt * ((e / self.mass) + g - ((b * self.actual_velocity) / self.mass)) + self.actual_velocity

    def calculate_position(self):
        self.pos_y = self.pos_y + self.actual_velocity

        if self.pos_y > submarine_image_pos_yLim:
            self.pos_y = submarine_image_pos_yLim

        if self.pos_y < sea_level:
            self.pos_y = sea_level

        self.pos_x = max(0, min(self.pos_x + submarine_direction_x, SCREEN_WIDTH - submarine_image.get_width()))
        return self.pos_x, self.pos_y

    def set_direction(self, direction):
        self.direction = direction

class Projectile:
    def __init__(self, pos_x, pos_y, velocity_x, velocity_y, image_right, image_left, direction):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocity_x = velocity_x * direction
        self.velocity_y = velocity_y
        self.image_right = image_right
        self.image_left = image_left
        self.image = image_right if direction == 1 else image_left

def show_menu(screen):
    font = pygame.font.Font(None, 36)
    options = ["Jugar", "Seleccionar submarino", "Seleccionar mapa", "Salir"]
    option_rects = []

    menu_background = pygame.image.load("fondomenu.png").convert()

    for i, option in enumerate(options):
        text = font.render(option, True, (255, 255, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 50))
        option_rects.append((rect, option))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for rect, option in option_rects:
                        if rect.collidepoint(event.pos):
                            if option == "Jugar":
                                return True
                            elif option == "Seleccionar submarino":
                                print("Opción: Seleccionar submarino")
                            elif option == "Seleccionar mapa":
                                print("Opción: Seleccionar mapa")
                            elif option == "Salir":
                                sys.exit()

        screen.blit(menu_background, (0, 0))
        for rect, option in option_rects:
            pygame.draw.rect(screen, (50, 50, 200), rect)
            screen.blit(font.render(option, True, (255, 255, 255)), rect.topleft)

        pygame.display.flip()

def main():
    global submarine_direction_x, submarine_image

    pygame.init()
    tank1 = Reservoir(1005, 2, 50000, 'air')
    submarine1 = Submarine(tank1, 2, 2, 150, 150)
    projectiles = []

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SG")

    original_submarine_image = pygame.image.load("submatron2.png").convert_alpha()
    background_image = pygame.image.load("fondonoche.png").convert()
    submarine_image = original_submarine_image
    projectile_image_right = pygame.image.load("proyectile.png").convert_alpha()
    projectile_image_left = pygame.transform.flip(projectile_image_right, True, False)

    if not show_menu(screen):
        sys.exit()

    screen.blit(submarine_image, (submarine1.pos_x, submarine_image_pos_y_init))
    screen.blit(background_image, (0, 0))

    pygame.display.flip()
    clock = pygame.time.Clock()
    target_fps = 75

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        submarine1.calculate_velocity()
        submarine1.calculate_position()

        screen.blit(background_image, (0, 0))
        screen.blit(submarine_image, (submarine1.pos_x, submarine1.pos_y))

        for projectile in projectiles:
            projectile.pos_x += projectile.velocity_x
            projectile.pos_y += projectile.velocity_y
            screen.blit(projectile.image, (projectile.pos_x, projectile.pos_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    tank1.pumping_air_water('air')
                elif event.key == K_DOWN:
                    tank1.pumping_air_water('water')
                elif event.key == K_LEFT:
                    submarine_image = pygame.transform.flip(original_submarine_image, True, False)
                    submarine_direction_x = -1
                    submarine1.set_direction(submarine_direction_x)
                elif event.key == K_RIGHT:
                    submarine_image = original_submarine_image
                    submarine_direction_x = 1
                    submarine1.set_direction(submarine_direction_x)
                elif event.key == K_f:
                    new_projectile = Projectile(submarine1.pos_x, submarine1.pos_y, 6, 0.6, projectile_image_right, projectile_image_left, submarine1.direction)
                    projectiles.append(new_projectile)

            elif event.type == pygame.KEYUP:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    submarine_direction_x = 0

        submarine1.calculate_mass()
        clock.tick(target_fps)

if __name__ == "__main__":
    submarine_direction_x = 0
    main()
