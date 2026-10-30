#!/usr/bin/env python3
"""Check all owned-holder cuts in two pinned P104 words.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Word construction: GamingPuzzled, DreamingOfClouds, thu-nmrc and the P104
predecessors listed in README.md. No source interpreter is imported.
"""
import bisect
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in out}
    return out


def member(v, basis):
    pivots = {}
    for x in basis:
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    while v:
        k = v.bit_length() - 1
        if k not in pivots:
            return False
        v ^= pivots[k]
    return True


def timelines(w):
    n = w['public']
    cur = list(w['initial']) + [None] * 8
    out = [[] for _ in cur]
    owned = set()
    for i, e in enumerate(w['program']):
        op, r = e[:2]
        if op == 'MOVE':
            need(cur[r] == e[2] and (r in owned) == e[4], 'MOVE entry')
            a, b = map(lambda f: span(w['frames'][f]), e[2:4])
            need(b < a if r in owned else a < b, 'MOVE direction')
            cur[r] = e[3]
            continue
        if op == 'INIT':
            need(r >= n and r not in owned, 'INIT role')
            owned.add(r)
            cur[r] = e[2]
        regs = (r, e[2]) if op in ('ADD', 'COPY') else (r,)
        frame = e[2] if op in ('INIT', 'CLEAR') else e[-1]
        need(all(cur[j] == frame for j in regs), 'Scalar frames')
        for j in regs:
            out[j].append((i, frame))
        if op == 'CLEAR':
            need(r in owned, 'CLEAR role')
            owned.remove(r)
            cur[r] = None
    need(not owned and cur[:n] == w['final'], 'Final frames')
    return out


