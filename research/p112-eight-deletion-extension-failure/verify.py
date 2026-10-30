#!/usr/bin/env python3
"""Certify eight-deletion failures of global quadratic extension on P112."""

from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
GEOMETRY = 'research/complex-rank8-rigidity-p105/verify.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_geometry():
    rows = json.loads((ROOT/'SOURCES.json').read_text())['files']
    pin = next(r for r in rows if r['path'] == GEOMETRY)
    need(hashlib.sha256((REPO/GEOMETRY).read_bytes()).hexdigest() == pin['sha256'], 'geometry source hash')
    spec = importlib.util.spec_from_file_location('p105_source', REPO/GEOMETRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rank_q(rows):
    """Exact rank over Q by Gaussian elimination on Fractions."""
    rows = [[Fraction(x) for x in r] for r in rows]
    rank = 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((i for i in range(rank, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][c]:
                f = rows[i][c]/rows[rank][c]
                rows[i] = [a-f*b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def quadratic_forms():
    """Rational basis of the 35 trace-zero symmetric 8x8 matrices."""
    forms = []
    for i, j in itertools.combinations(range(8), 2):
        h = [[0]*8 for _ in range(8)]
        h[i][j] = h[j][i] = 1
        forms.append(h)
    for i in range(7):
        h = [[0]*8 for _ in range(8)]
        h[i][i], h[7][7] = 1, -1
        forms.append(h)
    return forms


def evaluations(s, lines):
    forms = quadratic_forms()
    return [[sum(h[a][b]*s.LINES[i][a]*s.LINES[i][b] for a in range(8) for b in range(8)) for i in lines]
            for h in forms]


def live_frames(s, deleted):
    dead = s.F0MASK | sum(1 << i for i in deleted)
    return [F for F, m in zip(s.FRAMES, s.FMASK) if not m & dead]


def certify(s, X):
    """Return the exact kernel data of the live-frame incidence after deleting X."""
    L = [i for i in s.P112 if i not in X]
    frames = live_frames(s, X)
    covered = {i for F in frames for i in F}
    isolated = [i for i in L if i not in covered]
    incidence_rank = rank_q([[int(i in F) for i in L] for F in frames])
    kernel = len(L)-incidence_rank
    # Quadratic restrictions to L span 35 dimensions and lie in the kernel.
    need(rank_q(evaluations(s, L)) == 35, 'quadratic restriction dimension on L')
    # Kernel vectors explained by quadratics plus indicator vectors of isolated lines.
    units = [[int(i == j) for i in L] for j in isolated]
    explained = rank_q(evaluations(s, L)+units)
    need(explained <= kernel, 'isolated indicators and quadratics lie in the kernel')
    return {'deleted': sorted(X), 'live_lines': len(L), 'live_frames': len(frames),
            'isolated_lines': isolated, 'rank_q': incidence_rank, 'kernel_dimension': kernel,
            'excess_over_quadratics': kernel-35,
            'quadratics_plus_isolated_indicators': explained}


def main():
    s = load_geometry()
    need(len(s.LINES) == 120 and len(s.FRAMES) == 2025 and len(s.P112) == 112, 'E8 line/frame geometry')
    live = live_frames(s, [])
    need(len(live) == 1260, 'live frames avoiding FRAME0')
    need(Counter(i for F in live for i in F) == Counter({i: 90 for i in s.P112}), 'ninety live frames per line')

    heavy = {}
    for line in s.P112:
        through = [F for F in live if line in F]
        partners = Counter(i for F in through for i in F if i != line)
        need(Counter(partners.values()) == Counter({10: 51, 15: 8}), 'partner frame counts')
        X = tuple(sorted(i for i in partners if partners[i] == 15))
        need(all(set(F) & set(X) for F in through), 'heavy partners hit every live frame through the line')
        heavy[line] = X
    families = sorted(set(heavy.values()))
    need(len(families) == 14, 'fourteen distinct heavy-partner octets')
    need(all(sum(v == X for v in heavy.values()) == 8 for X in families), 'each octet isolates eight lines')

    certificates = [certify(s, X) for X in families]
    for c in certificates:
        need(sorted(c['isolated_lines']) == sorted(l for l, X in heavy.items() if list(X) == c['deleted']),
             'isolated lines are exactly the lines owning this octet')
        need(tuple(c['isolated_lines']) in families, 'isolated lines form the partner octet')
        need((c['live_lines'], c['live_frames'], c['rank_q'], c['kernel_dimension']) == (104, 648, 62, 42),
             'exact octet incidence data')
        need(c['quadratics_plus_isolated_indicators'] == c['kernel_dimension'], 'kernel fully explained')
        need(c['excess_over_quadratics'] > 0, 'extension fails')
    excess = Counter(c['excess_over_quadratics'] for c in certificates)

    # Controls: every seven-subset of the first octet keeps all lines covered and has
    # the #5697 rank |L|-35; a damaged octet does not isolate its line.
    X = families[0]
    for drop in X:
        Y = [i for i in X if i != drop]
        frames = live_frames(s, Y)
        L = [i for i in s.P112 if i not in Y]
        need({i for F in frames for i in F} == set(L), 'seven deletions isolate nothing')
        need(rank_q([[int(i in F) for i in L] for F in frames]) == len(L)-35, 'seven-deletion control rank')
    owner = next(l for l, Y in heavy.items() if Y == X)
    damaged = list(X[1:])+[next(i for i in s.P112 if i not in X and i != owner)]
    need(any(owner in F for F in live_frames(s, damaged)), 'damaged octet control')

    result = {'status': 'PASS_P112_EIGHT_DELETION_EXTENSION_FAILURE',
              'octets': len(families), 'excess_histogram': dict(sorted(excess.items())),
              'certificates': certificates, 'seven_subset_controls': len(X)}
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
