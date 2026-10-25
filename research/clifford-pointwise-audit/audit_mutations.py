#!/usr/bin/env python3
"""Reject six actual changes to the standalone independent checker.

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(__file__).with_name('verify_symplectic.py').read_text()
mutations = [
    ('accept-all-matrices',
     'if not symplectic(columns, n):', 'if False:', 'noninvertible-preserver'),
    ('drop-displacement-identity',
     'columns[j] ^ (1 << j) for j in range(m)', 'columns[j] for j in range(m)',
     'fixed-rank-disagreement'),
    ('count-zero-trace-lifts',
     'positive = sum(s != 0 for s in sums)', 'positive = len(sums)',
     'wrong-nonzero-lift-count'),
    ('use-image-for-preimage',
     'values = {omega(x, w, n) for x in preimages[u]}',
     'values = {omega(u, w, n) for x in preimages[u]}',
     'residual-left-degenerate'),
    ('drop-first-overlap-half',
     'initial = Fraction(1, 1 << (s+1))', 'initial = Fraction(1, 1 << s)',
     'clifford-uniform-tail'),
    ('erase-central-phase',
     'roots = ((1, 0), (0, 1), (-1, 0), (0, -1))',
     'roots = ((1, 0), (1, 0), (1, 0), (1, 0))',
     'phase-fourier-orthogonality'),
]
out = []
with tempfile.TemporaryDirectory(prefix='independent-clifford-mutations-') as tmp:
    target = Path(tmp)/'verify.py'
    for name, old, new, diagnostic in mutations:
        if old not in source:
            raise RuntimeError('missing mutation site: '+name)
        target.write_text(source.replace(old, new))
        for optimized in (False, True):
            command = [sys.executable, '-I', '-W', 'error', '-B']
            if optimized:
                command.append('-O')
            command.append(str(target))
            run = subprocess.run(command, capture_output=True, text=True, timeout=120)
            if run.returncode == 0 or diagnostic not in run.stderr:
                raise RuntimeError('wrong mutation outcome: '+name+' '+run.stderr)
            out.append({'mutation': name, 'optimized': optimized,
                        'exit': run.returncode, 'diagnostic': diagnostic})
print(json.dumps(out, indent=2))
print('PASS_INDEPENDENT_SYMPLECTIC_MUTATIONS')
