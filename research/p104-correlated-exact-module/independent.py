"""Separate residue and coefficient proof checks. Apache-2.0.

No primary arithmetic, receipt, wrapper parser or executable is imported.
"""

import gzip
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def residue_check():
    accepted = 0
    for ar, ai, br, bi in itertools.product(range(8), repeat=4):
        integral_entry = all(z % 4 == 0 for z in (ar, ai, br, bi))
        numerators = (ar + br - ai + bi, ai + bi + ar - br,
                      ar + br + ai - bi, ai + bi - ar + br)
        exact = integral_entry and all(z % 8 == 0 for z in numerators)
        congruence = integral_entry and ((ar + ai - br - bi) // 4) % 2 == 0
        require(exact == congruence, 'pair criterion on complete modulo-eight domain')
        if exact:
            a, b, c, d = ar // 4, ai // 4, br // 4, bi // 4
            dr, di = a - c, b - d
            sr, si = c + dr // 2, d + di // 2
            low = sr - (-di) // 2, si - dr // 2
            literal = low[0] - di, low[1] + dr, low[0], low[1]
            require(literal == tuple(z // 8 for z in numerators),
                    'literal floors on every admitted residue')
            accepted += 1
    require(accepted == 8, 'admitted residue count')
    return accepted


def coefficient_check():
    extra = Counter()
    for subset in itertools.product((0, 1), repeat=9):
        degree = sum(subset)
        exponent = max(degree, 4 + subset[0])
        extra[exponent - degree] += 1
        # An integral Boolean difference has the same coefficient divisibility
        # as its values, since its evaluation matrix is integer unimodular.
        require(exponent >= 4 and (not subset[0] or exponent >= 5),
                'all value and first-difference congruences')
        if exponent > degree:
            require(exponent - 1 < 4 or (subset[0] and exponent - 1 < 5),
                    'lowered coefficient violates a required congruence')
    require(dict(extra) == {4: 2, 3: 16, 2: 56, 1: 112, 0: 326}, 'coefficient histogram')
    require(sum(k * count for k, count in extra.items()) == 280, 'index exponent')
    return dict(extra)


def source_check():
    root = Path(__file__).resolve().parents[1] / 'p104-rounded-collector/inputs'
    sources = [
        ('WORD.json', 'cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50'),
        ('NATIVE.json.gz',
         'ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d')]
    decoded = []
    for name, expected in sources:
        p = root / name
        require(p.is_file() and not p.is_symlink(), 'regular independent input')
        with p.open('rb') as handle:
            raw = handle.read(4 * 1024 * 1024 + 1)
        require(len(raw) <= 4 * 1024 * 1024, 'independent source capacity')
        require(hashlib.sha256(raw).hexdigest() == expected, 'independent input hash')
        raw = gzip.decompress(raw) if name.endswith('.gz') else raw
        require(len(raw) <= 16 * 1024 * 1024, 'independent expansion capacity')
        decoded.append(json.loads(raw))
    word, native = decoded
    records = [r for r in native['transports'] if 1092 in r['events']]
    require(len(records) == 1, 'unique independent window recipe')
    r = records[0]
    require(word['program'][1092] == ['transport', 'D31', r['old'], r['new'], 1]
            and r['recipe']['rank'] == 1, 'independent rank-one binding')
    require(word['program'][1090] == ['add', 'D31', 'Y27', '1/4', r['old']]
            and word['program'][1129] == ['add', 'D31', 'Y26', '1/4', r['new']],
            'independent source-read binding')
    # A forward dependency calculation, separate from the backward primary.
    origin = {name: {name} for name in word['initial_frames']}
    histories = {name: set() for name in origin}
    for i, row in enumerate(word['program'][:2025]):
        target = row[1]
        histories[target].add(i)
        if row[0] == 'add':
            origin[target] |= origin[row[2]]
            histories[target] |= histories[row[2]]
    targets = ['D31', 'D30', 'D29', 'D28', 'D27', 'Q7']
    events = set().union(*(histories[name] for name in targets))
    dependencies = set().union(*(origin[name] for name in targets))
    require(len(events) == 257 and len(dependencies) == 58, 'forward dependency closure')
    active_reads = [i for i in sorted(events) if word['program'][i][0] == 'add'
                    and word['program'][i][2] in ('Y27', 'Y26')]
    require(active_reads == [1090, 1129], 'exact in-cone readers')
    require(any(row[0] == 'add' and row[2] in ('Y27', 'Y26')
                for i, row in enumerate(word['program'][:2025]) if i not in events),
            'noncone obligations really remain')
    return len(events)


def main():
    count = source_check()
    residues = residue_check()
    coefficient_check()
    print(f'PASS_P104_MODULE_SEPARATE residues=4096 accepted={residues} cone={count}')


if __name__ == '__main__':
    main()
