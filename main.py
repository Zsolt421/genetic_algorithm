import pygame
import math
import os
import random
import numpy as np

pygame.init()

# -------------------------
# VARIABLE DEFINITION
# -------------------------

WIDTH = 1448
HEIGHT = 1086
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 30
NUMBER_OF_ENTITIES = 100
#NUMBER_OF_GENES = 32
NUM_OF_GENE_ROWS = 2
NUM_OF_GENE_COLUMNS = 16
#NUM_OF_SENSORS_COLUMNS = 16
#NUM_OF_SENSORS_ROWS = 1
GEN_MIN = -1
GEN_MAX = 1
TOURNAMENT_SIZE = 5
#MAX_SPEED = 150
TURN_SPEED = 60
TIMEOUT = 25

# -------------------------
# SENSOR VALUES
# -------------------------

SENSOR_ORIGIN_OFFSET = 25
# Negatív = balra
# Pozitív = jobbra
sensor_1 = 30
sensor_2 = 15
sensor_3 = -1 * sensor_2
sensor_4 = -1 * sensor_1
SENSOR_ANGLES = [sensor_1, sensor_2, sensor_3, sensor_4]

# Távolságok az autó előtt
sensor_dist = 20
SENSOR_DISTANCES = [sensor_dist, 2 * sensor_dist, 3 * sensor_dist, 4 * sensor_dist]

SENSOR_RADIUS = 3

# Ennyivel induljon az érzékelés
# az autó középpontja előtt
SENSOR_ORIGIN_OFFSET = 25

CHECKPOINTS = [
    pygame.Rect(305, 940, 30, 30),
    pygame.Rect(230, 915, 30, 30),
    pygame.Rect(165, 855, 30, 30),
    pygame.Rect(115, 775, 30, 30),
    pygame.Rect(100, 685, 30, 30),
    pygame.Rect(115, 595, 30, 30),
    pygame.Rect(160, 510, 30, 30),
    pygame.Rect(210, 430, 30, 30),
    pygame.Rect(240, 345, 30, 30),
    pygame.Rect(250, 260, 30, 30),
    pygame.Rect(305, 195, 30, 30),
    pygame.Rect(395, 160, 30, 30),
    pygame.Rect(505, 145, 30, 30),
    pygame.Rect(625, 140, 30, 30),
    pygame.Rect(745, 145, 30, 30),
    pygame.Rect(860, 145, 30, 30),
    pygame.Rect(965, 135, 30, 30),
    pygame.Rect(1055, 113, 30, 30),
    pygame.Rect(1135, 100, 30, 30),
    pygame.Rect(1185, 120, 30, 30),
    pygame.Rect(1145, 190, 30, 30),
    pygame.Rect(1095, 255, 30, 30),
    pygame.Rect(1105, 320, 30, 30),
    pygame.Rect(1165, 370, 30, 30),
    pygame.Rect(1245, 405, 30, 30),
    pygame.Rect(1295, 485, 30, 30),
    pygame.Rect(1315, 585, 30, 30),
    pygame.Rect(1305, 690, 30, 30),
    pygame.Rect(1280, 785, 30, 30),
    pygame.Rect(1225, 860, 30, 30),
    pygame.Rect(1145, 900, 30, 30),
    pygame.Rect(1055, 910, 30, 30),
    pygame.Rect(950, 905, 30, 30),
    pygame.Rect(845, 890, 30, 30),
    pygame.Rect(740, 895, 30, 30),
    pygame.Rect(635, 925, 30, 30),
    pygame.Rect(530, 955, 30, 30),
    pygame.Rect(415, 970, 30, 30),]



generation_counter = 1
cars = []


# -------------------------
# PYGAME LOAD IN
# -------------------------

pygame.display.set_caption(f"Iteration: {generation_counter}")
folder = os.path.dirname(__file__)
background = pygame.image.load(os.path.join(folder, "track.png"))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


# -------------------------
# CAR STARTING SETTINGS
# -------------------------

