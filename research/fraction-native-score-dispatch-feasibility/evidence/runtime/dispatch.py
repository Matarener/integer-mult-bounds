import sys
import guard
guard.SOURCE=guard.HERE.parent/'feasibility'
guard.CLOSURE=tuple(sorted(str(p.relative_to(guard.SOURCE)) for p in guard.SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts))+('/usr/lib/python3.12/fractions.py',)
label=sys.argv[1]
with (guard.HERE/'execution.lock').open('a') as lock:
    guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
    guard.run(label,'micro.py',optimized=label.endswith('-O'))
