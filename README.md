# Green Capacity Experiment — Ollama Edition

This repository is a **ready-to-run** harness to evaluate LLM-generated code using:
- **Ollama** for local inference (e.g., Llama 3 8B Instruct, quantized)
- **perf** for runtime + FLOPs
- **tracemalloc** for peak memory
- **Smart plug** for whole-system energy (manual input)

It also includes **prompt templates** and a **code generator** that saves model outputs as runnable Python modules.

---

## Quick Start

### 0) Prerequisites
- Linux (tested on Xubuntu 22.04)
- Python 3.10+
- `perf` (linux-tools): `sudo apt install linux-tools-common linux-tools-$(uname -r)`
- **Ollama**: follow https://ollama.com/download

### 1) Pull models
```bash
make ollama-pull
```

By default we use: `llama3:8b-instruct-q4_K_M`

### 2) Python deps
```bash
make init
```

### 3) Sanity tests
```bash
make test
```

### 4) Generate code with Ollama
Example: generate a **baseline** solution for the `inefficient_sort` task:
```bash
make gen-sort-baseline
```

This creates a file under `tasks/generated/inefficient_sort/... .py` plus a metadata JSON.

### 5) Measure a specific implementation
Provide **energy in Joules** from your smart plug (either per-run or total with `--energy-total`).

- Measure the **human baseline** reference implementation:
```bash
make measure-sort-human ENERGY=1200 RUNS=5
```

- Measure a **generated** implementation (pass the created module path):
```bash
python harness/run.py --task-id inefficient_sort --impl tasks.generated.inefficient_sort.AUTO_PICK   --variant llama3_baseline --runs 5 --energy 1200 --energy-total
```

`AUTO_PICK` automatically chooses the most recent generated file for that task.

### 6) Compute PD & GC
```bash
make analyse
```

Outputs:
- `data/derived/pd_table.csv`
- `data/derived/gc_table.csv`

---

## Repository Map

- `prompts/` — prompt templates (baseline, CoT, efficient, tagged/explained)
- `models/ollama/models.yaml` — list of models to pull
- `tasks/task_specs/` — task descriptions injected into prompts
- `tasks/reference/` — human baselines
- `tasks/generated/` — LLM outputs saved as modules
- `tasks/tests/` — pytest tests (sanity)
- `tasks/validators.py` — correctness validators per task
- `harness/generate.py` — Ollama generator (REST API)
- `harness/run.py` — measurement harness (perf + tracemalloc + smart plug energy)
- `analysis/compute_gc.py` — PD & GC computation (with correctness filter)
- `AGENT_TASKS.md` — step-by-step task list for an LLM agent to maintain/extend this repo

---

Generated on 2025-09-27 13:50:03.
