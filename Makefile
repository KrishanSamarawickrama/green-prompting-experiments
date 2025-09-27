.PHONY: init test analyse ollama-pull gen-sort-baseline gen-mod-baseline measure-sort-human measure-mod-human

init:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

test:
	PYTHONPATH=. pytest -q

analyse:
	python analysis/compute_gc.py

ollama-pull:
	python3 tools/ollama_pull.py

gen-sort-baseline:
	python harness/generate.py --task-id inefficient_sort --prompt baseline

gen-mod-baseline:
	python harness/generate.py --task-id modular_example --prompt baseline

measure-sort-human:
	python harness/run.py --task-id inefficient_sort --impl tasks.reference.inefficient_sort_human --variant baseline --runs $${RUNS} --energy $${ENERGY} --energy-total

measure-mod-human:
	python harness/run.py --task-id modular_example --impl tasks.reference.modular_example_human --variant baseline --runs $${RUNS} --energy $${ENERGY} --energy-total