STARTING_X = 384
STARTING_Y = 973
STARTING_ANGLE = math.radians(-166)
WHEEL_DISTANCE = 40
car_length = 50
car_width = 30
car_surface = pygame.Surface((car_length, car_width), pygame.SRCALPHA)
car_surface.fill((220, 20, 20))



class Car:
    def __init__(self, genome):
        self.x = STARTING_X
        self.y = STARTING_Y
        self.angle = STARTING_ANGLE
        self.rect = pygame.Rect(0, 0, car_length, car_width)#
        self.rect.center = (round(self.x), round(self.y))#
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        #self.speed = MAX_SPEED
        self.alive = True
        self.fitness = 0
        self.genome = genome
        self.checkpoint_index = 0
        self.alive_time = 0

    def read_sensors(self) -> np.ndarray :

        sensor_values = np.empty((NUM_OF_GENE_COLUMNS, 3))

        # érzékelők indulópontja: az autó eleje
        
        origin_x = self.x + math.cos(self.angle) * SENSOR_ORIGIN_OFFSET
        origin_y = self.y + math.sin(self.angle) * SENSOR_ORIGIN_OFFSET
        sensor_origin = [origin_x, origin_y]
     
        for distance in SENSOR_DISTANCES:

            for relative_angle in SENSOR_ANGLES:

                sensor_angle = (
                    self.angle + math.radians(relative_angle)
                )

                sensor_x = (
                    origin_x + math.cos(sensor_angle) * distance
                )

                sensor_y = (
                    origin_y + math.sin(sensor_angle) * distance
                )

                if not check_if_on_road(sensor_x, sensor_y):
                    value = 0 # ha fű
                else:
                    value = 1 # ha út
                    

                i = distance * len(SENSOR_ANGLES) + relative_angle
                sensor_values[i, 0] = value
                sensor_values[i, 1] = sensor_x
                sensor_values[i, 2] = sensor_y

        return sensor_values, sensor_origin

    def calculate_controls(self, sensor_values) -> tuple[float, float]: 
        # A szenzorértékek és a genom alapján kiszámolja,
        # hogyan mozogjon az autó.
        #sensors_vector = np.array(sensor_values)
        output = np.dot(self.genome, sensor_values[:, 0])

        right_wheel_acceleration = output[0]
        left_wheel_acceleration = output[1]

        return right_wheel_acceleration, left_wheel_acceleration

    def move(self, dt, right_wheel_acceleration, left_wheel_acceleration, WHEEL_DISTANCE) -> None:
        # Frissíti az autó pozícióját és irányát az eltelt idő alapján.
        self.right_wheel_speed += right_wheel_acceleration * dt
        self.left_wheel_speed += left_wheel_acceleration * dt
        forward_speed = (self.left_wheel_speed + self.right_wheel_speed) / 2

        delta_angle = (self.left_wheel_speed - self.right_wheel_speed) / WHEEL_DISTANCE * dt
        self.angle += delta_angle


        #ide kell self. vagy nem? + egybe legyen egy nagy egyenlet vagy bontsam valtozokra
        self.x += (np.cos(self.angle) * forward_speed * dt)
        self.y += (np.sin(self.angle) * forward_speed * dt)
        self.rect.center = (round(self.x), round(self.y))

        return None

    
    def check_checkpoint(self) -> None:
        # Ellenőrzi, hogy az autó elérte-e a következő checkpointot.
        if self.checkpoint_index < len(CHECKPOINTS):
            current_target = CHECKPOINTS[self.checkpoint_index]

            # The car's rectangle is centered on its current position.
            if self.rect.colliderect(current_target):
                self.checkpoint_index += 1

    def calculate_fitness(self) -> None:

        if self.checkpoint_index < len(CHECKPOINTS):
            target = CHECKPOINTS[self.checkpoint_index]

            distance = math.hypot(self.x - target.centerx, self.y - target.centery)
            self.fitness = self.checkpoint_index * 1000 - distance

        else:
            self.fitness = len(CHECKPOINTS) * 1000

    def draw(self, screen) -> None:
        rotated_car = pygame.transform.rotate(car_surface,-math.degrees(self.angle))
        rect = rotated_car.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_car, rect)

    def draw_sensors(sensor_values, sensor_origin):
        for value, sensor_x, sensor_y in sensor_values:

            # A vonal csak vizualizáció
            pygame.draw.line(SCREEN,(100, 100, 100),(sensor_origin[0], sensor_origin[1]),(sensor_x, sensor_y),1)

            # 0 = fű -> zöld pont
            # 1 = út -> piros pont

            if value == 0:
                sensor_color = (255, 0, 0)
            else:
                sensor_color = (0, 255, 0)

            pygame.draw.circle(
                SCREEN,sensor_color,(int(sensor_x), int(sensor_y)),SENSOR_RADIUS
            )

