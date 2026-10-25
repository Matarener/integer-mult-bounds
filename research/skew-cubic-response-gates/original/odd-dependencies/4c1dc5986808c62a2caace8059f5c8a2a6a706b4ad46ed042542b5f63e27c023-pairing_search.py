#!/usr/bin/env python3
"""Bounded rank-only proposal search over ADD-vertex path pairings.
Exact witnesses are admitted separately by circuit/phase edge replay.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from pathlib import Path
from functools import lru_cache
import argparse, hashlib, json, math, random, sys, time
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'pauli-caller-retiming'
PINS = {
    'trajectory_certificate.py': '677a342334e49befbfe069441325f3ac6008705c6697cff5c348905a67d92cbc',
    'inputs/REPAIRED-SIMPLIFIED.json': '4491cfe2a1f3e48510b33403b9b50c704865c3b1dc6d659ef5157840654e8fc3',
    'inputs/ADMITTED-TWO-SITE.json': '30d3f569d91304856118796f0c586176d0ad961eff70b09c78fce7532392101f',
}
for relative, digest in PINS.items():
    if hashlib.sha256((OLD / relative).read_bytes()).hexdigest() != digest:
        raise ValueError('frozen source pin: ' + relative)
sys.path.insert(0, str(OLD))
import trajectory_certificate as t


def lookup(op):
    columns = t.columns(op)
    chunks = (2 * op.n + 7) // 8
    out = []
    for k in range(chunks):
        A = columns[8*k:8*k+8]
        table = [0] * 256
        for value in range(1, 256):
            bit = value & -value
            index = bit.bit_length() - 1
            table[value] = table[value ^ bit] ^ (A[index] if index < len(A) else 0)
        out.append(table)
    return tuple(out)


def prepare(fixture):
    m, n = fixture['ambient_arity'], fixture['banks']
    prepared = []
    add_ordinals = []
    events = fixture.get('full_events', fixture['events'])
    for ordinal, e in enumerate(events):
        kind = e['kind']
        if kind == 'ADD':
            add_ordinals.append(ordinal)
            prepared.append(('A', e['dst'], e['src'], len(add_ordinals)-1))
        elif kind == 'BANK_SWAP':
            prepared.append(('S', *e['banks']))
        elif kind == 'SCALE':
            pass
        else:
            op, extra = t.unary(e, m)
            if op.tab != t.ce.identity(m):
                prepared.append(('G', e['bank'], lookup(op)))
    return m, n, prepared, add_ordinals


def evaluate(mask, m, n, events):
    states = [tuple(1 << (m+i) for i in range(m)) for _ in range(n)]
    chunks = (2*m+7)//8
    for e in events:
        if e[0] == 'A':
            if mask >> e[3] & 1:
                i, j = e[1:3]
                states[i], states[j] = states[j], states[i]
        elif e[0] == 'S':
            i, j = e[1:]
            states[i], states[j] = states[j], states[i]
        else:
            bank, tables = e[1:]
            if chunks == 3:
                a, b, c = tables
                states[bank] = tuple(a[x & 255] ^ b[(x >> 8) & 255] ^ c[x >> 16] for x in states[bank])
            elif chunks == 4:
                a, b, c, d = tables
                states[bank] = tuple(a[x & 255] ^ b[(x >> 8) & 255] ^ c[(x >> 16) & 255] ^ d[x >> 24] for x in states[bank])
            else:
                raise ValueError('proposal engine is bounded to the declared q2/q3 widths')
    low = (1 << m)-1
    ranks = [t.rank(x & low for x in state) for state in states]
    return sum(ranks), ranks


def search(fixture, seconds, seed, name):
    m, n, events, ordinals = prepare(fixture)
    width = len(ordinals)
    rng = random.Random(seed)
    trials = 0
    start = time.monotonic()
    bestmask = 0
    best, ranks = evaluate(0, m, n, events)
    history = [dict(trial=0, floor=best, ranks=ranks, mask=str(bestmask))]
    output = HERE / (name + '-Q' + str(fixture['q']) + '-PROPOSAL.json')

    def save():
        result = dict(status='RANK_ONLY_PAIRING_PROPOSAL', source_family=name, q=fixture['q'],
                      m=m, banks=n, goal=m*n, best_floor=best, mask=str(bestmask),
                      crossing_ADD_event_ordinals=[ordinal for i, ordinal in enumerate(ordinals) if bestmask >> i & 1],
                      ADD_event_ordinals=ordinals, trials=trials, seed=seed, history=history,
                      source_pins={str(OLD/r):h for r,h in PINS.items()},
                      producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      limits=['Search proposal only; not an exhaustive bound.', 'Exact edge/circuit/phase admission is separate.'])
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')

    mask = 0
    score = best
    step = 0
    while time.monotonic()-start < seconds and best < m*n:
        # Reheat/restart; exact bit-flip proposals never affect source events.
        if step % (8*width) == 0:
            mask = bestmask if rng.random() < .5 else rng.getrandbits(width)
            score, _ = evaluate(mask, m, n, events)
        bit = rng.randrange(width)
        candidate = mask ^ (1 << bit)
        value, cranks = evaluate(candidate, m, n, events)
        trials += 1
        temperature = max(.2, 2.5 * (1 - (step % (8*width))/(8*width)))
        if value >= score or rng.random() < math.exp((value-score)/temperature):
            mask, score = candidate, value
        if value > best:
            best, bestmask = value, candidate
            history.append(dict(trial=trials, floor=best, ranks=cranks, mask=str(bestmask)))
            save()
            print(name, 'q'+str(fixture['q']), 'NEW_FLOOR', best, cranks, 'trial', trials, flush=True)
        step += 1
    save()
    print(name, 'q'+str(fixture['q']), 'STOP', best, 'goal', m*n, 'trials', trials, flush=True)
    return best


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--family', choices=['REPAIRED', 'TWO-SITE'], default='REPAIRED')
    p.add_argument('--q', type=int, default=2)
    p.add_argument('--seconds', type=float, default=180)
    p.add_argument('--seed', type=int, default=1019)
    a = p.parse_args()
    source = 'inputs/REPAIRED-SIMPLIFIED.json' if a.family == 'REPAIRED' else 'inputs/ADMITTED-TWO-SITE.json'
    data = json.loads((OLD / source).read_text())
    f = next(f for f in data['fixtures'] if f['q'] == a.q)
    search(f, a.seconds, a.seed, a.family)


if __name__ == '__main__':
    main()
