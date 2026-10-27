# M1 Project

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
| `group11_p3_analysis.xlsx` | Excel analysis (`simulation_output` and `simulation_results` sheets) |
| `group11_p3_simulation_report.pdf` | Report |

## Requirements

- Python 3.9 or newer.
- `run_simulation.py` uses the standard library only: no packages are required.
- `prepare_inputs.py` (optional) needs pandas and openpyxl: `python3 -m pip install pandas openpyxl`.

## Input sources

Distribution parameters and prepared tables come from the P2 workbook (MES, MDM, EAM and workforce data, January 2024).
Sources and assumptions per variable are in the `source` field of each input in `simulation_config.json`.

## Run

From the project folder:

    python3 run_simulation.py

The script regenerates `results/simulation_output.csv` on every run. The same seed gives the same output.
Every scenario uses the same random draws (common random numbers), so scenarios differ only through their parameters.

## Excel refresh

Open `group11_p3_analysis.xlsx` and choose Data > Refresh All. Power Query reloads `results/simulation_output.csv`
into the `simulation_output` sheet and the formulas and charts in `simulation_results` update.
If Excel asks for the file location, point the query to `results/simulation_output.csv` in this folder.