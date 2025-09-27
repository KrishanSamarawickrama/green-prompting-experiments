# Experiment Manifest

## Hardware
- CPU: Intel Core i5-7200U
- GPU: NVIDIA GeForce 940MX (2GB DDR3)
- RAM: 16 GB
- Disk: 128 GB SSD
- Smart Plug: <Model / App / Export method>

## Software
- OS: Xubuntu 22.04 LTS
- Kernel: (output of `uname -r`)
- Python: (e.g., 3.12.x)
- perf: (output of `perf --version`)
- NVIDIA Driver: (output of `nvidia-smi`)

## Notes
- Background services disabled: indexers, updates, cloud sync.
- Fixed input seeds used across runs.
- Model + tokenizer hashes recorded in generation metadata.
