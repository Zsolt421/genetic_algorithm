import pygame
import math
import os
import numpy as np
import renderer
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
import shutil


# -------------------------
# *VARIABLE DEFINITION
# -------------------------

WIDTH = 1448
HEIGHT = 1086
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 675
SCREEN = None
GAME_SURFACE = None
FPS = 60
SIM_DT = 2 / 30
NUMBER_OF_ENTITIES = 100

NUM_OF_GENE_ROWS = 3
NUM_OF_GENE_COLUMNS = 16

GEN_MIN = -1
GEN_MAX = 1

TOURNAMENT_SIZE = 5
#TARGET_AVERAGE_SPEED = 100
#SPEED_CONTROL_GAIN = 2.0
MAX_SPEED = 150
GRASS_SPEED_MULTIPLIER = 0.4
GRASS_PENALTY_PER_SECOND = 50.0

NUMBER_OF_ELITE = 1




# -------------------------
# *Bools
# -------------------------

DRAW = True
MUTATION = True
GRASS_ALLOWED = True
MUTATION_CHANCE = 70
TIMEOUT = 25

GEN_MEAN = 0
GEN_STD = 0.5

SENSOR_RADIUS = 3

# Ennyivel induljon az érzékelés az autó középpontja előtt
SENSOR_ORIGIN_OFFSET = 20

generation_counter = 1
cars = []


RESULTS_DIR = Path(__file__).resolve().parent / "results"
SUMMARY_FIELDS = [
    "generation",
    "seed",
    "best_fitness",
    "average_fitness",
]


# -------------------------
# *PYGAME LOAD IN
# -------------------------

pygame.display.set_caption(f"Iteration: {generation_counter}")
folder = os.path.dirname(__file__)
background = pygame.image.load(os.path.join(folder, "round_track.png"))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


# -------------------------
# *CAR STARTING SETTINGS
# -------------------------

