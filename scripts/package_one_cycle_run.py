#!/usr/bin/env python3
"""Copy one completed Harbor trial plus analysis into the review package."""
import json
import os
import re
import shutil
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
run=int(sys.argv[1]); assert 1<=run<=5
suffix=sys.argv[2] if len(sys.argv)>2 else ''
label=f'run-{run:02d}'+(f'-{suffix}' if suffix else '')
source=root/'results/kimi-k3-one-cycle'/label
job=source/(f'k3-one-cycle-{run:02d}'+(f'-{suffix}' if suffix else ''))
result=json.loads((job/'result.json').read_text())
if result['stats']['n_running_trials'] or result['stats']['n_pending_trials']:
    raise ValueError('run is not complete')
dest_label=sys.argv[3] if len(sys.argv)>3 else f'run-{run:02d}'
if '..' in Path(dest_label).parts or Path(dest_label).is_absolute():
    raise ValueError('invalid destination label')
dest=root/'submission/trajectories/kimi-k3-max'/dest_label
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists(): raise FileExistsError(dest)
shutil.copytree(source,dest,ignore=shutil.ignore_patterns('launcher_pid.txt'))
analysis=root/f'results/one-cycle-analysis/run-{run:02d}/analysis-run-{run:02d}'
if (analysis/'analysis.json').exists():
    shutil.copytree(analysis,dest/'analysis')
secret_values=[os.environ.get(name,'').encode().strip() for name in ('OPENAI_API_KEY','DEEPSEEK_API_KEY')]
replacements=[(str(root).encode(),b'<workspace>')]
text_suffixes={'.json','.log','.txt','.pane','.cast','.csv','.md','.toml','.sha256','.sh','.py'}
count=0
for path in dest.rglob('*'):
    if not path.is_file(): continue
    data=path.read_bytes()
    if any(secret and secret in data for secret in secret_values): raise RuntimeError(f'secret found in {path}')
    if re.search(rb'sk-[A-Za-z0-9]{20,}',data): raise RuntimeError(f'key-like string found in {path}')
    if path.suffix in text_suffixes:
        for original,replacement in replacements: data=data.replace(original,replacement)
        data=re.sub(rb'/home/[^/\s"\\]+',b'<home>',data)
        data=re.sub(rb'/tmp/cyclic-harbor-venv',b'<harbor-env>',data)
        data=re.sub(rb'/tmp/terminal-bench-science',b'<tb-science-repo>',data)
        data=re.sub(rb'/root/\.local/share/uv/python',b'<python-runtime>',data)
        data=re.sub(rb'/tmp/tmp[a-zA-Z0-9_]+',b'<tempdir>',data)
        data=re.sub(rb'/tmp/harbor-analyze-[a-zA-Z0-9_]+',b'<analysis-tempdir>',data)
        if re.search(rb'/home/[^/\s"\\]+',data): raise RuntimeError(f'host path found in {path}')
        path.write_bytes(data)
    count+=1
print(dest, 'files',count)
