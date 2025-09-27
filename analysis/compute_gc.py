import pandas as pd
from pathlib import Path

runs_path = Path("data/derived/runs.csv")
if not runs_path.exists():
    raise SystemExit("No runs.csv found. Run the harness first.")

df = pd.read_csv(runs_path)

# Aggregate per (task_id, variant)
agg = df.groupby(["task_id","variant"]).agg(
    runtime_s=("runtime_s","mean"),
    mem_kib=("mem_kib","mean"),
    flops=("flops", "mean"),
    energy_j=("energy_j","mean"),
    correct=("correct","max"),
    n=("runtime_s","size")
).reset_index()

# Baseline is any variant named 'baseline' for each task_id
base = agg[agg["variant"]=="baseline"][["task_id","runtime_s","mem_kib","flops","energy_j"]].rename(columns={
    "runtime_s":"runtime_base","mem_kib":"mem_base","flops":"flops_base","energy_j":"energy_base"
})
merged = agg.merge(base, on="task_id", how="left")

def safe_pd(a, b):
    if a is None or a == 0 or pd.isna(a):
        return 0.0
    if b is None or pd.isna(b):
        return 0.0
    return (a - b) / a

merged["pd_runtime"] = (merged["runtime_base"] - merged["runtime_s"]) / merged["runtime_base"]
merged["pd_memory"]  = (merged["mem_base"]     - merged["mem_kib"])  / merged["mem_base"]
merged["pd_flops"]   = (merged["flops_base"]   - merged["flops"])    / merged["flops_base"]
merged["pd_energy"]  = (merged["energy_base"]  - merged["energy_j"]) / merged["energy_base"]

for c in ["pd_runtime","pd_memory","pd_flops","pd_energy"]:
    merged[c] = merged[c].fillna(0.0)

# Correctness filter (0/1)
for c in ["pd_runtime","pd_memory","pd_flops","pd_energy"]:
    merged[c] = merged[c] * merged["correct"]

# GC = sum of positive PDs
merged["gc"] = merged[["pd_runtime","pd_memory","pd_flops","pd_energy"]].clip(lower=0).sum(axis=1)

out_pd = merged[["task_id","variant","correct","pd_runtime","pd_memory","pd_flops","pd_energy"]]
out_gc = merged[["task_id","variant","gc","correct"]]

out_pd.to_csv("data/derived/pd_table.csv", index=False)
out_gc.to_csv("data/derived/gc_table.csv", index=False)

print("=== PD (Performance Delta) with correctness filter ===")
print(out_pd.sort_values(["task_id","variant"]).to_string(index=False))
print("\n=== GC (Green Capacity: sum of positive PDs) ===")
print(out_gc.sort_values(["task_id","variant"]).to_string(index=False))
print("\nSaved: data/derived/pd_table.csv, data/derived/gc_table.csv")