STARTING_X = 915
STARTING_Y = 915
STARTING_ANGLE = math.radians(-190)
WHEEL_DISTANCE = 0.1 
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
        self.alive = True
        self.fitness = 0
        self.genome = genome
        self.alive_time = 0
        self.grass_time = 0
        self.previous_x = self.x
        self.previous_y = self.y
        self.sensor_values = np.empty((NUM_OF_GENE_COLUMNS, 3))
        self.sensor_origin = []


    def read_sensors(self) -> None:

        sensord_1 = round(1.0 + self.genome[2][2] * 50)
        sensor_distances = [sensord_1, 2 * sensord_1, 3 * sensord_1, 4 * sensord_1]

        sensor_1 = round((1.0 + self.genome[2][0]) * 45)
        sensor_2 = round(sensor_1 * self.genome[2][0])
        sensor_3 = round((1.0 + self.genome[2][7]) * 45)
        sensor_4 = round(sensor_1 * self.genome[2][8])
        sensor_angles = [sensor_1, sensor_2, -1 * sensor_3, -1 * sensor_4]

        # érzékelők indulópontja: az autó eleje
        
        origin_x = self.x + math.cos(self.angle) * SENSOR_ORIGIN_OFFSET
        origin_y = self.y + math.sin(self.angle) * SENSOR_ORIGIN_OFFSET
        self.sensor_origin = [origin_x, origin_y]

        for distance_index, distance in enumerate(sensor_distances):

            for angle_index, relative_angle in enumerate(sensor_angles):

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
                    

                i = distance_index * len(sensor_angles) + angle_index
                self.sensor_values[i, 0] = value
                self.sensor_values[i, 1] = sensor_x
                self.sensor_values[i, 2] = sensor_y

        return None


    def calculate_controls(self) -> tuple[float, float]: 
        # A szenzorértékek és a genom alapján kiszámolja, hogyan mozogjon az autó.
        # sensors_vector = np.array(sensor_values)
        output = np.dot(self.genome[:2], self.sensor_values[:, 0])

        right_wheel_acceleration = output[0]
        left_wheel_acceleration = output[1]

        return right_wheel_acceleration, left_wheel_acceleration


    def move(self, dt, right_wheel_acceleration, left_wheel_acceleration, WHEEL_DISTANCE, on_road) -> None:
        
        self.angle += (right_wheel_acceleration - left_wheel_acceleration) * ((1.0 + self.genome[2][4])/10)

        if not on_road and GRASS_ALLOWED:
            speed_multiplier = GRASS_SPEED_MULTIPLIER
        else: speed_multiplier = 1.0
        speed_limit = ((1.5 + self.genome[2][5]) * 100) * speed_multiplier

        self.x += (np.cos(self.angle) * speed_limit * dt)
        self.y += (np.sin(self.angle) * speed_limit * dt)
        self.rect.center = (round(self.x), round(self.y))

        return None


    def calculate_fitness(self, dt) -> None:
        distance_x = self.x - self.previous_x
        distance_y = self.y - self.previous_y

        full_distance = 0
        full_displacement = 0
        displacement_timer = 0

        distance = np.sqrt(distance_x**2 + distance_y**2)
        full_distance += distance

        previous_displacement_x = self.x
        previous_displacement_y = self.y

        displacement_interval = 1.0
        displacement_timer += dt

        if displacement_timer >= displacement_interval:
            x_displacement = self.x - previous_displacement_x
            y_displacement = self.y - previous_displacement_y

            full_displacement += np.sqrt(x_displacement**2 + y_displacement**2)

            previous_displacement_x = self.x
            previous_displacement_y = self.y

            displacement_timer = 0.0

        self.fitness += full_distance + full_displacement


    def draw(self, screen) -> None:
        rotated_car = pygame.transform.rotate(car_surface,-math.degrees(self.angle))
        rect = rotated_car.get_rect(center=(int(self.x), int(self.y)))

        if DRAW == True : self.draw_sensors()

        screen.blit(rotated_car, rect)
        

    def draw_sensors(self) -> None:
        if len(self.sensor_origin) < 2:
            return
        for value, sensor_x, sensor_y in self.sensor_values:
            pygame.draw.line(GAME_SURFACE, (100, 100, 100),
                self.sensor_origin, (sensor_x, sensor_y), 1)
            sensor_color = (255, 0, 0) if value == 0 else (0, 255, 0)
            pygame.draw.circle(GAME_SURFACE, sensor_color, (int(sensor_x), int(sensor_y)), SENSOR_RADIUS)

# -------------------------
# *Run Car
# -------------------------

def run_cars(dt) -> None:
    for car in cars:
        if car.alive:
            car.alive_time += dt

            car.read_sensors()

            right_wheel_acceleration, left_wheel_acceleration = car.calculate_controls()
            on_road_before_move = check_if_on_road(car.x, car.y)
            car.move(dt, right_wheel_acceleration, left_wheel_acceleration, WHEEL_DISTANCE, on_road_before_move)

            if GRASS_ALLOWED:
                on_road = check_if_on_road(car.x, car.y)
                in_bounds = 0 <= car.x < WIDTH and 0 <= car.y < HEIGHT
                if not on_road:
                    car.grass_time += dt

                if not in_bounds or car.alive_time >= TIMEOUT:
                    car.alive = False
                    car.calculate_fitness(dt)


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


def draw_scene() -> None:

    GAME_SURFACE.blit(background, (0, 0))

    for car in cars:
        if car.alive:
            car.draw(GAME_SURFACE)

    pygame.transform.smoothscale(GAME_SURFACE, SCREEN.get_size(), SCREEN)
    pygame.display.flip()

    return None


def first_creation(NUMBER_OF_ENTITIES) -> None:

    for _ in range(NUMBER_OF_ENTITIES):
        genome = np.random.uniform(GEN_MIN, GEN_MAX,(NUM_OF_GENE_ROWS, NUM_OF_GENE_COLUMNS))
        cars.append(Car(genome))

    return None


