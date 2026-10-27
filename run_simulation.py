import csv
import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "inputs" / "simulation_config.json"
CENTRES_PATH = BASE_DIR / "inputs" / "work_centre_baseline.csv"
ELIGIBILITY_PATH = BASE_DIR / "inputs" / "reallocation_eligibility.csv"
OUTPUT_PATH = BASE_DIR / "results" / "simulation_output.csv"


def read_centres(path):
    """Return {work_centre_id: row} with numeric columns converted to float."""
    with open(path, newline="", encoding="utf-8") as file:
        return {row["work_centre_id"]: {k: float(v) for k, v in row.items() if k != "work_centre_id"}
                for row in csv.DictReader(file)}


def read_eligibility(path):
    """Return {(donor, target): scheduled hours of donor workers qualified for target}."""
    with open(path, newline="", encoding="utf-8") as file:
        return {(row["donor"], row["target"]): float(row["eligible_hours"]) for row in csv.DictReader(file)}


def sample_normal(rng, spec, lower, upper=float("inf")):
    """Draw from Normal(mean, std_dev) and clip the value to [lower, upper]."""
    return min(max(rng.gauss(spec["mean"], spec["std_dev"]), lower), upper)


def reallocate(capacity, workload, eligible, share, absence):
    """Move capacity (hours) from centres with a surplus to centres with a gap.

    The most loaded centres are served first and receive hours from the least loaded donors.
    A transfer is limited by (i) the donor's workers qualified for the target, (ii) the share of
    the donor's capacity that may be released, (iii) the donor's surplus and (iv) the target's gap.
    """
    capacity = dict(capacity)
    budget = {c: share * hours for c, hours in capacity.items()}
    load = {c: workload[c] / capacity[c] for c in capacity}          # workload-to-capacity ratio
    for target in sorted(load, key=load.get, reverse=True):
        for donor in sorted(load, key=load.get):
            gap = workload[target] - capacity[target]
            if load[donor] >= load[target] or gap <= 0:
                break
            surplus = capacity[donor] - workload[donor]
            moved = min(eligible[(donor, target)] * (1 - absence), budget[donor], surplus, gap)
            if moved > 0:
                capacity[donor] -= moved
                capacity[target] += moved
                budget[donor] -= moved
    return capacity


def run_trial(rng, scenario, centres, eligible):
    """Simulate one month and return the sampled inputs and the KPIs."""
    inputs = scenario["inputs"]
    multiplier = sample_normal(rng, inputs["workload_multiplier"], lower=0.0)
    absence = sample_normal(rng, inputs["worker_absence_rate"], lower=0.0, upper=1.0)

    workload = {c: multiplier * p["january_workload_h"] for c, p in centres.items()}
    capacity = {c: p["scheduled_workforce_h"] * (1 - absence) * p["equipment_availability"]
                for c, p in centres.items()}
    capacity = reallocate(capacity, workload, eligible,
                          scenario["decision_variables"]["reallocation_share"], absence)

    unfinished = {c: max(0.0, workload[c] - capacity[c]) for c in centres}
    total_workload, total_capacity = sum(workload.values()), sum(capacity.values())
    total_unfinished = sum(unfinished.values())

    row = {
        "reallocation_share": scenario["decision_variables"]["reallocation_share"],
        "workload_multiplier": round(multiplier, 4),
        "absence_rate": round(absence, 4),
        "total_workload_h": round(total_workload, 2),
        "total_capacity_h": round(total_capacity, 2),
        "workload_to_capacity_pct": round(100 * total_workload / total_capacity, 2),
        "unfinished_workload_h": round(total_unfinished, 2),
        "workload_served_pct": round(100 * (1 - total_unfinished / total_workload), 2),
        "shortfall": int(total_unfinished > 0),
        "overloaded_centres": sum(1 for u in unfinished.values() if u > 0),
    }
    row.update({f"unfinished_{c}_h": round(u, 2) for c, u in unfinished.items()})
    return row


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    centres, eligible = read_centres(CENTRES_PATH), read_eligibility(ELIGIBILITY_PATH)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as file:
        for count in config["simulation_counts"]:
            for scenario in config["scenarios"]:
                # Re-seeding per experiment gives every scenario the same random draws
                # (common random numbers), so scenarios differ only through their parameters.
                rng = random.Random(config["seed"])
                for replication in range(1, count + 1):
                    row = {"scenario": scenario["name"], "simulation_count": count,
                           "replication": replication, "seed": config["seed"]}
                    row.update(run_trial(rng, scenario, centres, eligible))
                    if writer is None:
                        writer = csv.DictWriter(file, fieldnames=list(row))
                        writer.writeheader()
                    writer.writerow(row)
            print(f"finished {count} replications for {len(config['scenarios'])} scenarios")
    print(f"Results written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
