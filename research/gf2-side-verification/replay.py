"""One cold complete side replay, bounded and serial; no automatic repetition."""
import fcntl
import os
from pathlib import Path
import sys
import guard

PACKAGE = Path(__file__).resolve().parent
if len(sys.argv) != 3 or sys.argv[1] not in ('B', 'C'):
    raise ValueError('replay.py B|C NEW_EXTERNAL_EVIDENCE_DIRECTORY')
evidence = Path(sys.argv[2]).resolve()
if evidence.exists() or evidence.is_relative_to(PACKAGE):
    raise ValueError('new evidence directory outside the immutable package required')
evidence.mkdir(parents=True)
os.environ['CROC_GF2_SIDE_OUTPUT'] = str(evidence / 'scientific')
guard.HERE = evidence
guard.SOURCE = PACKAGE
guard.CLOSURE = tuple(sorted(str(p.relative_to(PACKAGE)) for p in PACKAGE.rglob('*')
                             if p.is_file() and '__pycache__' not in p.parts))
guard.AGGREGATE = 600
with (evidence / 'execution.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    guard.run('complete-' + sys.argv[1], 'full_' + sys.argv[1] + '.py')
