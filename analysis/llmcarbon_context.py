import argparse, pandas as pd

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-gco2-kwh", type=float, required=True, help="Grid intensity (gCO2/kWh)")
    ap.add_argument("--pue", type=float, default=1.1, help="Power Usage Effectiveness")
    ap.add_argument("--embodied-kg", type=float, default=0.0, help="Embodied kg CO2e (context)")
    args = ap.parse_args()

    df = pd.read_csv("data/derived/runs.csv")

    # Joules -> kWh; include PUE to account for infra overhead
    df["kwh"] = (df["energy_j"].fillna(0) * args.pue) / 3.6e6
    df["kg_co2e_operational"] = df["kwh"] * (args.grid_gco2_kwh / 1000.0)

    agg = df.groupby(["task_id","variant"]).agg(
        runs=("runtime_s","size"),
        kwh=("kwh","sum"),
        kg_co2e_operational=("kg_co2e_operational","sum")
    ).reset_index()

    total_op = agg["kg_co2e_operational"].sum()

    print("=== Operational carbon (task × variant) ===")
    print(agg.to_string(index=False))
    print(f"\nTotal operational kg CO2e: {total_op:.6f}")
    if args.embodied_kg > 0:
        print(f"Embodied kg CO2e (context): {args.embodied_kg:.2f}")
        print(f"Operational share: {100*total_op/(total_op+args.embodied_kg):.2f}%")
