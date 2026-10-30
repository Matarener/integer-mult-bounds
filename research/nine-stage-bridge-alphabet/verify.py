#!/usr/bin/env python3
"""Nine-stage bridge schedules: the idle alphabet 16/32/48 is forced in the simple-riding class.

Standard library only. Checks
  1. the exact eight-wire rule is the one in replay_gk.py, and RECIPE-9 closes to the identity;
  2. the level model reproduces the DATA-PHASES idle children of every port;
  3. the simple-riding builder rebuilds RECIPE-9 and the exact closure test recovers its three final bridges;
  4. census: every simple-riding design with globally alternating stage directions is tested exactly;
     exactly 16 close, all with the incumbent idle alphabet;
  5. a deterministic sample (every 1000th design) of non-alternating designs: none closes;
  6. rejection controls; equality with RESULT.json.
"""
import hashlib, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import bridges as B  # noqa: E402

RECIPE = ROOT / 'research/e8-signed-prefix/vendor/cx/work/odd-stages/RECIPE-9.json'
RULE = ROOT / 'research/e8-complex-gauge-kernel/code/replay_gk.py'
PHASES = ROOT / 'research/direct-delivery504-global/inputs/data-base/work/complex-nine-native/DATA-PHASES.json'
INCUMBENT = (8, 8, 8, 16, 16, 32, 32, 48, 48)
BEST_RELAXED = (8, 8, 8, 8, 16, 32, 40, 48, 48)


def need(c, msg):
    if not c:
        raise SystemExit('FAIL: ' + msg)


def main():
    out = {}
    # 1. exact rule bound to the repository's own checker
    rule = RULE.read_text()
    for line in ["dst,src,q=(a,b,-1) if e['reverse'] else (b,a,1)",
                 "matrix[2*i]=[x+q*y for x,y in zip(matrix[2*i],matrix[2*j])]",
                 "matrix[2*j+1]=[x-q*y for x,y in zip(matrix[2*j+1],matrix[2*i+1])]",
                 "for i in range(4):matrix[2*i]=old[2*i+1];matrix[2*i+1]=[-x for x in old[2*i]]",
                 "assert matrix==[[int(i==j) for j in range(8)] for i in range(8)]"]:
        need(line in rule, 'replay_gk.py rule line missing: ' + line)
    recipe = json.loads(RECIPE.read_text())
    need(B.apply(recipe) == B.IDENTITY, 'RECIPE-9 closes')
    bad = json.loads(RECIPE.read_text()); bad[2]['coefficient'] = -1
    need(B.apply(bad) != B.IDENTITY, 'control: flipped bridge coefficient must fail')

    # 2. idle children: level model vs DATA-PHASES (two sides per port)
    seg = B.idle_segments(recipe)
    need(seg == INCUMBENT, f'idle segments {seg}')
    phases = json.loads(PHASES.read_text())
    want = Counter(INCUMBENT * 2)
    for r in phases['recipes']:
        got = Counter(c['rank'] for c in r['idle_children'] if c['rank'])
        need(got == want, f"port {r['port']} idle ranks {got}")
    out['incumbent_idle_children_per_side'] = list(seg)
    out['data_phases_ports_matched'] = len(phases['recipes'])

    # 3. builder and closure on the incumbent design
    inc = dict(owners=(0, 0, 0, 1, 1, 2, 2, 3, 3), dirs=(0, 1, 0, 1, 0, 1, 0, 1, 0), riders=[[], [2], [4], [6]])
    rec = B.build(inc)
    need(rec == recipe[:len(rec)], 'builder reproduces RECIPE-9 stages and riding bridges')
    cl = B.closure(rec)
    need(cl == recipe[len(rec):-1], f'closure recovers the three final bridges, got {cl}')

    # 4. census: all simple-riding designs; exact closure for every globally alternating design and
    #    for every design with the best relaxed-packing alphabet
    alt = [(0, 1, 0, 1, 0, 1, 0, 1, 0), (1, 0, 1, 0, 1, 0, 1, 0, 1)]
    tick = [0]

    def keep(seg, dirs):
        tick[0] += 1
        tag = ('alt ' if dirs in alt else '') + ('best ' if seg == BEST_RELAXED else '')
        if not tag and tick[0] % 1000 == 0:
            tag = 'sample'
        return tag
    total, alphabets, kept = B.census(keep)
    n_alt = 0; n_best = 0; closed = Counter(); best_closed = 0
    for s, d in kept:
        if d['tag'] == 'sample':
            continue
        is_alt = d['dirs'] in alt
        ok = B.closure(B.build(d)) is not None
        if is_alt:
            n_alt += 1
            if ok:
                closed[s] += 1
        if s == BEST_RELAXED:
            n_best += 1; best_closed += ok
    need(sum(closed.values()) == 16 and set(closed) == {INCUMBENT}, f'census {closed}')
    need(best_closed == 0, 'a design with the best relaxed alphabet closes')
    out['simple_riding_designs'] = total
    out['distinct_idle_alphabets'] = len(alphabets)
    out['alternating_designs'] = n_alt
    out['alternating_closable'] = {','.join(map(str, k)): v for k, v in closed.items()}
    out['best_relaxed_alphabet'] = list(BEST_RELAXED)
    out['best_relaxed_alphabet_designs'] = n_best
    out['best_relaxed_alphabet_closable'] = best_closed

    # 5. deterministic sample of non-alternating designs: every 1000th in census order
    sample = [d for s_, d in kept if d['tag'] == 'sample']
    tested = len(sample)
    closing = sum(1 for d in sample if B.closure(B.build(d)) is not None)
    need(tested >= 1900 and closing == 0, f'{closing} of {tested} sampled non-alternating designs close')
    out['non_alternating_sample'] = {'rule': 'every 1000th design in census order', 'tested': tested, 'closing': closing}

    # 6. control: a wrong final bridge fails
    broken = rec + [dict(x) for x in cl] + [B.TERMINAL]; broken[-2]['coefficient'] = 2
    need(B.apply(broken) != B.IDENTITY, 'control: wrong final bridge must fail')
    out['status'] = 'PASS_NINE_STAGE_BRIDGE_ALPHABET'

    res = HERE / 'RESULT.json'
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if '--emit' in sys.argv:
        res.write_text(text)
    need(res.read_text() == text, 'RESULT.json differs from recomputation')
    print(out['status'], hashlib.sha256(text.encode()).hexdigest())


if __name__ == '__main__':
    main()
