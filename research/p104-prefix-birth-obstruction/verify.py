#!/usr/bin/env python3
"""Exact new boundary fixtures; no predecessor arithmetic replay. Stdlib only."""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from math import isqrt
from pathlib import Path
import platform

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
TOOLKIT = 'research/p104-designer-toolkit-v2/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(basis):
    require(len(basis) <= 9, 'basis dimension exceeds nine')
    result = frozenset({0})
    for value in basis:
        require(type(value) is int and 0 < value < 512, 'bad binary vector')
        require(value not in result, 'dependent basis')
        result = result | frozenset(x ^ value for x in result)
    return result


def plane_subspaces(plane):
    require(len(plane) == 4 and 0 in plane, 'intersection is not a plane')
    nonzero = sorted(plane - {0})
    candidates = []
    for mask in range(8):
        subset = frozenset({0} | {nonzero[i] for i in range(3) if mask >> i & 1})
        if all(a ^ b in subset for a in subset for b in subset):
            candidates.append(subset)
    require(len(candidates) == 5, 'wrong plane lattice')
    return candidates


def read_inputs():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    paths = []
    for entry in manifest['files']:
        if entry.get('usage') == 'input':
            name = entry['path']
            data = (ROOT / name).read_bytes()
            require(hashlib.sha256(data).hexdigest() == entry['sha256'], 'source hash: ' + name)
            paths.append(name)
    require(len(paths) == 3, 'wrong live input inventory')
    raw = (ROOT / (TOOLKIT + 'words/6030.json.gz')).read_bytes()
    require(len(raw) < 2_000_000, 'source container too large')
    word_data = gzip.decompress(raw)
    require(len(word_data) < 16_000_000, 'source word too large')
    word = json.loads(word_data)
    plan = json.loads((ROOT / (TOOLKIT + 'alignbuild/data/manifest_6030.json')).read_text())
    require(len(word['initial']) == word['public'] == 770, 'wrong public interface')
    require(len(word['frames']) <= 1200 and len(word['program']) < 26000, 'word bounds')
    require(len(plan['plan']) <= 32, 'manifest bound')
    return word, plan, paths


def market_rows(word, plan, frames):
    markets = [g for block in plan['plan'] if block['side'] == 'markets' for g in block['items']]
    require(len(markets) == len(set(markets)) == 14, 'wrong market inventory')
    main = set(word['live']) | {r + 112 for r in word['live']}
    rows = []
    all_roles = set()
    for market in markets:
        birth = frames[market]
        require(len(birth) == 32, 'market dimension')
        hub = frozenset(x for x in range(512) if all((x & g).bit_count() % 2 == 0 for g in birth))
        intersection = hub & birth
        require(len(hub) == 16 and len(intersection) == 4, 'hub/intersection dimension')
        roles = [r for r, f in enumerate(word['initial']) if f == market and r not in main]
        require(0 < len(roles) <= 8, 'market role bound')
        require(not all_roles.intersection(roles), 'duplicate market role')
        for role in roles:
            require(len(frames[word['final'][role]]) == 512, 'helper final is not full')
            moves = [e for e in word['program'] if e[0] == 'MOVE' and e[1] == role]
            require(moves and moves[0][2] == market, 'first original MOVE is not from G')
        all_roles.update(roles)
        rows.append((market, roles, intersection))
    require(len(all_roles) == 62, 'changed helper inventory')
    return rows


def splice(word, frames, market, role, lower):
    require(lower < frames[market], 'birth must be a strict subspace')
    require(word['initial'][role] == market, 'wrong source birth')
    require(all((x & g).bit_count() % 2 == 0 for x in lower for g in frames[market]),
            'lower birth is outside the associated hub')
    index = next((f for f, space in enumerate(frames) if space == lower), len(frames))
    initial = list(word['initial'])
    initial[role] = index
    program = [['MOVE', role, index, market]] + word['program']
    table = list(word['frames'])
    if index == len(table):
        basis = []
        covered = frozenset({0})
        for value in sorted(lower):
            if value not in covered:
                basis.append(value)
                covered = span(basis)
        require(covered == lower, 'new frame basis')
        table.append(basis)
    return dict(word, initial=initial, program=program, frames=table, lower=lower, index=index)


