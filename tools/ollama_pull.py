import yaml, subprocess, sys

with open('models/ollama/models.yaml', 'r', encoding='utf-8') as f:
    m = yaml.safe_load(f) or {}

for e in m.get('models', []):
    if e.get('pull'):
        name = e['name']
        print(f'Pulling {name} …', flush=True)
        subprocess.run(['ollama', 'pull', name], check=False)