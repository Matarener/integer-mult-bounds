"""Independent replay of a G20 global caller stream (from scratch; imports no package code).

Checks:
 1. GF(2) bitmap replay of every event of GLOBAL.jsonl.gz on N originals + owned registers:
    owned-only clears/headers, distinct ADD operands, free frame moves only on zero payloads,
    final state = identity on all originals and zero on all owned registers.
 2. Paid histogram recounted from QUERY events == INVOICE.json paid; QUERY count == QUERYs.
 3. Each of the 18 calls in CALLS.json: the core slice [core_begin, core_end) is exactly the local
    WORD under ONE consistent injective wire->register map (op by op, same ranks and frames).
 4. TARGET-OWNERS: owners are a permutation of all originals; histogram == INVOICE targets;
    rank-8 targets sit in 8-dim frames; split targets have rank = dim(source)-dim(target).
 5. Rank surplus recomputed.
Usage: python3 audit_global.py PACKAGE_DIR FRAMES.json label
"""
from collections import Counter
from pathlib import Path
import gzip, json, sys, time


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def main(pkg, frames_path, label):
    pkg = Path(pkg)
    inv = json.load(open(pkg / 'INVOICE.json'))
    calls = json.load(open(pkg / 'CALLS.json'))
    targets = json.load(open(pkg / 'TARGET-OWNERS.json'))
    word = json.loads(gzip.decompress((pkg / 'WORD.json.gz').read_bytes()))
    dims = {int(k): v['dim'] for k, v in json.load(open(frames_path))['frames'].items()}
    events = [json.loads(l) for l in gzip.decompress((pkg / 'GLOBAL.jsonl.gz').read_bytes()).splitlines()]
    N, OWN = inv['originals'], inv['owned_allocated']
    owned = set(range(N, N + OWN))
    log(label, 'events', len(events), 'originals', N, 'owned', OWN)

    # 1+2: bitmap replay
    val = [1 << i for i in range(N + OWN)]
    paid, ops, routes = Counter(), Counter(), Counter()
    for ix, e in enumerate(events):
        op = e[0]; ops[op] += 1
        if op == 'OWNED_CLEAR':
            need(e[1] in owned, 'clear of original at %d' % ix); val[e[1]] = 0
        elif op == 'OWNED_ZERO_HEADER':
            need(e[1] in owned and val[e[1]] == 0, 'header on nonzero/original at %d' % ix)
        elif op == 'ADD':
            need(e[1] != e[2], 'self ADD at %d' % ix); val[e[1]] ^= val[e[2]]
        elif op == 'QUERY':
            k = e[2]; need(isinstance(k, int) and k > 0, 'query rank at %d' % ix); paid[k] += 1
        elif op == 'WHOLE_ZERO_FRAME':
            need(val[e[1]] == 0, 'free move of nonzero payload at %d' % ix)
        elif op == 'PAID_PORT_ROUTE':
            routes[e[4]] += 1
        else:
            need(False, 'unknown op %s' % op)
        if ix % 50000 == 0:
            log(label, 'event', ix)
    need(all(val[i] == 1 << i for i in range(N)), 'identity on all originals')
    need(all(val[i] == 0 for i in owned), 'owned registers end at zero')
    P = {int(k): v for k, v in inv['paid'].items()}
    need(dict(paid) == P and sum(paid.values()) == inv['QUERYs'], 'paid histogram recount %s vs %s' % (dict(paid), P))
    log(label, 'PASS bitmap replay + paid recount', dict(ops), 'routes', dict(routes))

    # 3: per-call embedding of the local word
    rec = word['records']
    for c in calls:
        sl = events[c['core_begin']:c['core_end']]
        need(len(sl) == len(rec), 'call length stage %s' % c['stage'])
        m, back = {}, {}

        def bind(lw, g):
            if lw in m:
                need(m[lw] == g, 'inconsistent wire map stage %s wire %s' % (c['stage'], lw))
            else:
                need(g not in back, 'non-injective wire map stage %s' % c['stage'])
                m[lw] = g; back[g] = lw
        for e, g in zip(rec, sl):
            op = e[0]
            if op == 'ADD':
                need(g[0] == 'ADD', 'op mismatch'); bind(e[1], g[1]); bind(e[2], g[2])
            elif op == 'Q':
                need(g[0] == 'QUERY' and g[2] == e[4] and g[3][2:4] == [e[2], e[3]], 'query mismatch'); bind(e[1], g[1])
            elif op == 'ZERO_Q':
                need(g[0] == 'WHOLE_ZERO_FRAME' and g[2:5] == e[2:5], 'free move mismatch'); bind(e[1], g[1])
            elif op == 'ERASE':
                need(g[0] == 'OWNED_CLEAR', 'erase mismatch'); bind(e[1], g[1])
            elif op == 'INIT':
                need(g[0] == 'OWNED_ZERO_HEADER' and g[2] == e[2], 'init mismatch'); bind(e[1], g[1])
            else:
                need(False, 'local op ' + op)
        need(all(m[o] in owned for o in word['owned'] if o in m), 'local owned wires map to owned registers')
        need(all(m[i] not in owned for i in m if i not in word['owned']), 'local originals map to originals')
    log(label, 'PASS all %d calls embed the local word under consistent injective wire maps' % len(calls))

    # 4: targets
    owners = sorted(t['original_owner'] for t in targets)
    need(owners == list(range(N)), 'target owners = all originals exactly once')
    T = Counter(t['rank'] for t in targets)
    TI = {int(k): v for k, v in inv['targets'].items()}
    need(dict(T) == TI, 'target histogram')
    for t in targets:
        if 'native_frame' in t:
            need(dims[t['native_frame']] == t['rank'], 'rank-%d target frame dim' % t['rank'])
        if 'split' in t:
            need(dims[t['native_source_frame']] - dims[t['native_target_frame']] == t['rank'], 'split target rank')
    kinds = Counter((t.get('split') or ('native' if 'native_frame' in t else 'main'), t['rank']) for t in targets)
    surplus = sum(k * v for k, v in T.items()) - sum(k * v for k, v in paid.items())
    need(surplus == inv['rank_surplus'], 'rank surplus')
    res = dict(label=label, events=len(events), ops=dict(ops), paid=dict(sorted(paid.items())),
               targets=dict(sorted(T.items())), target_kinds={'%s:%s' % k: v for k, v in sorted(kinds.items(), key=str)},
               rank_surplus=surplus, calls=len(calls))
    log('PASS', json.dumps(res))


if __name__ == '__main__':
    main(*sys.argv[1:4])
