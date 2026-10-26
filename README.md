# Genetic algorithm car simulation

Run a new simulation from the project folder:

```powershell
python main.py
```

When a generation finishes, its full population, genes, fitness values, and
best-car information are saved as JSON in a new folder under `results/`.
Fitness statistics for each saved generation are also recorded in
`summary.csv` in that run folder.

To continue evolving from a saved generation, provide its number and the
folder containing its JSON file:

```powershell
python main.py --resume-generation 3 --run-directory "results\run_20261025_112500"
```

Replace the example folder with the actual run folder under `results/`. The
saved generation is copied into a new run folder, and the simulation creates
the next generation from its cars. This keeps the original run unchanged.
Only completed generations are saved; closing the simulation during a
generation does not checkpoint its in-progress cars.