def genome_crosser(parent1, parent2) -> np.ndarray:
    child_genes = np.empty((NUM_OF_GENE_ROWS, NUM_OF_GENE_COLUMNS))

    for row in range(NUM_OF_GENE_ROWS):

        for column in range(NUM_OF_GENE_COLUMNS):

            if MUTATION and np.random.randint(MUTATION_CHANCE) == 0:
                child_genes[row][column] = np.random.uniform(GEN_MIN, GEN_MAX)

            else:
                choice = np.random.randint(1, 3)

                if choice == 1:
                    child_genes[row][column] = parent1.genome[row][column]

                else:
                    child_genes[row][column] = parent2.genome[row][column]

    return child_genes


def tournament_selection(cars, tournament_selection_constant) -> Car:
    indices = np.random.choice(len(cars), tournament_selection_constant, replace=False)
    competitors = [cars[i] for i in indices]
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


def top_selection(cars, n) -> list:
    ranked_cars = sorted(cars, key=lambda car: car.fitness, reverse=True)
    return ranked_cars[:n]


def create_next_generation() -> list:
    new_cars = []
    top = top_selection(cars, NUMBER_OF_ELITE)
    for i in range(NUMBER_OF_ELITE):
        new_cars.append(Car(top[i].genome.copy()))
    print(top[0].fitness)
    for _ in range(NUMBER_OF_ELITE, NUMBER_OF_ENTITIES):
        child_genome = genetic_algorithm_tournament_selection(cars)
        new_car = Car(child_genome)
        new_cars.append(new_car)

    return new_cars


def generation_finished() -> bool:
    for car in cars:
        if car.alive == True:
            return False
    return True


def save_generation(
    cars: list[Car],
    generation_number: int,
    run_directory: Path,
    seed: int | None,
) -> None:
    if not cars:
        raise ValueError("Cannot save a generation without cars.")

    best_car = max(cars, key=lambda car: car.fitness)
    generation_data = {
        "generation": generation_number,
        "population_size": len(cars),
        "best_fitness": float(best_car.fitness),
        "average_fitness": float(np.mean([car.fitness for car in cars])),
        "best_genome": best_car.genome.tolist(),
        "cars": [
            {
                "genome": car.genome.tolist(),
                "fitness": float(car.fitness),
                #"checkpoint_index": car.checkpoint_index,
                "alive_time": float(car.alive_time),
                "grass_time": float(car.grass_time),
            }
            for car in cars
        ],
    }
    if generation_number == 1:
        if seed is None:
            raise ValueError("Generation 1 must be saved with its random seed.")
        generation_data["seed"] = seed

    generation_path = run_directory / f"generation_{generation_number:04}.json"

    with generation_path.open("x", encoding="utf-8") as generation_file:
        json.dump(generation_data, generation_file, indent=2, allow_nan=False)

    append_generation_summary(generation_data, run_directory)

    print(f"Saved generation {generation_number} to {generation_path}")


def append_generation_summary(generation_data: dict, run_directory: Path) -> None:
    summary_path = run_directory / "summary.csv"
    summary_exists = summary_path.exists()
    with summary_path.open("a", newline="", encoding="utf-8") as summary_file:
        writer = csv.DictWriter(summary_file, fieldnames=SUMMARY_FIELDS)
        if not summary_exists:
            writer.writeheader()
        writer.writerow({field: generation_data.get(field, "") for field in SUMMARY_FIELDS})


def load_generation(generation_number: int, run_directory: Path) -> list[Car]:
    generation_path = run_directory / f"generation_{generation_number:04}.json"
    with generation_path.open("r", encoding="utf-8") as generation_file:
        generation_data = json.load(generation_file)

    if generation_data.get("generation") != generation_number:
        raise ValueError(f"{generation_path} does not contain generation {generation_number}.")

    saved_cars = generation_data.get("cars")
    if not isinstance(saved_cars, list) or not saved_cars:
        raise ValueError(f"{generation_path} does not contain a non-empty car population.")

    loaded_cars = []
    expected_shape = (NUM_OF_GENE_ROWS, NUM_OF_GENE_COLUMNS)
    for index, saved_car in enumerate(saved_cars):
        genome = np.asarray(saved_car["genome"], dtype=float)
        if genome.shape != expected_shape:
            raise ValueError(
                f"Car {index} in {generation_path} has genome shape {genome.shape}; "
                f"expected {expected_shape}."
            )

        car = Car(genome)
        car.fitness = float(saved_car["fitness"])
        #car.checkpoint_index = int(saved_car["checkpoint_index"])
        car.alive_time = float(saved_car["alive_time"])
        car.grass_time = float(saved_car["grass_time"])
        loaded_cars.append(car)

    if len(loaded_cars) != NUMBER_OF_ENTITIES:
        raise ValueError(
            f"{generation_path} contains {len(loaded_cars)} cars; "
            f"the current simulation expects {NUMBER_OF_ENTITIES}."
        )

    return loaded_cars