def row_stream(w, dyadic=False):
    """Use sparse fractions or integer rows with one binary denominator."""
    n = w['public']
    rows = [{r: 1} for r in range(n)] + [{} for _ in range(8)]
    powers = [0] * len(rows)
    for i, e in enumerate(w['program']):
        op, r = e[:2]
        old = set(rows[r])
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
            powers[r] = 0
        elif op != 'MOVE':
            q = Q(e[-2])
            if dyadic:
                k = q.denominator.bit_length() - 1
                need(q.denominator == 1 << k, 'Dyadic input')
                s = r if op == 'SCALE' else e[2]
                new = {x: q.numerator * a for x, a in rows[s].items()}
                power = powers[s] + k
                if op == 'ADD':
                    level = max(power, powers[r])
                    new = {x: a << (level - power) for x, a in new.items()}
                    for x, a in rows[r].items():
                        new[x] = new.get(x, 0) + (a << (level - powers[r]))
                    power = level
                rows[r] = {x: a for x, a in new.items() if a}
                powers[r] = power
                while powers[r] and not any(a & 1 for a in rows[r].values()):
                    rows[r] = {x: a // 2 for x, a in rows[r].items()}
                    powers[r] -= 1
            else:
                if op == 'SCALE':
                    rows[r] = {x: q * a for x, a in rows[r].items()}
                elif op == 'COPY':
                    need(not rows[r], 'Empty COPY destination')
                    rows[r] = {x: q * a for x, a in rows[e[2]].items()}
                else:
                    need(op == 'ADD', 'Opcode')
                    new = dict(rows[r])
                    for x, a in rows[e[2]].items():
                        new[x] = new.get(x, 0) + q * a
                    rows[r] = {x: a for x, a in new.items() if a}
        touched = old | set(rows[r]) | {r}
        if op in ('ADD', 'COPY'):
            touched |= set(rows[e[2]]) | {e[2]}
        yield i, rows, touched
    live = set(w['live'])
    for r, row in enumerate(rows):
        unit = (1 << powers[r]) if dyadic else 1
        want = {r: unit} if r < n else {}
        if r - 112 in live:
            want[r - 112] = unit
        need(row == want, 'Exact final scalar rows')


def audit(w, supplied=None, dyadic=False):
    n = w['public']
    main = set(w['live']) | {r + 112 for r in w['live']}
    helpers = set(range(n)) - main
    need(len(helpers) == 527, 'Helper domain')
    tl = timelines(w)
    ix = [[i for i, _ in t] for t in tl]
    frames = w['frames']
    masks = [sum(1 << v for v in span(b)) for b in frames]
    records, states = [], set()
    touched_points = 0
    witnesses = {} if supplied is None else {(r[0], r[1]): r for r in supplied}
    if supplied is not None:
        need(len(witnesses) == len(supplied), 'Unique certificate keys')
    for i, rows, touched in row_stream(w, dyadic):
        candidates = set().union(*(rows[j] for j in range(n, n + 8))) & helpers
        for h in sorted(candidates):
            holders = [j for j in range(n) if h in rows[j] or j == h]
            bounds = []
            for j in holders:
                k = bisect.bisect_right(ix[j], i)
                a = tl[j][k - 1][1] if k else w['initial'][j]
                b = tl[j][k][1] if k < len(tl[j]) else w['final'][j]
                bounds.append((j, a, b))
            states.add((h, tuple(bounds)))
            touched_points += w['program'][i][0] != 'MOVE' and h in touched
            if supplied is None:
                rec = next(([i, h, j, a, k, b, v]
                            for j, a, _ in bounds for k, _, b in bounds
                            for v in frames[a] if not (masks[b] >> v & 1)), None)
                need(rec is not None, 'No public separator at cut ' + str((i, h)))
            else:
                need((i, h) in witnesses, 'Missing cut')
                rec = witnesses.pop((i, h))
                _, _, j, a, k, b, v = rec
                anchor = {r: (aa, bb) for r, aa, bb in bounds}
                need(j in anchor and k in anchor, 'Public holder witness')
                need(anchor[j][0] == a and anchor[k][1] == b, 'Exact scalar anchors')
                need(member(v, frames[a]) and not member(v, frames[b]), 'Separator')
            records.append(rec)
    if supplied is not None:
        need(not witnesses, 'Extra cuts')
    return records, {'events': len(w['program']), 'helpers': len(helpers),
                     'owned_holder_cuts': len(records), 'touched_cuts': touched_points,
                     'distinct_public_anchor_states': len(states),
                     'public_separators': len(records)}


def reject(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('Control accepted: ' + label)


def main():
    results = {}
    for pin in json.loads((HERE / 'INPUTS.json').read_bytes()):
        raw = (HERE / pin['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source byte pin')
        w = json.loads(gzip.decompress(raw))
        records, summary = audit(w)
        checked, second = audit(w, records, dyadic=True)
        need(checked == records and second == summary, 'Independent arithmetic pass')
        summary['certificate_sha256'] = sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()
        need(summary['owned_holder_cuts'] == 5252 and summary['touched_cuts'] == 2832,
             'Complete coverage count')
        results[Path(pin['local_path']).name] = summary
        if pin['local_path'].endswith('pr5569-WORD.json.gz'):
            controls = [reject(lambda: audit(w, records[1:], True), 'missing cut')]
            for label, index, value in [('zero separator', 6, 0),
                                        ('wrong anchor', 3, -1),
                                        ('owned instead of public holder', 2, 735)]:
                bad = [r[:] for r in records]
                bad[0][index] = value
                controls.append(reject(lambda: audit(w, bad, True), label))
    # Nontrivial positive frame interval and two membership outcomes.
    low, middle, high = [1], [1, 2], [1, 2, 4]
    need(span(low) < span(middle) < span(high), 'Positive public interval')
    need(member(3, middle) and not member(4, middle), 'Membership controls')
    out = {'status': 'PASS_P104_OWNED_HOLDER_HANDOFFS', 'words': results,
           'rejected_controls': controls, 'new_kappa': None}
    expected = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        expected.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(out == json.loads(expected.read_bytes()), 'Exact result receipt')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
