.PHONY: init test analyse stats llmcarbon ollama-pull gen-sort-baseline gen-mod-baseline measure-sort-human measure-mod-human

init:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

test:
	PYTHONPATH=. pytest -q

analyse:
	python analysis/compute_gc.py

stats:
	python analysis/stats.py

llmcarbon:
	python analysis/llmcarbon_context.py --grid-gco2-kwh $${GRID} --pue $${PUE} --embodied-kg $${EMB}

ollama-pull:
	python3 tools/ollama_pull.py

gen-sort-baseline:
	python -m harness.generate --task-id inefficient_sort --prompt baseline --model deepseek-coder:6.7b --with-codecarbon

gen-mod-baseline:
	python -m harness.generate --task-id modular_example --prompt baseline --model deepseek-coder:6.7b --with-codecarbon

measure-sort-human:
	python -m harness.run --task-id inefficient_sort --impl tasks.reference.inefficient_sort_human --variant baseline --runs 10 --warmup 2 --energy-source perf

measure-mod-human:
	python -m harness.run --task-id modular_example --impl tasks.reference.modular_example_human --variant baseline --runs 10 --warmup 2 --energy-source perf

gen-unit-baseline:
	python -m harness.generate --task-id unit_test_gen --prompt baseline --model deepseek-coder:6.7b --with-codecarbon

measure-unit-human:
	python -m harness.run --task-id unit_test_gen --impl tasks.reference.unit_test_gen_human --variant baseline --runs 10 --warmup 2 --energy-source perf

# === One-shot pipelines (generate → measure → analyse → stats) ===
# Defaults (override on CLI: MODEL=..., PROMPT=..., VARIANT=..., etc.)
MODEL ?= deepseek-coder:6.7b
PROMPT ?= baseline
VARIANT := $(shell echo $(MODEL)_$(PROMPT) | tr ':/.' '_')
RUNS ?= 10
WARMUP ?= 2
ENERGY_SOURCE ?= perf           # perf | csv | none
ENERGY_CSV ?=                   # set when ENERGY_SOURCE=csv

# Full pipeline for the "inefficient_sort" task
full-sort:
	python -m harness.generate --task-id inefficient_sort --prompt $(PROMPT) --model $(MODEL) --with-codecarbon
	python -m harness.run --task-id inefficient_sort --impl tasks.generated.inefficient_sort.AUTO_PICK \
		--variant $(VARIANT) --runs $(RUNS) --warmup $(WARMUP) --energy-source $(ENERGY_SOURCE) \
		$$( test "$(ENERGY_SOURCE)" = "csv" && printf -- ' --energy-csv %s' "$(ENERGY_CSV)" || true )
	python analysis/compute_gc.py
	python analysis/stats.py

# Full pipeline for the "modular_example" task
full-mod:
	python -m harness.generate --task-id modular_example --prompt $(PROMPT) --model $(MODEL) --with-codecarbon
	python -m harness.run --task-id modular_example --impl tasks.generated.modular_example.AUTO_PICK \
		--variant $(VARIANT) --runs $(RUNS) --warmup $(WARMUP) --energy-source $(ENERGY_SOURCE) \
		$$( test "$(ENERGY_SOURCE)" = "csv" && printf -- ' --energy-csv %s' "$(ENERGY_CSV)" || true )
	python analysis/compute_gc.py
	python analysis/stats.py

full-unit:
	python -m harness.generate --task-id unit_test_gen --prompt $(PROMPT) --model $(MODEL) --with-codecarbon
	python -m harness.run --task-id unit_test_gen --impl tasks.generated.unit_test_gen.AUTO_PICK \
		--variant $(VARIANT) --runs $(RUNS) --warmup $(WARMUP) --energy-source $(ENERGY_SOURCE) \
		$$( test "$(ENERGY_SOURCE)" = "csv" && printf -- ' --energy-csv %s' "$(ENERGY_CSV)" || true )
	python analysis/compute_gc.py
	python analysis/stats.py