def check_splice(word, frames, market, role, edited):
    prefix = edited['program'][0]
    require(prefix == ['MOVE', role, edited['index'], market], 'missing or wrong paid ascent')
    require(edited['lower'] < frames[market], 'non-nested paid ascent')
    require(span(edited['frames'][edited['index']]) == edited['lower'], 'dangling frame')
    require(edited['final'] == word['final'], 'final boundary changed')
    require(edited['program'][1:] == word['program'], 'old suffix changed')
    current = list(edited['initial'])
    require(current[role] == edited['index'], 'wrong edited entry')
    current[role] = market  # MOVE transports a value unchanged; no row operation occurs.
    require(current == word['initial'], 'old entry boundary not restored')
    added = len(word['frames'][market]) - (len(edited['lower']).bit_length() - 1)
    old_span = len(word['frames'][word['final'][role]]) - len(word['frames'][market])
    require(old_span == 4 and added in (3, 4, 5), 'wrong changed ranks')
    return (old_span, added, old_span + added)


def sqrt_bounds(value):
    scale = 10**12
    floor = isqrt(value * scale * scale)
    return Fraction(floor, scale), Fraction(floor + 1, scale)


def power_controls():
    # Exact interval arithmetic at t=1/2 corroborates the written all-power proof.
    count = 0
    for added in (3, 4, 5):
        root_lo, root_hi = sqrt_bounds(added)
        total_lo, total_hi = sqrt_bounds(4 + added)
        require(2 + root_lo - total_hi > 0, 'preparation deficit not positive')
        require(total_lo - 2 > 0, 'paid-deletion escape control must gain')
        for mask in range(1 << (added - 1)):
            cuts = [0] + [i + 1 for i in range(added - 1) if mask >> i & 1] + [added]
            parts = [b - a for a, b in zip(cuts, cuts[1:])]
            require(sum(parts) == added, 'composition mass')
            # Equality for one jump; a strict lower enclosure suffices otherwise.
            if len(parts) > 1:
                require(sum(sqrt_bounds(x)[0] for x in parts) > root_hi, 'path bound')
            count += 1
    require(count == 28, 'composition inventory')
    return count


def rejection_controls(word, frames, row):
    market, roles, lower = row
    role = roles[0]
    good = splice(word, frames, market, role, lower)
    bad = []
    empty_prefix = dict(good, program=good['program'][1:])
    bad.append(lambda: check_splice(word, frames, market, role, empty_prefix))
    wrong_rank = dict(good, program=[['MOVE', role, good['index'], 0]] + word['program'])
    bad.append(lambda: check_splice(word, frames, market, role, wrong_rank))
    deleted = dict(good, program=good['program'][:-1])
    bad.append(lambda: check_splice(word, frames, market, role, deleted))
    wrong_entry = dict(good, initial=list(word['initial']))
    bad.append(lambda: check_splice(word, frames, market, role, wrong_entry))
    bad.append(lambda: splice(word, frames, market, role, frames[market]))
    bad.append(lambda: splice(word, frames, market, role, frozenset(range(512))))
    outside = next(x for x in frames[market] if x not in lower)
    bad.append(lambda: splice(word, frames, market, role, frozenset({0, outside})))
    for operation in bad:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError('rejection control accepted')
    return len(bad)


def main():
    word, plan, inputs = read_inputs()
    frames = [span(basis) for basis in word['frames']]
    rows = market_rows(word, plan, frames)
    counts = Counter()
    details = []
    for market, roles, intersection in rows:
        spaces = plane_subspaces(intersection)
        for role in roles:
            for lower in spaces:
                edited = splice(word, frames, market, role, lower)
                old, added, new = check_splice(word, frames, market, role, edited)
                counts[added] += 1
                require((old, new) == (4, 4 + added), 'changed target entry')
        details.append({'market': market, 'roles': roles, 'intersection': sorted(intersection)})
    require(dict(counts) == {5: 62, 4: 186, 3: 62}, 'new splice inventory')
    controls = rejection_controls(word, frames, rows[0])
    compositions = power_controls()
    files = sorted(PACKAGE.glob('*'))
    receipt = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
               for path in files if path.is_file()}
    receipt.update({name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs})
    result = {'schema': 'p104-birth-obstruction/1', 'markets': details,
              'splices': sum(counts.values()), 'added_rank_counts': dict(sorted(counts.items())),
              'compositions': compositions, 'rejections': controls, 'python': platform.python_version(),
              'minimum_loss': '18*(4^t+3^t-7^t), 0<t<1', 'sha256': receipt}
    print('PASS_P104_BIRTH_OBSTRUCTION splices=310 compositions=28 rejections=7 no_new_kappa')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
