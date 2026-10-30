"""A source-bound 2^76 collision certificate. zxv + OpenAI Codex. Apache-2.0."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/p104-helper-subspace-splits/WORD.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sr(n, d, u=0):
    need(d > 0 and d & (d-1) == 0 and 0 <= u < d, 'dyadic coin')
    return (n+d-1-u)//d


def event(e):
    q = Q(e[-2])
    return e[0], e[1], e[2] if e[0] == 'ADD' else None, q.numerator, q.denominator


def forward(initial, events):
    x = list(initial)
    peak = max(map(abs,x), default=0)
    for op,r,s,n,d in events:
        x[r] = x[r]+sr(n*x[s],d) if op == 'ADD' else sr(n*x[r],d)
        peak = max(peak,abs(x[r]))
    return x, peak


def inverse_prefix(output, events, bits):
    """All-zero coins; each signed halving has two distinct exact preimages."""
    x = list(output)
    it = iter(bits)
    for op,r,s,n,d in reversed(events):
        if op == 'ADD':
            x[r] -= sr(n*x[s],d)
        elif d == 2:
            x[r] = n*(2*x[r]-next(it))
        else:
            need(n == -1 and d == 1, 'no doubling in surjective prefix')
            x[r] = -x[r]
    need(next(it,None) is None, 'all prefix choice bits consumed')
    return x


def inverse_bound(output_bound, events):
    bound = output_bound
    for op,r,s,n,d in reversed(events):
        if op == 'ADD':
            bound += (abs(n)*bound+d-1)//d
        elif d == 2:
            bound = 2*bound+1
        else:
            need(n == -1 and d == 1, 'prefix SCALE domain')
    return bound


def source():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'],
                 'source bytes: '+pin['path'])
    p = json.loads((HERE/'PREDECESSOR.json').read_text())
    need(sha256((HERE/p['retained_path']).read_bytes()).hexdigest() == p['sha256'],
         'retained PR6066 statement')
    w = json.loads(gzip.decompress((ROOT/WORD).read_bytes()))
    cut = next(i for i,e in enumerate(w['program']) if e[0] == 'MOVE')
    need(w['public'] == 748 and cut == 9589 and w['frames'][3] == [], 'historical source ABI')
    prefix = w['program'][:cut]
    need(all(e[0] in ('ADD','SCALE') and e[-1] == 3 for e in prefix), 'common empty-chart scalar block')
    events = [event(e) for e in prefix]
    for op,r,s,n,d in events:
        need(0 <= r < 748 and (op != 'ADD' or 0 <= s < 748 and r != s), 'public indices')
        need(d in (1,2,4) and abs(Q(n,d)) <= 16, 'coefficient domain')
        if op == 'SCALE':
            need(Q(n,d) in (Q(-1),Q(2),Q(1,2),Q(-1,2)), 'SCALE domain')
    return events


def calculate():
    events = source()
    pre, tail = events[:8411], events[9532:]
    halves = sum(op == 'SCALE' and d == 2 for op,r,s,n,d in events)
    doubles = sum(op == 'SCALE' and n == 2 and d == 1 for op,r,s,n,d in events)
    need(halves == 84 and doubles == 32, 'source half/double ledger')
    need(sum(op == 'SCALE' and d == 2 for op,r,s,n,d in pre) == 60, 'sixty prefix losses')
    need(all(op == 'ADD' or n == -1 or d == 2 for op,r,s,n,d in pre), 'surjective prefix')
    need(len(tail) == 57 and all(op == 'ADD' for op,r,s,n,d in tail), 'bijective trailing shears')
    fixture = json.loads((HERE/'COLLISIONS.json').read_text())
    need(len(fixture['blocks']) == 8, 'eight collision blocks')
    blocks, cursor, signatures, bound = [], 8411, [], 0
    for b, row in enumerate(fixture['blocks']):
        lo = 272+16*b
        size = 137 if b < 3 else 142
        es = events[cursor:cursor+size]
        need(row['block'] == b and all(lo <= r < lo+16 and
             (s is None or lo <= s < lo+16) for op,r,s,n,d in es), 'independent literal block')
        local = [(op,r-lo,None if s is None else s-lo,n,d) for op,r,s,n,d in es]
        xs = row['input_preimages']
        need(len(xs) == 4 and len({tuple(x) for x in xs}) == 4 and
             all(len(x) == 16 and all(type(v) is int for v in x) for x in xs), 'four distinct preimages')
        for x in xs:
            y, peak = forward(x,local)
            need(y == row['output'], 'literal all-zero-tape collision')
            bound = max(bound,max(map(abs,x)))
        # Three halvings leave only eight possible inverse branches. Enumerate them
        # to check the fixture's complete fiber, without relying on search output.
        states = [list(row['output'])]
        for op,r,s,n,d in reversed(local):
            new = []
            for old in states:
                x = list(old)
                if op == 'ADD':
                    x[r] -= sr(n*x[s],d); new.append(x)
                elif d == 2:
                    for bit in (0,1):
                        xx = list(x); xx[r] = n*(2*x[r]-bit); new.append(xx)
                elif n == 2:
                    if x[r] % 2 == 0:
                        x[r] //= 2; new.append(x)
                else:
                    x[r] = -x[r]; new.append(x)
            states = new
        need({tuple(x) for x in states} == {tuple(x) for x in xs}, 'complete exact four-point block fiber')
        signatures.append(sha256(json.dumps(local,separators=(',',':')).encode()).hexdigest())
        blocks.append((lo,local,xs))
        cursor += size
    need(cursor == 9532, 'complete middle coverage')
    need(all(not 272 <= r < 400 and (s is None or not 272 <= s < 400)
             for op,r,s,n,d in tail), 'trailing shears separate from collision blocks')
    final, start = [0]*748, [0]*748
    for b,(lo,es,xs) in enumerate(blocks):
        start[lo:lo+16] = xs[0]
    final, _ = forward(start,events[8411:])
    patterns = [[0]*60,[1]*60] + [[int(i == j) for i in range(60)] for j in range(60)]
    checked, peak = 0, 0
    for bits in patterns:
        x = inverse_prefix(start,pre,bits)
        actual, size = forward(x,events)
        need(actual == final, 'complete prefix lift and full endpoint')
        checked += 1; peak = max(peak,size.bit_length())
    for b,(lo,es,xs) in enumerate(blocks):
        for xlocal in xs[1:]:
            state = list(start); state[lo:lo+16] = xlocal
            x = inverse_prefix(state,pre,[0]*60)
            actual,size = forward(x,events)
            need(actual == final, 'independent block lift reaches common full endpoint')
            checked += 1; peak = max(peak,size.bit_length())
    # The written product proof supplies the unenumerated 2^76 quantifier.
    upper = inverse_bound(bound,pre)
    local_checks = 0
    for y,n,u in product(range(-64,65),(-1,1),(0,1)):
        xs = [n*(2*y+(2*u-1)*r) for r in (0,1)]
        need(xs[0] != xs[1] and all(sr(n*x,2,u) == y for x in xs), 'two-to-one half lemma')
        local_checks += 1
    need([sr(2*x,2,0) for x in range(-5,6)] == list(range(-5,6)),
         'double-then-half is injective: raw half counts alone do not suffice')
    # Altered output and a deleted collision state must invalidate the certificate.
    try:
        need(forward(fixture['blocks'][0]['input_preimages'][0],blocks[0][1])[0] ==
             [x+int(i == 0) for i,x in enumerate(fixture['blocks'][0]['output'])], 'wrong output')
    except ValueError:
        pass
    else:
        raise ValueError('wrong collision output accepted')
    need(60+sum(2 for block in blocks) == 76 and 84-76 == 8, 'retention floor and possible headroom')
    p = json.loads((HERE/'PREDECESSOR.json').read_text())['retained_verifier']
    raw = (HERE/p['retained_path']).read_bytes()
    need(sha256(raw).hexdigest() == p['sha256'], 'literal predecessor verifier')
    old = types.ModuleType('retained_pr6066')
    old.__file__ = str(HERE/p['retained_path'])
    exec(compile(raw,old.__file__,'exec'),old.__dict__)
    compressed = types.ModuleType('compressed_source')
    exec(compile((HERE/'compressed.py').read_bytes(),str(HERE/'compressed.py'),'exec'),compressed.__dict__)
    construction = compressed.verify(events,old)
    return dict(status='PASS_OPTIMAL_STOCHASTIC_RETAINED_LOG',events=9589,
                public_integer_roles=748,source_halves=halves,source_doubles=doubles,
                surjective_prefix_events=8411,prefix_fiber_power=60,
                independent_blocks=8,block_fiber_sizes=[4]*8,block_program_sha256=signatures,
                full_fiber_power_lower=76,source_log_bits=84,optimal_retained_log_bits=76,
                saved_log_bits=8,construction=construction,
                full_word_lifts_checked=checked,half_lemma_checks=local_checks,
                lift_bound_magnitude_bits=upper.bit_length(),fixture_peak_magnitude_bits=peak,
                conservative_signed_guard_bits=upper.bit_length()+8,
                scope='Optimal retained residue capacity for the exact PR6066 logical boundary and unchanged tape; physical working scratch and full native costs remain open; no new kappa.')


def main():
    result = calculate()
    need(result == json.loads((HERE/'RESULT.json').read_text()), 'committed semantic receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
