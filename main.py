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
MAX_SPEED = 150
TARGET_AVERAGE_SPEED = 100
SPEED_CONTROL_GAIN = 2.0
TURN_SPEED = 60
TIMEOUT = 25
CHECKPOINT_GATE_SEARCH_LIMIT = 220

# -------------------------
# SENSOR VALUES
# -------------------------

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

CHECKPOINT_CENTERS = [
    (320, 955),
    (245, 930),
    (180, 870),
    (130, 790),
    (115, 700),
    (130, 610),
    (175, 525),
    (225, 445),
    (226, 372),
    (224, 241),
    (318, 187),
    (410, 175),
    (520, 160),
    (640, 155),
    (760, 160),
    (875, 160),
    (980, 148),
    (1048, 128),
    (1188, 115),
    (1186, 87),
    (1142, 229),
    (1110, 270),
    (1120, 335),
    (1180, 385),
    (1260, 420),
    (1310, 500),
    (1330, 600),
    (1320, 705),
    (1295, 800),
    (1240, 875),
    (1160, 915),
    (1070, 925),
    (965, 920),
    (860, 905),
    (755, 910),
    (650, 940),
    (545, 970),
    (430, 985),
]



generation_counter = 1
cars = []


# -------------------------
# PYGAME LOAD IN
# -------------------------

pygame.display.set_caption(f"Iteration: {generation_counter}")
folder = os.path.dirname(__file__)
background = pygame.image.load(os.path.join(folder, "round_track.png"))
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
        self.previous_x = self.x
        self.previous_y = self.y

    def read_sensors(self) -> tuple[np.ndarray, list[float]]:

        sensor_values = np.empty((NUM_OF_GENE_COLUMNS, 3))

        # érzékelők indulópontja: az autó eleje
        
        origin_x = self.x + math.cos(self.angle) * SENSOR_ORIGIN_OFFSET
        origin_y = self.y + math.sin(self.angle) * SENSOR_ORIGIN_OFFSET
        sensor_origin = [origin_x, origin_y]
     
        for distance_index, distance in enumerate(SENSOR_DISTANCES):

            for angle_index, relative_angle in enumerate(SENSOR_ANGLES):

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
                    

                i = distance_index * len(SENSOR_ANGLES) + angle_index
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
        self.previous_x = self.x
        self.previous_y = self.y
        forward_speed = (self.left_wheel_speed + self.right_wheel_speed) / 2  #checks the forward speed
        average_acceleration = (right_wheel_acceleration + left_wheel_acceleration) / 2  # acceleration based on the sensors

        #calculates how far the car's forward speed is from the target speed and corrects it.
        speed_correction = (SPEED_CONTROL_GAIN * (TARGET_AVERAGE_SPEED - forward_speed)- average_acceleration)


        right_wheel_speed = (self.right_wheel_speed + (right_wheel_acceleration + speed_correction) * dt)
        left_wheel_speed = (self.left_wheel_speed + (left_wheel_acceleration + speed_correction) * dt)

        forward_speed = np.clip((right_wheel_speed + left_wheel_speed) / 2, -MAX_SPEED, MAX_SPEED) 
        differential_speed = (right_wheel_speed - left_wheel_speed) / 2
        max_differential_speed = MAX_SPEED - abs(forward_speed)

        differential_speed = np.clip(differential_speed, -max_differential_speed, max_differential_speed) #difference of the two wheels' speed.
        self.right_wheel_speed = forward_speed + differential_speed
        self.left_wheel_speed = forward_speed - differential_speed

        delta_angle = (self.left_wheel_speed - self.right_wheel_speed) / WHEEL_DISTANCE * dt
        self.angle += delta_angle


        self.x += (np.cos(self.angle) * forward_speed * dt)
        self.y += (np.sin(self.angle) * forward_speed * dt)

        #? lehet enelkul is mukodik?
        self.rect.center = (round(self.x), round(self.y))

        return None

    
    def check_checkpoint(self) -> None:
        if self.checkpoint_index < len(CHECKPOINT_CENTERS):
            if checkpoint_gate_was_crossed(
                self.previous_x,
                self.previous_y,
                self.x,
                self.y,
                self.checkpoint_index,
            ):
                self.checkpoint_index += 1

    def calculate_fitness(self) -> None:
        max_distance = math.hypot(WIDTH, HEIGHT)
        checkpoint_reward = max_distance + 1

        if self.checkpoint_index < len(CHECKPOINT_CENTERS):
            target_x, target_y = CHECKPOINT_CENTERS[self.checkpoint_index]
            distance = math.hypot(self.x - target_x, self.y - target_y)
            progress_reward = max_distance - distance
            self.fitness = self.checkpoint_index * checkpoint_reward + progress_reward
        
        else:
            self.fitness = (
                len(CHECKPOINT_CENTERS) * checkpoint_reward
                + 1 / (1 + self.alive_time)
            )

    def draw(self, screen) -> None:
        rotated_car = pygame.transform.rotate(car_surface,-math.degrees(self.angle))
        rect = rotated_car.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_car, rect)

    @staticmethod
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
        if car.alive:
            car.alive_time += dt

            sensor_values, sensor_origin = car.read_sensors()

            right_wheel_acceleration, left_wheel_acceleration = car.calculate_controls(sensor_values)
            car.move(dt, right_wheel_acceleration, left_wheel_acceleration, WHEEL_DISTANCE)
            car.draw_sensors(sensor_values, sensor_origin)

            on_road = check_if_on_road(car.x, car.y)
            if on_road:
                car.check_checkpoint()

            if (
                not on_road
                or car.alive_time >= TIMEOUT
                or car.checkpoint_index >= len(CHECKPOINT_CENTERS)
            ):
                car.alive = False
                car.calculate_fitness()


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


