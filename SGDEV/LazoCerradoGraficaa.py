import pygame
from pygame.locals import *
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

SCREEN_WIDTH = 1738  # ANCHO DE VENTANA
SCREEN_HEIGHT = 971  # ALTO DE VENTANA
sea_level = 25  # NIVEL DEL MAR
submarine_direction_x = 0
submarine_image_pos_yLim = 500
submarine_image_pos_y_init = sea_level

g = 9.8  # Gravedad
Fep = 0.2  # Fuerza Empuje X

Fd = 1  # Fuerza Disparo
p = 1000  # Densidad
v = 1  # Volumen
dt = 1
by = 250  # Friccion EJE Y
bx = 65  # Friccion EJE X
e = -(p * g * v)  # Fuerza Empuje Y


# CLASE - TANQUE INTERNO DEL SUBMARINO
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

    # LAZO CERRADO
    def lazocerrading(self, posicionYsubmarino, target_y):

        if posicionYsubmarino > target_y:
            self.pumping_air_water("air")

        elif posicionYsubmarino < target_y:
            self.pumping_air_water("water")
        elif posicionYsubmarino == target_y:
            print("nada")


# CLASE - SUBMARINO
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


# CLASE - PROYECTIL
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


# LAZO CERRADO
class Crosshair:
    def __init__(self):
        self.length = 20
        self.thickness = 4
        self.color = (255, 255, 255)  # Color blanco por defecto

    def update_position(self, mouse_pos):
        self.center = mouse_pos

    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.center[0] - self.length, self.center[1]),
                         (self.center[0] + self.length, self.center[1]), self.thickness)
        pygame.draw.line(surface, self.color, (self.center[0], self.center[1] - self.length),
                         (self.center[0], self.center[1] + self.length), self.thickness)


def main():
    global submarine_direction_x, submarine_image, original_submarine_image, projectile_image_right, projectile_image_left

    pygame.init()

    icon_image = pygame.image.load("icono.png")
    pygame.display.set_icon(icon_image)

    tank1 = Reservoir(1005, 10, 5000, 'air')
    submarine1 = Submarine(tank1, 2, 0, 150, 150, 150, 1, 0, 0)
    projectiles = []

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SubG")

    original_submarine_image = pygame.image.load("submatron2.png").convert_alpha()
    background_image = pygame.image.load("fondonoche.png").convert()
    submarine_image = original_submarine_image
    projectile_image_right = pygame.image.load("proyectile2.png").convert_alpha()
    projectile_image_left = pygame.transform.flip(projectile_image_right, True, False)
    explosion_image = pygame.image.load("explosion.png").convert_alpha()

    screen.blit(submarine_image, (submarine1.pos_x, submarine_image_pos_y_init))
    screen.blit(background_image, (0, 0))

    pygame.display.flip()
    clock = pygame.time.Clock()
    target_fps = 75

    crosshair = Crosshair()
    target_y = 30

    pos_y_values = []  # Lista para almacenar los valores de posición en Y
    time_values = []  # Lista para almacenar los valores de tiempo en segundos

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=10)

    while datetime.now() < end_time:
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()

        submarine1.calculate_velocity_y()
        submarine1.calculate_velocity_x()
        submarine1.calculate_position()

        # LAZO CERRADO
        posicionYsubmarino = submarine1.pos_y
        tank1.lazocerrading(posicionYsubmarino, target_y)

        pos_y_values.append(submarine1.pos_y)
        time_values.append(elapsed_time)

        screen.blit(background_image, (0, 0))
        screen.blit(submarine_image, (submarine1.pos_x, submarine1.pos_y))

        projectiles_to_remove = []

        for projectile in projectiles:
            projectile.calculate_VelocidadPx()
            projectile.calculate_VelocidadPy()
            projectile.pos_x += projectile.Vpx
            projectile.pos_y += projectile.Vpy

            screen.blit(projectile.image, (projectile.pos_x, projectile.pos_y))

            # CONDICION SI IMPACTA CON BORDE DE VENTANA
            if projectile.check_collision() or (
                    projectile.pos_x < 0 or projectile.pos_x > SCREEN_WIDTH - projectile.image.get_width()
                    or projectile.pos_y < 0 or projectile.pos_y > SCREEN_HEIGHT
            ):
                projectiles_to_remove.append(projectile)
                screen.blit(explosion_image, (projectile.pos_x, projectile.pos_y))

        for projectile in projectiles_to_remove:
            projectiles.remove(projectile)

        pygame.display.flip()

        # CONFIGURACION DE TECLAS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                target_y = crosshair.center[1]

        submarine1.calculate_mass()
        clock.tick(target_fps)
        mouse_pos = pygame.mouse.get_pos()
        crosshair.update_position(mouse_pos)
        crosshair.draw(screen)
        pygame.display.flip()

        print("Submarine position: ", submarine1.pos_y)
        print("MOUSE POSITION: ", target_y)

    plt.plot(time_values, pos_y_values)
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Posición en Y del Submarino')
    plt.title('Posición en Y del Submarino vs Tiempo')
    plt.xticks(range(int(min(time_values)), int(max(time_values)) + 1, 1))

    plt.show()


if __name__ == "__main__":
    submarine_direction_x = 0
    main()