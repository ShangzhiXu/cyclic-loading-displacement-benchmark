#!/usr/bin/env python3
"""Finish the three remaining K3 runs strictly one at a time."""
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root=Path(__file__).resolve().parents[1]
base=root/'results/kimi-k3-one-cycle'
log_path=base/'serial_schedule.jsonl'

def log(event,**kwargs):
    item={'time_utc':datetime.now(timezone.utc).isoformat(),'event':event,**kwargs}
    with log_path.open('a') as f:f.write(json.dumps(item)+'\n')
    print(json.dumps(item),flush=True)

def alive(pid):
    p=Path(f'/proc/{pid}/stat')
    if not p.exists():return False
    try:return p.read_text().split(') ')[1][0]!='Z'
    except (OSError,IndexError):return False

def scored(run):
    p=base/f'watchdog-{run:02d}.jsonl'
    if not p.exists():return None
    for line in reversed(p.read_text().splitlines()):
        try:x=json.loads(line)
        except ValueError:continue
        if x.get('event')=='scored':return x
    return None

def start_watchdog(run):
    out=base/f'watchdog-{run:02d}.log'
    with out.open('ab') as f:
        proc=subprocess.Popen(['python3',str(root/'scripts/watch_one_cycle_k3.py'),str(run)],
                              cwd=root,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,
                              start_new_session=True,close_fds=True)
    (base/f'watchdog-{run:02d}.pid').write_text(str(proc.pid)+'\n')
    log('watchdog_started',run=run,pid=proc.pid)

for run in (1,2,3):
    log('run_waiting',run=run)
    while True:
        result=scored(run)
        if result:
            log('run_scored',run=run,attempt=result.get('attempt'),reward=result.get('reward'))
            break
        pid_path=base/f'watchdog-{run:02d}.pid'
        pid=int(pid_path.read_text()) if pid_path.exists() else -1
        if not alive(pid):
            start_watchdog(run)
        time.sleep(20)
log('all_three_scored')
