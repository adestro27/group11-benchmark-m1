# M1 Project – Workforce reallocation dashboard

**Group:** 11

**Company:** Benchmark Electronics Almelo

**Topic:** Production capacity

## Members

- Alessandro Destro (3940438)
- Philipp Gawor (3339742)
- Thomas Hoogstede (3918246)
- Efe Karaöz (3756165)
- Colin de Roode (3927679)

## Project description

The simulation estimates how reallocating qualified workers between the eight production work centres
changes the share of the monthly workload that usable capacity can cover. One trial simulates one
production month (January 2024 as base month) with uncertain order volume and worker absence.
The KPIs are unfinished workload (hours), the risk of a capacity shortfall, and the share of the workload served
(a capacity-based proxy, **not** the true share of operations completed before their due date).

## Files

| File | Purpose |
|---|---|
| `run_simulation.py` | Runs all experiments and writes the CSV |
| `prepare_inputs.py` | Builds the two prepared input tables from the P2 Excel workbook |
| `inputs/simulation_config.json` | Seed, replication counts, scenarios, distributions and their sources |
| `inputs/work_centre_baseline.csv` | Prepared data: January workload, scheduled workforce hours, equipment availability per work centre |
| `inputs/reallocation_eligibility.csv` | Prepared data: scheduled hours of workers qualified for each target work centre |
| `inputs/group11_p2_data_analysis.xlsx` | P2 data workbook (source of the prepared tables) |
| `results/simulation_output.csv` | Per-trial output (one row per trial, 36,000 rows) |
| `group11_dashboard.xlsx` | Dashboard workbook (sheets described below) |

Sheets in `group11_dashboard.xlsx`:

| Sheet | Purpose |
|---|---|
| `Dashboard` | For the production manager: choose a demand scenario and reallocation share (yellow cells) and compare KPIs, charts and all six scenarios |
| `simulation_results` | Summary formulas per scenario (mean, SD, min, max, risk of shortfall, workload served) used by the dashboard |
| `simulation_output` | One row per simulated month, loaded by Power Query from `results/simulation_output.csv`. Do not edit |
| `Settings` | Works out where the results file is (`ProjectFolder`, `ResultsPath`), so the workbook finds it on any computer. Do not edit |

## Requirements

- Python 3.9 or newer.
- `run_simulation.py` uses the standard library only: no packages are required.
- `prepare_inputs.py` (optional) needs pandas and openpyxl: `python3 -m pip install pandas openpyxl`.
- Microsoft Excel 365 (Mac or Windows) with Power Query.

## Input sources

Distribution parameters and prepared tables come from the P2 workbook (MES, MDM, EAM and workforce data, January 2024).
Sources and assumptions per variable are in the `source` field of each input in `simulation_config.json`.

## Run

From the project folder:

    python3 run_simulation.py

The script regenerates `results/simulation_output.csv` on every run. The same seed gives the same output.
Every scenario uses the same random draws (common random numbers), so scenarios differ only through their parameters.

## Run a what-if analysis

1. Change a setting in `inputs/simulation_config.json` and save it (see below what can be changed).
2. From the project folder run:

       python3 run_simulation.py

   On Windows use `py run_simulation.py`. The script overwrites `results/simulation_output.csv`.
3. Open `group11_dashboard.xlsx` and choose **Data > Refresh All**. Power Query reloads the CSV and the
   `simulation_results` formulas, the dashboard and its charts update.

Keep the folder structure: the workbook looks for `results/simulation_output.csv` in its own folder.

## What can be changed in the configuration

Safe to change in each scenario: the `mean` and `std_dev` of `workload_multiplier` (1.15 = 15% more orders than
January 2024) and of `worker_absence_rate`, and the `seed`.

Known limitation: the scenario names (`baseline_realloc_0` … `surge_realloc_20`), the reallocation shares and the
replication counts (1,000 and 5,000) are used as fixed labels by the dashboard. Changing them without updating the
`simulation_results` sheet makes the dashboard show missing or wrong values.

## If something goes wrong

- **Refresh says the file cannot be found:** the workbook was moved out of the project folder, or the simulation
  has not been run. Check the path in `Settings!B2`.
- **Privacy levels / Formula.Firewall message:** Data > Get Data > Query Options > Privacy (Current Workbook) >
  Ignore the Privacy Levels, then refresh.
- **Dashboard did not change after a run:** refresh again and wait until it finishes; check that the config file
  was saved before running the script.
