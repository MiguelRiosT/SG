import pygame
from pygame.locals import *
import sys

SCREEN_WIDTH = 1738
SCREEN_HEIGHT = 971

sea_level = 25

submarine_direction_x = 0
submarine_image_pos_yLim = 500
submarine_image_pos_y_init = sea_level

g = 9.8
Fep = 0.2  # Fuerza Empuje proyectil en X
Fd = 1  # Fuerza disparo proyectil
p = 1000
v = 1
dt = 1
by = 250
bx = 65
e = -(p * g * v)  # Fuerza Empuje proyectil en Y


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
    def __init__(self, tank, mass, vel_x, vel_y, pos_x, pos_y, direction, Fv, Ig):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mass = mass
        self.vel_y = vel_y
        self.vel_x = vel_x
        self.tank = tank
        self.direction = direction
        self.Fv = Fv
        self.Ig = Ig

    def calculate_mass(self):
        self.mass = self.tank.actual_level

    def calculate_velocity_y(self):
        self.vel_y = dt * ((e / self.mass) + g - ((by * self.vel_y) / self.mass)) + self.vel_y

    def calculate_velocity_x(self):
        self.vel_x = (dt * ((self.Fv - bx * self.vel_x) / self.mass)) + self.vel_x

    def calculate_position(self):
        self.pos_y = self.pos_y + self.vel_y

        if self.pos_y > submarine_image_pos_yLim:
            self.pos_y = submarine_image_pos_yLim

        if self.pos_y < sea_level:
            self.pos_y = sea_level

        self.pos_x = max(0, min(self.pos_x + self.vel_x, SCREEN_WIDTH - submarine_image.get_width()))

        return self.pos_x, self.pos_y

    def set_direction(self, direction):
        if direction < 0:
            self.direction = -1
        elif direction > 0:
            self.direction = 1
        else:
            self.direction = 0


class Projectile:
    def __init__(self, pos_x, pos_y, masaproyectil, Vpx, Vpy, image_right, image_left, direction):
        self.pos_x = pos_x + original_submarine_image.get_width() - image_right.get_width()
        self.pos_y = pos_y + original_submarine_image.get_height() - image_right.get_height()
        self.masaproyectil = masaproyectil
        self.Vpx = Vpx * direction
        self.Vpy = Vpy
        self.image_right = image_right
        self.image_left = image_left
        self.image = image_right if direction == 1 else image_left

    def calculate_masaproyectil(self):
        self.masaproyectil = self.masaproyectil

    def calculate_VelocidadPy(self):

        self.Vpy = dt * ((Fep / self.masaproyectil) + g - ((by * self.Vpy) / self.masaproyectil)) + self.Vpy

    def calculate_VelocidadPx(self):
        self.Vpx = (dt * ((Fd - bx * self.Vpx) / self.masaproyectil)) + self.Vpx

    def calculate_position(self):
        self.pos_y = self.pos_y + self.Vpy

        if self.pos_y > submarine_image_pos_yLim:
            self.pos_y = submarine_image_pos_yLim

        if self.pos_y < sea_level:
            self.pos_y = sea_level

        self.pos_x = self.pos_x + self.Vpx

        # Verificar colisión con los bordes de la ventana
        if self.pos_x < 0 or self.pos_x > SCREEN_WIDTH - self.image.get_width():
            self.Vpx = -self.Vpx  # Invertir la velocidad en X al colisionar con los bordes

        if self.pos_y < 0 or self.pos_y > SCREEN_HEIGHT:
            self.Vpy = -self.Vpy  # Invertir la velocidad en Y al colisionar con los bordes


        return self.pos_x, self.pos_y

    def check_collision(self):
        if (
                self.pos_x < 0
                or self.pos_x > SCREEN_WIDTH - self.image.get_width()
                or self.pos_y < 0
                or self.pos_y > SCREEN_HEIGHT - self.image.get_height()
        ):
            return True
        return False

    def update(self):  # Agrega este método
        self.calculate_VelocidadPx()
        self.calculate_VelocidadPy()
        self.calculate_position()


def main():
    global submarine_direction_x, submarine_image, original_submarine_image, projectile_image_right, projectile_image_left

    pygame.init()

    icon_image = pygame.image.load("icono.png")
    pygame.display.set_icon(icon_image)

    tank1 = Reservoir(1005, 10, 5000, 'air')
    submarine1 = Submarine(tank1, 2, 0, 150, 150, 150, 1, 0, 0)
    projectiles = []

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SG")

    original_submarine_image = pygame.image.load("submatron1.png").convert_alpha()
    background_image = pygame.image.load("fondonoche.png").convert()
    submarine_image = original_submarine_image
    projectile_image_right = pygame.image.load("proyectile.png").convert_alpha()
    projectile_image_left = pygame.transform.flip(projectile_image_right, True, False)
    explosion_image = pygame.image.load("explosion.png").convert_alpha()

    screen.blit(submarine_image, (submarine1.pos_x, submarine_image_pos_y_init))
    screen.blit(background_image, (0, 0))

    pygame.display.flip()
    clock = pygame.time.Clock()
    target_fps = 75

    while True:
        submarine1.calculate_velocity_y()
        submarine1.calculate_velocity_x()
        submarine1.calculate_position()

        screen.blit(background_image, (0, 0))
        screen.blit(submarine_image, (submarine1.pos_x, submarine1.pos_y))

        projectiles_to_remove = []

        for projectile in projectiles:
            projectile.pos_x += projectile.Vpx
            projectile.pos_y += projectile.Vpy
            screen.blit(projectile.image, (projectile.pos_x, projectile.pos_y))

            # Verificar colisión con los bordes de la ventana
            if projectile.check_collision() or (
                    projectile.pos_x < 0 or projectile.pos_x > SCREEN_WIDTH - projectile.image.get_width()
                    or projectile.pos_y < 0 or projectile.pos_y > SCREEN_HEIGHT
            ):
                projectiles_to_remove.append(projectile)
                screen.blit(explosion_image, (projectile.pos_x, projectile.pos_y))

        for projectile in projectiles_to_remove:
            projectiles.remove(projectile)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    tank1.pumping_air_water('air')
                elif event.key == K_DOWN:
                    tank1.pumping_air_water('water')

                elif event.key == K_s:
                    submarine1.Fv = 0
                    submarine1.calculate_velocity_x()

                elif event.key == K_LEFT:
                    submarine_image = pygame.transform.flip(original_submarine_image, True, False)
                    submarine1.direction = -1
                    submarine1.Fv = -1000
                    submarine1.calculate_velocity_x()
                    submarine1.calculate_position()

                elif event.key == K_RIGHT:
                    submarine1.direction = 1
                    submarine_image = original_submarine_image
                    submarine1.Fv = 1000
                    submarine1.calculate_velocity_x()
                    submarine1.calculate_position()

                elif event.key == K_f:
                    # Crea un nuevo proyectil en la dirección del submarino
                    new_projectile = Projectile(submarine1.pos_x, submarine1.pos_y, 1, 10, 3,projectile_image_right, projectile_image_left, submarine1.direction)

                    projectiles.append(new_projectile)

        submarine1.calculate_mass()
        clock.tick(target_fps)

if __name__ == "__main__":
    submarine_direction_x = 0
    main()