def create_run_directory(name_suffix: str = "") -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"run_{timestamp}{'_' + name_suffix if name_suffix else ''}"
    run_directory = RESULTS_DIR / run_name
    suffix = 1
    while run_directory.exists():
        run_directory = RESULTS_DIR / f"{run_name}_{suffix}"
        suffix += 1
    run_directory.mkdir()
    return run_directory


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the car genetic algorithm.")
    parser.add_argument(
        "--resume-generation",
        type=int,
        help="Continue evolving from this saved generation.",
    )
    parser.add_argument(
        "--run-directory",
        type=Path,
        help="Existing results/run_... directory to load the saved generation from.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for a new run. Reuse a run's generation 1 seed to reproduce it.",
    )
    arguments = parser.parse_args()

    if arguments.resume_generation is not None:
        if arguments.resume_generation < 1:
            parser.error("--resume-generation must be at least 1.")
        if arguments.run_directory is None:
            parser.error("--run-directory is required when resuming.")
        if arguments.seed is not None:
            parser.error("--seed can only be used when starting a new run.")
    elif arguments.run_directory is not None:
        parser.error("--run-directory can only be used with --resume-generation.")

    return arguments


def main():
    global cars, generation_counter, SCREEN, GAME_SURFACE
    arguments = parse_arguments()

    seed_input = input("Enter a seed, or press Enter for a random seed: ")

    if seed_input == "":
        SEED = int(np.random.SeedSequence().generate_state(1)[0])
    else:
        SEED = int(seed_input)

    np.random.seed(SEED)
    run_seed = SEED

    print(f"Seed used: {SEED}")

    # Only now start Pygame
    pygame.init()

    SCREEN = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    GAME_SURFACE = pygame.Surface(
        (WIDTH, HEIGHT)
    )

    clock = pygame.time.Clock()
    run = True

    if arguments.resume_generation is not None:
        source_directory = arguments.run_directory.resolve()

        if not source_directory.is_dir():
            raise FileNotFoundError(
                f"Results directory does not exist: {source_directory}"
            )

        cars = load_generation(
            arguments.resume_generation,
            source_directory
        )

        source_generation_path = (
            source_directory
            / f"generation_{arguments.resume_generation:04}.json"
        )

        with source_generation_path.open(
            "r",
            encoding="utf-8"
        ) as generation_file:
            source_generation_data = json.load(generation_file)

        run_directory = create_run_directory(
            f"from_generation_{arguments.resume_generation:04}"
        )

        shutil.copy2(
            source_generation_path,
            run_directory / source_generation_path.name
        )

        append_generation_summary(
            source_generation_data,
            run_directory
        )

        generation_counter = arguments.resume_generation + 1
        cars = create_next_generation()

        print(
            f"Continuing with generation {generation_counter} from "
            f"{source_generation_path}; new results will be saved to "
            f"{run_directory}"
        )

    else:
        run_directory = create_run_directory()
        first_creation(NUMBER_OF_ENTITIES)

    pygame.display.set_caption(
        f"Iteration: {generation_counter}"
    )

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        run_cars(SIM_DT)

        draw_scene()

        if generation_finished():
            print(clock.get_fps())
            save_generation(  cars, generation_counter, run_directory, run_seed)
            generation_counter += 1
            pygame.display.set_caption(f"Iteration: {generation_counter}")

            cars = create_next_generation()

    pygame.quit()

if __name__ == "__main__":
    main()
