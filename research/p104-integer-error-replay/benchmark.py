#!/usr/bin/env python3
"""Measure complete baseline and candidate runs in six serial fresh processes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

P=Path(__file__).resolve().parent


def measure():
    rows=[]
    order=['baseline','candidate','candidate','baseline','baseline','candidate']
    for mode in order:
        start=time.perf_counter()
        run=subprocess.run([sys.executable,'-I','-B',str(P/'verify.py'),'--'+mode],cwd=P.parent.parent,capture_output=True,text=True,check=True,timeout=120)
        elapsed=time.perf_counter()-start
        payload=json.loads(run.stdout.splitlines()[-1])
        rows.append(dict(mode=mode,wall_seconds=elapsed,internal_seconds=payload['seconds'],receipt=payload['receipt']))
        print(f'{mode}: {elapsed:.3f} seconds',file=sys.stderr,flush=True)
    if len({json.dumps(row['receipt'],sort_keys=True) for row in rows})!=1:raise ValueError('benchmark coverage differs')
    baseline=statistics.median(r['wall_seconds'] for r in rows if r['mode']=='baseline')
    candidate=statistics.median(r['wall_seconds'] for r in rows if r['mode']=='candidate')
    files=['integer.py','contract.py','verify.py','benchmark.py','inputs/source.tar']
    return dict(platform=platform.platform(),python=sys.version,code_sha256={f:sha256((P/f).read_bytes()).hexdigest() for f in files},order=order,runs=rows,
        baseline_median_seconds=baseline,candidate_median_seconds=candidate,speedup=baseline/candidate,wall_reduction_fraction=1-candidate/baseline,
        cold_processes=True,parallel_replays=False,scope='Complete contract with source authentication, extraction, all original endpoint/error/guard/control checks. Local shared-host timings; no Linux or hosted speed claim. Qualification is a separate cost.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();text=json.dumps(measure(),indent=2)+'\n'
    if args.output:args.output.write_text(text)
    else:print(text,end='')