# -------------------------
# Run Car
# -------------------------

def run_cars(dt) -> None:
    for car in cars:
        if car.alive == True:
            
            car.alive_time += dt

            sensor_values, sensor_origin = car.read_sensors()

            right_wheel_acceleration, left_wheel_acceleration = car.calculate_controls(sensor_values)
            car.move(dt, right_wheel_acceleration, left_wheel_acceleration, WHEEL_DISTANCE)
            car.draw_sensors(sensor_values, sensor_origin)

            
            if check_if_on_road(car.x, car.y) and dt < TIMEOUT:
                car.alive = True
            
            if car.alive == True: car.check_checkpoint()
            else: car.calculate_fitness()


def check_if_on_road(x, y) -> bool:
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return False
    color = background.get_at((int(x), int(y)))

    r = color.r
    g = color.g
    b = color.b

    if g > r + 30 and g > b + 30:
        return False   # grass

    return True   # road

def first_creation(NUMBER_OF_ENTITIES) -> None:

    for _ in range(NUMBER_OF_ENTITIES):
        genome = np.random.normal(GEN_MIN, GEN_MAX,(NUM_OF_GENE_ROWS, NUM_OF_GENE_COLUMNS))
        cars.append(Car(genome))

def genome_crosser(parent1, parent2) -> list:
    child_genes = np.empty((NUM_OF_GENE_ROWS, NUM_OF_GENE_COLUMNS))

    for row in range(NUM_OF_GENE_ROWS):

        for column in range(NUM_OF_GENE_COLUMNS):

            choice = random.randint(1, 2)

            if choice == 1:
                child_genes[row][column] = parent1.genome[row][column]

            else:
                child_genes[row][column] = parent2.genome[row][column]

    return child_genes

def tournament_selection(cars, tournament_selection_constant) -> Car:
    competitors = random.sample(cars, tournament_selection_constant)
    king = competitors[0]

    for k in range(1, tournament_selection_constant):
        if competitors[k].fitness > king.fitness:
            king = competitors[k]

    return king


def genetic_algorithm_tournament_selection(cars) -> np.ndarray:
    parent1 = tournament_selection(cars, TOURNAMENT_SIZE)
    parent2 = tournament_selection(cars, TOURNAMENT_SIZE)

    while parent1 is parent2:
        parent2 = tournament_selection(cars, TOURNAMENT_SIZE)

    child_genes = genome_crosser(parent1, parent2,)

    return child_genes

def draw_scene() -> None:

    SCREEN.blit(background, (0, 0))

    for car in cars:

        if car.alive:
            car.draw(SCREEN)

    pygame.display.flip()

def create_next_generation() -> list:
    new_cars = []

    for _ in range(NUMBER_OF_ENTITIES):
        child_genome = genetic_algorithm_tournament_selection(cars)
        new_car = Car(child_genome)
        new_cars.append(new_car)

    return new_cars
    

""" def mutation():
    pass """

def generation_finished() -> bool:
    for car in cars:
        if car.alive == True:
            return False
    return True


def main():
    global cars
    clock = pygame.time.Clock()
    run = True

    first_creation(NUMBER_OF_ENTITIES)

    while run:
        dt = clock.tick(FPS)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        run_cars(dt)

        if generation_finished():
            generation_counter += 1
            cars = create_next_generation()

        draw_scene()

    pygame.quit()


if __name__ == "__main__":
    main()
