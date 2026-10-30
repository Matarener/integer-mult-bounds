import sys
import guard
guard.SOURCE=guard.HERE.parent/'feasibility'
guard.CLOSURE=tuple(sorted(str(p.relative_to(guard.SOURCE)) for p in guard.SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts))+('/usr/lib/python3.12/fractions.py',)
guard.AGGREGATE=600
label=sys.argv[1]
if label.endswith('-debug'):
    guard.os.environ.update(PYTHONMALLOC='debug',PYTHONDEVMODE='1')
script='finite.py' if label.startswith('finite') else 'micro.py' if label.startswith('micro') else 'actual_audit.py'
if label.startswith('apply-micro'):script='micro_apply.py'
if label.startswith('full-'):script='full_C.py'
with (guard.HERE/'execution.lock').open('a') as lock:
    guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
    guard.run(label,script,optimized=label.endswith('-O'))
