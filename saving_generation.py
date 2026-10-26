import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
import numpy as np



RESULTS_DIR = Path(__file__).resolve().parent / "results"
SUMMARY_FIELDS = [
    "generation",
    "best_fitness",
    "average_fitness",
    "best_checkpoint",
]



def save_generation(cars: list[Car], generation_number: int, run_directory: Path) -> None:
    if not cars:
        raise ValueError("Cannot save a generation without cars.")

    best_car = max(cars, key=lambda car: car.fitness)
    generation_data = {
        "generation": generation_number,
        "population_size": len(cars),
        "best_fitness": float(best_car.fitness),
        "average_fitness": float(np.mean([car.fitness for car in cars])),
        "best_checkpoint": best_car.checkpoint_index,
        "best_genome": best_car.genome.tolist(),
        "cars": [
            {
                "genome": car.genome.tolist(),
                "fitness": float(car.fitness),
                "checkpoint_index": car.checkpoint_index,
                "alive_time": float(car.alive_time),
                "grass_time": float(car.grass_time),
            }
            for car in cars
        ],
    }
    generation_path = run_directory / f"generation_{generation_number:04}.json"

#opens the file (x means it creates a new file, utf_8 is just an encoding version), if it already exists then raises an error
    with generation_path.open("x", encoding="utf-8") as generation_file:
        json.dump(generation_data, generation_file, indent=2, allow_nan=False)
        #nan = not a number - only allows numbers to be saved (kell e?)

    append_generation_summary(generation_data, run_directory)

    print(f"Saved generation {generation_number} to {generation_path}")


def append_generation_summary(generation_data: dict, run_directory: Path) -> None:
    summary_path = run_directory / "summary.csv"
    summary_exists = summary_path.exists()
    with summary_path.open("a", newline="", encoding="utf-8") as summary_file:
        #a = append, new text without erasing the previous ones
        writer = csv.DictWriter(summary_file, fieldnames=SUMMARY_FIELDS)
        if not summary_exists:
            writer.writeheader()
        writer.writerow({field: generation_data[field] for field in SUMMARY_FIELDS})


def load_generation(generation_number: int, run_directory: Path) -> list[Car]:
    generation_path = run_directory / f"generation_{generation_number:04}.json"
    with generation_path.open("r", encoding="utf-8") as generation_file:
        generation_data = json.load(generation_file)

#safety check
    if generation_data.get("generation") != generation_number:
        raise ValueError(f"{generation_path} does not contain generation {generation_number}.")

    saved_cars = generation_data.get("cars")
    #checks whith isinstance that saved_cars is a list or not and if it isn't in won't load it
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
        car.checkpoint_index = int(saved_car["checkpoint_index"])
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
        help="Continue evolving from this completed generation.",
    )
    parser.add_argument(
        "--run-directory",
        type=Path,
        help="Existing results/run_... directory to load the saved generation from.",
    )
    arguments = parser.parse_args()

    if arguments.resume_generation is not None:
        if arguments.resume_generation < 1:
            parser.error("--resume-generation must be at least 1.")
        if arguments.run_directory is None:
            parser.error("--run-directory is required when resuming.")
    elif arguments.run_directory is not None:
        parser.error("--run-directory can only be used with --resume-generation.")

    return arguments

#to load a generation:
#python main.py --resume-generation 3 --run-directory "results\run_20261025_124747"