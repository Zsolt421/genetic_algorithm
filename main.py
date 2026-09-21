import pygame
import math
import os
import random
pygame.init()

WIDTH = 1000
HEIGHT = 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
NUMBER_OF_ENTITIES = 100
NUMBER_OF_GENES = 32
NUMBER_OF_SENSORS = 16
GEN_MIN = 0
GEN_MAX = 1
TOURNAMENT_SIZE = 5
generation_counter = 1
pygame.display.set_caption(f"Iteration: {generation_counter}")
cars = []

folder = os.path.dirname(__file__)

background = pygame.image.load(
    os.path.join(folder, "track.png")
)

background = pygame.transform.scale(
    background, (WIDTH, HEIGHT)
)

# -------------------------
# CAR APPEARANCE AND SETTINGS
# -------------------------

car_length = 50
car_width = 30

car_surface = pygame.Surface(
    (car_length, car_width), pygame.SRCALPHA
)

car_surface.fill((220, 20, 20))

# -------------------------
# CAR MOVEMENT SETTINGS
# -------------------------

x = WIDTH / 2
y = HEIGHT / 2 - 10

# 0 = facing right
angle = math.radians(-45)

wheel_distance = 40

MAX_SPEED = 150
TURN_SPEED = 60


class Car:
    def __init__(self, genome):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = MAX_SPEED
        self.alive = True
        self.fitness = 0
        self.genome = genome

def first_creation(NUMBER_OF_ENTITIES, NUMBER_OF_GENES) -> None:

    for j in range(NUMBER_OF_ENTITIES):
        genome = []

        for i in range(NUMBER_OF_GENES):
            genome.append(random.uniform(GEN_MIN, GEN_MAX))

        cars.append(Car(genome))

def genome_crosser(parent1, parent2) -> list:
    child_genes = []

    for i in range(len(parent1.genome)):
        choice = random.randint(1, 2)

        if choice == 1:
            gene = parent1.genome[i]
            child_genes.append(gene)
        else:
            gene = parent2.genome[i]
            child_genes.append(gene)

    return child_genes

def tournament_selection(cars, tournament_selection_constant) -> Car:
    competitors = random.sample(cars, tournament_selection_constant)
    king = competitors[0]

    for k in range(1, tournament_selection_constant):
        if competitors[k].fitness > king.fitness:
            king = competitors[k]

    return king


def genetic_algorithm_tournament_selection(cars) -> list:
    parent1 = tournament_selection(cars, TOURNAMENT_SIZE)
    parent2 = tournament_selection(cars, TOURNAMENT_SIZE)

    while parent1 is parent2:
        parent2 = tournament_selection(cars, TOURNAMENT_SIZE)

    child_genes = genome_crosser(parent1, parent2,)

    return child_genes


def main():
    global x, y, angle
    clock = pygame.time.Clock()
    run = True

    first_creation(NUMBER_OF_ENTITIES, NUMBER_OF_GENES)

    while run:
        dt = clock.tick(FPS)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        ## kiszámolja az autó pozícioját
        ## returnolj x és y és angle
        ##bemenet: érzékelő(0,1), gén(x-y között),MAX_SPEED??,TURN_SPEED??
        #gén elérési utja: car.self.genome[i]0-15balkerék, 16-31jobb kerék

        #kerék_sebesség_változó = matrix_dot_product()
        # Rotate the original car surface
        rotated_car = pygame.transform.rotate(car_surface, -math.degrees(angle))

        # Put the center of the rotated car at x, y
        rect = rotated_car.get_rect(center=(int(x), int(y)))

        # Draw background
        SCREEN.blit(background, (0, 0))
        # Draw car
        SCREEN.blit(rotated_car, rect)

        # Show finished frame
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()