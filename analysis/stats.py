import pandas as pd
from pathlib import Path
from scipy import stats
import itertools
import numpy as np

runs = Path("data/derived/runs.csv")
if not runs.exists():
    raise SystemExit("No runs.csv found. Run measurements first.")

df = pd.read_csv(runs)

def pairwise_tests(metric="runtime_s"):
    out = []
    for task, g in df.groupby("task_id"):
        g = g[g["correct"]==1]
        variants = sorted(g["variant"].unique())
        for (v1, v2) in itertools.combinations(variants, 2):
            a = g[g["variant"]==v1][metric].dropna()
            b = g[g["variant"]==v2][metric].dropna()
            if len(a) >= 2 and len(b) >= 2:
                # Check for nearly identical data that causes precision issues
                a_var = np.var(a)
                b_var = np.var(b)
                
                # Welch's t-test with precision check
                if a_var == 0 and b_var == 0:
                    # Both groups are constant - check if means are equal
                    t = 0.0 if np.mean(a) == np.mean(b) else np.inf
                    p = 1.0 if np.mean(a) == np.mean(b) else 0.0
                elif a_var == 0 or b_var == 0:
                    # One group is constant - may cause precision issues
                    try: 
                        t, p = stats.ttest_ind(a, b, equal_var=False)
                    except (RuntimeWarning, ValueError): 
                        t, p = np.nan, np.nan
                else:
                    # Normal case
                    try: t, p = stats.ttest_ind(a, b, equal_var=False)
                    except Exception: t, p = np.nan, np.nan
                
                # Mann-Whitney U test (more robust to identical values)
                try: w, p_w = stats.mannwhitneyu(a, b, alternative="two-sided")
                except Exception: w, p_w = np.nan, np.nan
                
                out.append({"task_id": task, "metric": metric, "v1": v1, "v2": v2, "t": t, "p_t": p, "mw": w, "p_mw": p_w})
    return pd.DataFrame(out)

def anova(metric="runtime_s"):
    out = []
    for task, g in df.groupby("task_id"):
        g = g[g['correct']==1]
        grouped = [grp[metric].dropna().values for _, grp in g.groupby("variant")]
        labels = list(dict.fromkeys(g["variant"]))
        if len(grouped) >= 2 and all(len(x) >= 2 for x in grouped):
            # Check if any group has constant values (variance = 0)
            variances = [np.var(x) for x in grouped]
            if all(v == 0 for v in variances):
                # All groups are constant - F statistic undefined
                f, p = np.nan, np.nan
            elif any(v == 0 for v in variances):
                # Some groups are constant - may still cause issues
                try: 
                    f, p = stats.f_oneway(*grouped)
                except (ValueError, RuntimeWarning): 
                    f, p = np.nan, np.nan
            else:
                # Normal case
                try: f, p = stats.f_oneway(*grouped)
                except Exception: f, p = np.nan, np.nan
            out.append({"task_id": task, "metric": metric, "f": f, "p": p, "k": len(grouped), "variants": ",".join(labels)})
    return pd.DataFrame(out)

metrics = ["runtime_s","mem_kib","flops","energy_j"]

for m in metrics:
    print(f"\n=== Pairwise ({m}) ===")
    dfp = pairwise_tests(m)
    print(dfp.to_string(index=False) if not dfp.empty else "(insufficient data)")

print("\n=== ANOVA (per metric) ===")
for m in metrics:
    dfa = anova(m)
    print(dfa.to_string(index=False) if not dfa.empty else f"(insufficient data for {m})")
