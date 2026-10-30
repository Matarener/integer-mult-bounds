"""Optional single guarded complete frozen-qualifier replay; no retry or benchmark fishing."""
import fcntl
from pathlib import Path
import sys
import guard

PACKAGE = Path(__file__).resolve().parent
if len(sys.argv) != 3 or sys.argv[1] not in ('B', 'C', 'D'):
    raise ValueError('replay.py B|C|D NEW_EXTERNAL_EVIDENCE_DIRECTORY')
evidence = Path(sys.argv[2]).resolve()
if evidence.is_relative_to(PACKAGE) or evidence.exists():
    raise ValueError('new evidence directory outside the immutable package required')
evidence.mkdir(parents=True)
guard.HERE = evidence
guard.SOURCE = PACKAGE
guard.CLOSURE = tuple(sorted(str(p.relative_to(PACKAGE)) for p in PACKAGE.rglob('*')
                             if p.is_file() and '__pycache__' not in p.parts)) + ('/usr/lib/python3.12/fractions.py',)
guard.AGGREGATE = 600
with (evidence / 'execution.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    script = 'owned_screen.py' if sys.argv[1] == 'D' else 'full_' + sys.argv[1] + '.py'
    guard.run('complete-' + sys.argv[1], script)
