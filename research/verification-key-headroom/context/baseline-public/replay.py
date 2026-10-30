"""Guarded explicit complete replay, with retained external evidence."""
import json,sys
from pathlib import Path
import guard
if len(sys.argv)!=2:raise ValueError('Supply one external evidence directory')
package=Path(__file__).resolve().parent;output=Path(sys.argv[1]).resolve()
if output.is_relative_to(package):raise ValueError('Evidence stays outside the immutable package')
output.mkdir(parents=True,exist_ok=True)
guard.SOURCE=package;guard.HERE=output
guard.CLOSURE=tuple(sorted(str(p.relative_to(package)) for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts))+('/usr/lib/python3.12/fractions.py',)
with (output/'execution.lock').open('a') as lock:
    guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
    guard.run('complete-native','replay_driver.py')
