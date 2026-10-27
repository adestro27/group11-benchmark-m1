from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
WORKBOOK = BASE_DIR / "inputs" / "group11_p2_data_analysis.xlsx"

MONTH_START, MONTH_END = "2024-01-01", "2024-02-01"   # only month with workforce and equipment data
SHIFT_DAYS, SHIFT_HOURS = 22, 7                      # working days in the workforce data, hours per shift

# Skill (as written in the data) that qualifies a worker for each work centre.
SKILL_OF_CENTRE = {
    "WC-AOI": "Automated optical inspection",
    "WC-CLEAN": "Cleanroom integration",
    "WC-FINAL": "Final assembly",
    "WC-HAND": "Hand soldering and pre-wave assembly",
    "WC-PACK": "Final inspection and packaging",
    "WC-PRESS": "Press-fit",
    "WC-SMT": "Surface-mount assembly",
    "WC-TEST": "Functional and system test",
}


def main() -> None:
    workload = pd.read_excel(WORKBOOK, sheet_name="data_workload_capacity")
    workforce = pd.read_excel(WORKBOOK, sheet_name="data_workforce_capacity")
    equipment = pd.read_excel(WORKBOOK, sheet_name="data_equipment_capacity")

    # January workload per work centre (operations planned to start in the month).
    start = pd.to_datetime(workload["planned_start_at"])
    january = workload[(start >= MONTH_START) & (start < MONTH_END)]
    workload_h = january.groupby("work_centre_id")["required_workload_hours"].sum()

    # Scheduled workforce hours per work centre. In the P2 data usable_workforce_hours equals
    # the scheduled hours (absence is recorded separately), so absence is applied in the simulation.
    scheduled_h = workforce.groupby("work_centre_id")["usable_workforce_hours"].sum()

    # Equipment availability = 1 - downtime hours / scheduled machine hours.
    downtime_h = equipment.groupby("work_centre_id")["downtime_duration_hours"].sum()
    machines = equipment.groupby("work_centre_id")["resource_id"].nunique()
    availability = 1 - downtime_h / (machines * SHIFT_DAYS * SHIFT_HOURS)

    centres = pd.DataFrame({
        "january_workload_h": workload_h,
        "scheduled_workforce_h": scheduled_h,
        "machines": machines,
        "downtime_h": downtime_h,
        "equipment_availability": availability,
    }).loc[list(SKILL_OF_CENTRE)].round(4)
    centres.index.name = "work_centre_id"
    centres.to_csv(BASE_DIR / "inputs" / "work_centre_baseline.csv")

    # Hours of each donor centre's workers who are also qualified for the target centre.
    skills = workforce["qualified_skills"].fillna("").astype(str)
    rows = []
    for donor in SKILL_OF_CENTRE:
        in_donor = workforce["work_centre_id"] == donor
        for target, skill in SKILL_OF_CENTRE.items():
            if donor == target:
                continue
            qualified = in_donor & skills.str.contains(skill, regex=False)
            rows.append((donor, target, workforce.loc[qualified, "usable_workforce_hours"].sum()))
    pd.DataFrame(rows, columns=["donor", "target", "eligible_hours"]).to_csv(
        BASE_DIR / "inputs" / "reallocation_eligibility.csv", index=False)

    # Parameters used in simulation_config.json (printed for traceability).
    daily = january.groupby(pd.to_datetime(january["planned_start_at"]).dt.date)["required_workload_hours"].sum()
    print(centres)
    print(f"Daily workload: mean {daily.mean():.2f} h, sd {daily.std():.2f} h, n = {len(daily)} days")
    print(f"Monthly workload CV = daily CV / sqrt(n) = {daily.std() / daily.mean() / len(daily) ** 0.5:.3f}")


if __name__ == "__main__":
    main()
