"""One parent-owned guarded command; no retries, immutable stage inputs."""
import argparse,fcntl,json,sys
from pathlib import Path
import guard
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('script');p.add_argument('--optimized',action='store_true');p.add_argument('--initial',action='store_true');a=p.parse_args()
script=(ROOT/a.script).resolve()
if not script.is_relative_to(ROOT/'stages') or not script.is_file():raise ValueError('Frozen stage script required')
stage=next(x for x in script.parents if x.parent==ROOT/'stages')
guard.HERE=ROOT/'runtime';guard.HERE.mkdir(exist_ok=True);guard.SOURCE=ROOT
# Static source closure includes every stage byte and unchanged baseline. Reports/evidence are excluded.
guard.CLOSURE=tuple(sorted(str(x.relative_to(ROOT)) for d in (stage,ROOT/'baseline',ROOT/'baseline-public',ROOT/'inputs') for x in d.rglob('*') if x.is_file() and '__pycache__' not in x.parts))+('guard.py','run_guarded.py','PLAN.json','/usr/lib/python3.12/fractions.py')
guard.AGGREGATE=1500
spent=sum(json.loads(x.read_text())['wall_seconds'] for x in (guard.HERE/'runs').glob('*/receipt.json'))
if a.initial and spent>=600:raise ValueError('Initial aggregate feasibility budget consumed')
if a.initial:guard.TIMEOUT=min(180,600-spent)
with (guard.HERE/'execution.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 guard.run(a.label,str(script.relative_to(ROOT)),a.optimized)
