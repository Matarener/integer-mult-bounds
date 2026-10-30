"""Test one extra row at the projected three-stage chronology gate.

This is a necessary-condition census, not a full endpoint search.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import itertools
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def run():
    spec = importlib.util.spec_from_file_location('checker', ROOT/'check.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    flags = [(a, c.add(a, c.eye(2))) for a in itertools.product(range(4), repeat=2)
             if c.mul(a, a) == a and c.rank(a) == 1]
    orders = sorted(set(itertools.permutations((0, 0, 1, 1, 2, 2))))
    hist = {'total': 0, 'has_one_extra_row': 0}
    examples = []
    start = time.monotonic()
    for fs in itertools.product(flags, repeat=3):
        for order in orders:
            seen, events = [0]*3, []
            for j in order:
                events.append((j, fs[j][seen[j]]))
                seen[j] += 1
            sums = {(j, k): (0, 0) for j in range(3) for k in range(3) if j != k}
            for i, (j, a) in enumerate(events):
                for k, b in events[i+1:]:
                    if j != k:
                        sums[j, k] = c.add(sums[j, k], c.mul(a, b))
            differences = [c.add(*[sums[j, k] for k in range(3) if k != j])
                           for j in range(3)]
            compatible = []
            for u, v in itertools.product(range(4), repeat=2):
                if all(all(row in (0, m) for row in mat)
                       for mat, m in zip(differences, (u ^ v, v, u))):
                    compatible.append((u, v))
            hist['total'] += 1
            if compatible:
                hist['has_one_extra_row'] += 1
                if len(examples) < 4:
                    examples.append({'flags': fs, 'order': order,
                                     'signatures': compatible[0], 'differences': differences})
    return {'counts': hist, 'examples': examples, 'seconds': round(time.monotonic()-start, 3),
            'scope': 'Necessary projected chronology only; not a full word'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
