# Genetic algorithm car simulation

Run a new simulation from the project folder:

```powershell
python main.py
```

The program creates a time-based seed automatically and saves it only with
generation 1. To repeat a run's random sequence, pass that seed when starting
a new run:

```powershell
python main.py --seed 123456789
```

Use the seed recorded in `generation_0001.json` or the first row of
`summary.csv`. Keep the same simulation settings and code for the run to be
reproducible.

When a generation finishes, its full population, genes, fitness values, and
best-car information are saved as JSON in a new folder under `results/`.
Fitness statistics for each saved generation are also recorded in
`summary.csv` in that run folder.

To resume evolution from a saved generation, provide its number and the folder
containing its JSON file:

```powershell
python main.py --resume-generation 3 --run-directory "results\run_20261025_112500"
```

Replace the example folder with the actual run folder under `results/`.
The saved population is used to create the next generation, and evolution
continues in a new results folder. Resuming does not reuse the original run's
random sequence, so it can develop differently.

Only completed generations are saved; closing the simulation during a
generation does not checkpoint its in-progress cars.