def build_checkpoint_gates() -> list[tuple[tuple[float, float], tuple[float, float]]]:
    #uses two checkpoints to define a normal vector between them, then searches for the road edges along that normal vector to define a gate.

    gates = []
    checkpoint_centers = CHECKPOINT_CENTERS
    start_point = (STARTING_X, STARTING_Y)

    for index, (center_x, center_y) in enumerate(checkpoint_centers):
        previous_point = start_point if index == 0 else checkpoint_centers[index - 1]
        next_point = start_point if index == len(checkpoint_centers) - 1 else checkpoint_centers[index + 1]
        tangent_x = next_point[0] - previous_point[0]
        tangent_y = next_point[1] - previous_point[1]
        tangent_length = math.hypot(tangent_x, tangent_y)
        if tangent_length == 0:
            raise ValueError(f"Cannot determine track direction at checkpoint {index}")

        tangent_x /= tangent_length
        tangent_y /= tangent_length
        normal_x = -tangent_y
        normal_y = tangent_x
        endpoints = []

        for direction in (-1, 1):
            for distance in range(1, CHECKPOINT_GATE_SEARCH_LIMIT + 1):
                edge_x = center_x + direction * normal_x * distance
                edge_y = center_y + direction * normal_y * distance
                if not check_if_on_road(round(edge_x), round(edge_y)):
                    endpoints.append(
                        (
                            center_x + direction * normal_x * (distance + 2),
                            center_y + direction * normal_y * (distance + 2),
                        )
                    )
                    break
            else:
                raise ValueError(f"Could not find a road edge for checkpoint {index}")

        gates.append((endpoints[0], endpoints[1]))

    return gates


CHECKPOINT_GATES = build_checkpoint_gates()


def checkpoint_gate_was_crossed(self) -> bool:
    gate_start, gate_end = CHECKPOINT_GATES[self.checkpoint_index]

    #calculates how far did the car get from previous to current position (from previous to self.x and self.y)
    move_x, move_y = self.x - self.previous_x, self.y - self.previous_y
    gate_x, gate_y = gate_end[0] - gate_start[0], gate_end[1] - gate_start[1]
    
    denominator = move_x * gate_y - move_y * gate_x
    if denominator == 0:
        return False

    offset_x, offset_y = gate_start[0] - self.previous_x, gate_start[1] - self.previous_y

    move_fraction = (offset_x * gate_y - offset_y * gate_x) / denominator
    gate_fraction = (offset_x * move_y - offset_y * move_x) / denominator
    return 0 <= move_fraction <= 1 and 0 <= gate_fraction <= 1


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

    for gate_start, gate_end in CHECKPOINT_GATES:
        pygame.draw.line(
            SCREEN,
            (255, 255, 0),
            (round(gate_start[0]), round(gate_start[1])),
            (round(gate_end[0]), round(gate_end[1])),
            3,
        )

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
    global cars, generation_counter
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
