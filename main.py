import pygame
import math
import os
import random
import numpy as np

pygame.init()

# -------------------------
# VARIABLE DEFINITION
# -------------------------

WIDTH = 1000
HEIGHT = 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
NUMBER_OF_ENTITIES = 100
#NUMBER_OF_GENES = 32
NUM_OF_GENE_ROWS = 2
NUM_OF_GENE_COLUMNS = 16
NUMBER_OF_SENSORS = 16
GEN_MIN = 0
GEN_MAX = 1
TOURNAMENT_SIZE = 5
MAX_SPEED = 150
TURN_SPEED = 60



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

STARTING_X = 265
STARTING_Y = 627
STARTING_ANGLE = math.radians(-166)
wheel_distance = 40
car_length = 50
car_width = 30
car_surface = pygame.Surface(
    (car_length, car_width), pygame.SRCALPHA)
car_surface.fill((220, 20, 20))



class Car:
    def __init__(self, genome):
        self.x = STARTING_X
        self.y = STARTING_Y
        self.angle = STARTING_ANGLE
        self.speed = MAX_SPEED
        self.alive = True
        self.fitness = 0
        self.genome = genome
        self.checkpoint_index = 0

    def read_sensors(self):
        pass

    def calculate_controls(self):
        # A szenzorértékek és a genom alapján kiszámolja,
        # hogyan mozogjon az autó.
        return

    def move(self, dt):
        # Frissíti az autó pozícióját és irányát az eltelt idő alapján.
          
        pass

    def check_road(self):
        # Ellenőrzi, hogy az autó még az úton van-e.
        # Ha lement róla, alive = False.
        color = background.get_at((int(self.x), int(self.y)))

        r = color.r
        g = color.g
        b = color.b

        if g > r + 30 and g > b + 30:
            return True

        return False

    
    def check_checkpoint(self):
        # Ellenőrzi, hogy az autó elérte-e a következő checkpointot.
        pass

    def calculate_fitness(self):
        pass

    def draw(self, screen):
        pass

def run_cars(dt) -> None:
    for car in cars:
        Car.read_sensor()

        ##

        Car.check_road()
        Car.check_checkpoint()
        Car.calculate_fitness()
        Car.draw(SCREEN)

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
            cars = create_next_generation()

        draw_scene()

    pygame.quit()


if __name__ == "__main__":
    main()
