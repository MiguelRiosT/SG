import pygame
from pygame.locals import *
import sys
import matplotlib.pyplot as plt # LIBRERIA PARA GRAFICOS - pip install matplotlib
from datetime import datetime, timedelta # MANEJO DE TIEMPOS A TRAVES DE LIBRERIA DATETIME Y TIMEDELTA

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
    # Lógica encargada de estabilizar el submarino en una posicion en Y
    def lazocerrading(self, posicionYsubmarino, target_y):

        # En caso de que el submarino este por debajo del punto indicado
        #Bombeara aire para hacerlo subir
        if posicionYsubmarino > target_y:
            self.pumping_air_water("air")

        # En caso de que el submarino este por arriba del punto indicado
        # Bombeara agua para hacerlo bajar
        elif posicionYsubmarino < target_y:
            self.pumping_air_water("water")

        # En caso de que el submarino este en el punto indicado en Y
        # No bombeara nada
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


# LAZO CERRADO
# Clase encargada de contener los valores gráficos, actualizar su posicion e ilustrarla en pantalla
class Crosshair:
    def __init__(self):
        #Definicion de constantes
        self.length = 20 #Longitud
        self.thickness = 10 #Grosor
        self.color = (255, 255, 255)  # Color: Blanco

    #Refresca la posicion en X y Y de la mira
    def update_position(self, mouse_pos):
        self.mouse_pos = mouse_pos

    #Se encarga de graficar la mira
    def draw(self, surface):

        #Usando las constantes de la clase Crosshair grafica el eje X de la mira
        #Usando la funcion .line graficamos en X la linea que corresponde al plano en X pasandole la superficie, color,
        #posicion donde comienza y donde termina y finalmente el grosor
        pygame.draw.line(surface, self.color,
                         #Posicion de Inicio de para graficar la linea en donde se toma la posicion en x de la posicion
                         # del mouse y se le resta la longitud,y se pasa la posicion en y del mouse
                         (self.mouse_pos[0] - self.length, self.mouse_pos[1]),
                         # Posicion de Fin de para graficar la linea en donde se toma la posicion en x de la posicion
                         # del mouse y se le suma la longitud y se pasa la posicion en y del mouse
                         (self.mouse_pos[0] + self.length, self.mouse_pos[1]),
                         self.thickness)

        # Usando las constantes de la clase Crosshair grafica el eje Y de la mira empleando
        # la misma logica de la linea anterior en X  pero esta vez para Y,dejando x constante como la posiscion de mouse
        pygame.draw.line(surface, self.color, (self.mouse_pos[0], self.mouse_pos[1] - self.length),
                         (self.mouse_pos[0], self.mouse_pos[1] + self.length), self.thickness)


def main():
    global submarine_direction_x, submarine_image, original_submarine_image

    pygame.init()

    icon_image = pygame.image.load("icono.png")
    pygame.display.set_icon(icon_image)

    tank1 = Reservoir(1005, 10, 5000, 'air')
    submarine1 = Submarine(tank1, 2, 0, 150, 150, 150, 1, 0, 0)


    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SubG")

    original_submarine_image = pygame.image.load("submatron2.png").convert_alpha()
    background_image = pygame.image.load("fondonoche.png").convert()
    submarine_image = original_submarine_image


    screen.blit(submarine_image, (submarine1.pos_x, submarine_image_pos_y_init))
    screen.blit(background_image, (0, 0))

    pygame.display.flip()
    clock = pygame.time.Clock()
    target_fps = 75

    #LAZO CERRADO INICIALIZAMOS
    crosshair = Crosshair()
    target_y = 30
    pos_y_values = []  # Lista para almacenar los valores de posición en Y
    time_values = []  # Lista para almacenar los valores de tiempo en segundos

    #MANEJO DE TIEMPOS LAZO CERRADO GRAFICA
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=10)

    #BUCLE QUE DURA LO DETERMINADO EN end_time
    while datetime.now() < end_time:
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()

        submarine1.calculate_velocity_y()
        submarine1.calculate_velocity_x()
        submarine1.calculate_position()

        # LAZO CERRADO
        posicionYsubmarino = submarine1.pos_y #Se guarda la posicion del submarino en el eje Y
        tank1.lazocerrading(posicionYsubmarino, target_y) #Se aplica la función que implementa la logica de lazo cerrado
        pos_y_values.append(submarine1.pos_y) #Agregamos a las listas los valores del submarino en Y en el tiempo
        time_values.append(elapsed_time) #Manejo de tiempo

        screen.blit(background_image, (0, 0))
        screen.blit(submarine_image, (submarine1.pos_x, submarine1.pos_y))


        pygame.display.flip()

        # CONFIGURACION DE TECLAS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            #LAZO CERRADO - CAPTURA DE VALOR POS Y DEL MOUSE AL DAR CLICK IZQUIERDO
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                target_y = crosshair.mouse_pos[1]#mouse_pos[0] = POS X  y mouse_pos[1] = POS Y

        submarine1.calculate_mass()
        clock.tick(target_fps)

        #LAZO CEERADO
        mouse_pos = pygame.mouse.get_pos() #se guarda el valor de la posicion del mouse
        crosshair.update_position(mouse_pos) #se actualzua la posicion de la mira
        crosshair.draw(screen) #se dibuja en el juego la mira
        pygame.display.flip()

        print("Submarine position: ", submarine1.pos_y)
        print("MOUSE POSITION: ", target_y)

    #LAZO CERRADO - GRAFICA
    plt.plot(time_values, pos_y_values) #Se realiza un plot graph de Posicion en Y del submarino VS Tiempo
    plt.xlabel('Tiempo (segundos)') #Nombre del eje x dentro de la grafica
    plt.ylabel('Posición en Y del Submarino') #Nombre del eje y dentro de la grafica
    plt.title('Posición en Y del Submarino vs Tiempo') #Titulo de la grafica
    plt.xticks(range(int(min(time_values)), int(max(time_values)) + 1, 1)) # Valores Eje x de uno en uno

    plt.show() # Se muestra el grafico


if __name__ == "__main__":
    submarine_direction_x = 0
    main()