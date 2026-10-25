#!/usr/bin/env python3
"""Prove the active checks reject semantic drift, without receipt comparison.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    source = Path(__file__).with_name('verify.py').read_text()
    cases = [
        ('forget width-dependent global phase',
         'Q(0, 1)**(phase*f)', 'Q(0, 1)**phase', 'actual phase lift'),
        ('make the odd algebra commute',
         'Q((-1)**f)', 'Q(1)', 'phase twist'),
        ('reuse smaller-alphabet projector',
         'scale(Q(F(1, 4)), mul(add(ident, p), add(ident, c)))',
         'scale(Q(F(1, 2)), add(ident, p))', 'odd-width false character control'),
        ('reverse the b coefficient in the literal target',
         'scale(b, x)), f)', 'scale(-b, x)), f)', 'Kronecker vs Hamming expansion'),
        ('weaken the invertibility boundary',
         'bool(a*b*(a*a-b*b))', 'bool(a*b)', 'invalid target admitted'),
        ('forget that one target was cached',
         'per*(q-1)', 'per*q', 'cached observation control'),
    ]
    receipts = []
    with tempfile.TemporaryDirectory(prefix='pauli-history-mutations-') as tmp:
        for index, (name, old, new, expected) in enumerate(cases):
            if source.count(old) != 1:
                raise RuntimeError('ambiguous mutation anchor: '+name)
            script = Path(tmp)/('case_'+str(index)+'.py')
            script.write_text(source.replace(old, new))
            # --emit bypasses committed RESULT comparison: an active semantic
            # check must reject the change, including under optimized Python.
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(script), '--emit'],
                                 capture_output=True, text=True, timeout=20)
            if run.returncode == 0 or expected not in run.stderr:
                raise RuntimeError('mutation escaped intended predicate: '+name+' '+run.stderr)
            receipts.append({'mutation': name, 'rejection': expected})
    print(json.dumps({'status': 'PASS_PAULI_HISTORY_SEMANTIC_MUTATIONS',
                      'optimized_semantic_rejections': receipts}, indent=2))


if __name__ == '__main__':
    main()
