#!/bin/bash
# Script to run all required make commands for green-prompting-experiments
set -e

# full-sort
make full-sort MODEL=deepseek-coder:6.7b PROMPT=baseline
make full-sort MODEL=deepseek-coder:6.7b PROMPT=cot_then_optimize
make full-sort MODEL=deepseek-coder:6.7b PROMPT=eff_from_scratch
make full-sort MODEL=deepseek-coder:6.7b PROMPT=tagged_explained
make full-sort MODEL=qwen2.5-coder:7b PROMPT=baseline
make full-sort MODEL=qwen2.5-coder:7b PROMPT=cot_then_optimize
make full-sort MODEL=qwen2.5-coder:7b PROMPT=eff_from_scratch
make full-sort MODEL=qwen2.5-coder:7b PROMPT=tagged_explained

# full-mod
make full-mod MODEL=deepseek-coder:6.7b PROMPT=baseline
make full-mod MODEL=deepseek-coder:6.7b PROMPT=cot_then_optimize
make full-mod MODEL=deepseek-coder:6.7b PROMPT=eff_from_scratch
make full-mod MODEL=deepseek-coder:6.7b PROMPT=tagged_explained
make full-mod MODEL=qwen2.5-coder:7b PROMPT=baseline
make full-mod MODEL=qwen2.5-coder:7b PROMPT=cot_then_optimize
make full-mod MODEL=qwen2.5-coder:7b PROMPT=eff_from_scratch
make full-mod MODEL=qwen2.5-coder:7b PROMPT=tagged_explained

# full-unit
make full-unit MODEL=deepseek-coder:6.7b PROMPT=baseline
make full-unit MODEL=deepseek-coder:6.7b PROMPT=cot_then_optimize
make full-unit MODEL=deepseek-coder:6.7b PROMPT=eff_from_scratch
make full-unit MODEL=deepseek-coder:6.7b PROMPT=tagged_explained
make full-unit MODEL=qwen2.5-coder:7b PROMPT=baseline
make full-unit MODEL=qwen2.5-coder:7b PROMPT=cot_then_optimize
make full-unit MODEL=qwen2.5-coder:7b PROMPT=eff_from_scratch
make full-unit MODEL=qwen2.5-coder:7b PROMPT=tagged_explained

# full-cacheexp
make full-cacheexp MODEL=deepseek-coder:6.7b PROMPT=baseline
make full-cacheexp MODEL=deepseek-coder:6.7b PROMPT=cot_then_optimize
make full-cacheexp MODEL=deepseek-coder:6.7b PROMPT=eff_from_scratch
make full-cacheexp MODEL=deepseek-coder:6.7b PROMPT=tagged_explained
make full-cacheexp MODEL=qwen2.5-coder:7b PROMPT=baseline
make full-cacheexp MODEL=qwen2.5-coder:7b PROMPT=cot_then_optimize
make full-cacheexp MODEL=qwen2.5-coder:7b PROMPT=eff_from_scratch
make full-cacheexp MODEL=qwen2.5-coder:7b PROMPT=tagged_explained

# full-jsonnorm
make full-jsonnorm MODEL=deepseek-coder:6.7b PROMPT=baseline
make full-jsonnorm MODEL=deepseek-coder:6.7b PROMPT=cot_then_optimize
make full-jsonnorm MODEL=deepseek-coder:6.7b PROMPT=eff_from_scratch
make full-jsonnorm MODEL=deepseek-coder:6.7b PROMPT=tagged_explained
make full-jsonnorm MODEL=qwen2.5-coder:7b PROMPT=baseline
make full-jsonnorm MODEL=qwen2.5-coder:7b PROMPT=cot_then_optimize
make full-jsonnorm MODEL=qwen2.5-coder:7b PROMPT=eff_from_scratch
make full-jsonnorm MODEL=qwen2.5-coder:7b PROMPT=tagged_explained

# full-log
make full-log MODEL=deepseek-coder:6.7b PROMPT=baseline
make full-log MODEL=deepseek-coder:6.7b PROMPT=cot_then_optimize
make full-log MODEL=deepseek-coder:6.7b PROMPT=eff_from_scratch
make full-log MODEL=deepseek-coder:6.7b PROMPT=tagged_explained
make full-log MODEL=qwen2.5-coder:7b PROMPT=baseline
make full-log MODEL=qwen2.5-coder:7b PROMPT=cot_then_optimize
make full-log MODEL=qwen2.5-coder:7b PROMPT=eff_from_scratch
make full-log MODEL=qwen2.5-coder:7b PROMPT=tagged_explained

# llmcarbon
make llmcarbon GRID=340 PUE=1.0 EMB=300
