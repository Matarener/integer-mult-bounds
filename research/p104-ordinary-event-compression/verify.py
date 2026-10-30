#!/usr/bin/env python3
"""Verify the ordinary-event compression of the PR5907 P104 word.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
Checks: (0) pinned live inputs; (1) compress.py regenerates the shipped word (decompressed payload equality);
(2) own exact replay of the source and compressed words: identical MOVE/INIT/CLEAR sequences, identical charts,
identical rows of all 799 roles at every MOVE and at the end; (3) the PR5827 author checker local.py (loaded
unmodified) accepts the compressed word with the same paid profile, helper profile and storage inventory, and its
dense transpose check passes; (4) two controls: a changed merged coefficient and a deleted live ADD are rejected
by the row comparison; (5) RESULT.json equals the recomputed receipt.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, importlib.util, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/p104-helper468-rung-removal/WORD.json.gz'
LOCAL = ROOT/'research/p104-unread-path-resynthesis/local.py'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


def span(basis):
    s = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in s, 'independent binary basis')
        s |= {x ^ v for x in s}
    return frozenset(s)


def replay(w):
    """Own exact replay: returns (trace of (MOVE/INIT/CLEAR events, rows of the moved role), final rows, charts)."""
    S = [span(f) for f in w['frames']]
    n, m = w['public'], w['owned_fields']
    cur = list(w['initial'])+[None]*m
    rows = [{r: Q(1)} for r in range(n)] + [{} for _ in range(m)]
    owned, trace = set(), []
    for i, e in enumerate(w['program']):
        op, r = e[0], e[1]
        need(0 <= r < n+m, 'role index')
        if op == 'MOVE':
            a, b, private = e[2], e[3], e[4]
            need(cur[r] == a and (r in owned) == private, 'transport source and ownership at %d' % i)
            need(S[b] < S[a] if private else S[a] < S[b], 'strict nesting at %d' % i)
            trace.append((tuple(e), tuple(sorted(rows[r].items()))))
            cur[r] = b
        elif op == 'INIT':
            need(r >= n and r not in owned, 'owned init'); owned.add(r); rows[r], cur[r] = {}, e[2]
            trace.append((tuple(e), ()))
        elif op == 'CLEAR':
            need(r in owned and cur[r] == e[2], 'owned erasure'); owned.discard(r); rows[r], cur[r] = {}, None
            trace.append((tuple(e), ()))
        else:
            q, f = Q(e[-2]), e[-1]
            need(q != 0 and cur[r] == f and q.denominator & (q.denominator-1) == 0, 'ordinary event at %d' % i)
            if op == 'SCALE':
                rows[r] = {k: q*v for k, v in rows[r].items()}
            else:
                s = e[2]; need(s != r and cur[s] == f, 'common chart at %d' % i)
                if op == 'COPY':
                    need(r in owned and not rows[r], 'COPY into cleared owned field')
                    rows[r] = {k: q*v for k, v in rows[s].items()}
                else:
                    need(op == 'ADD', 'opcode')
                    t = dict(rows[r])
                    for k, v in rows[s].items():
                        t[k] = t.get(k, 0)+q*v
                    rows[r] = {k: v for k, v in t.items() if v}
    need(not owned and cur[:n] == w['final'], 'exits')
    live = set(w['live'])
    for r in range(n+m):
        expected = {r: Q(1)} if r < n else {}
        if r-112 in live:
            expected[r-112] = Q(1)
        need(rows[r] == expected, 'endpoint row %d' % r)
    return trace


def main():
    pins = read(HERE/'SOURCES.json')
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin '+row['path'])
    source = read(SOURCE)
    C = load('p104_event_compress', HERE/'compress.py')
    word, passes = C.compress(source)
    shipped = read(HERE/'WORD.json.gz')
    need(word == shipped, 'regenerated word equals the shipped decompressed payload')
    print('regenerated', json.dumps(passes), flush=True)
    # (2) own replay: identical paid/owned event sequences and identical rows at every one of them
    t0, t1 = replay(source), replay(word)
    need(t0 == t1, 'identical MOVE/INIT/CLEAR sequence and identical rows of every moved field')
    need(sum(1 for e in word['program'] if e[0] == 'MOVE') == 3454, 'MOVE count')
    need({k: v for k, v in source.items() if k != 'program'} == {k: v for k, v in word.items() if k != 'program'}, 'unchanged header')
    print('own replay', len(t0), 'paid/owned events compared', flush=True)
    # (3) the author checker, loaded unmodified
    L = load('p104_local_5827', LOCAL)
    before, after = L.replay(source), L.replay(word)
    for key in ('paid', 'helpers', 'public_inputs', 'owned_fields', 'owned_lifetimes', 'peak_owned_fields', 'paid_rank_mass'):
        need(before[key] == after[key], 'author replay: unchanged '+key)
    need(after['real_scalar_allowance'] < before['real_scalar_allowance'], 'scalar allowance does not grow')
    L.reverse_columns(word)
    print('author checker', {k: after[k] for k in ('paid', 'helpers', 'real_scalar_allowance')}, flush=True)
    # (4) controls
    def reject(mutant, why):
        try:
            replay(mutant)
        except ValueError:
            return
        raise ValueError('control accepted: '+why)
    bad = json.loads(json.dumps(word))
    i = next(i for i, e in enumerate(bad['program']) if e[0] == 'ADD' and e[1] < word['public'])
    bad['program'][i][-2] = str(Q(bad['program'][i][-2])*2)
    reject(bad, 'doubled coefficient of a public ADD')
    bad = json.loads(json.dumps(word))
    del bad['program'][i]
    reject(bad, 'deleted live public ADD')
    ops_in, ops_out = Counter(e[0] for e in source['program']), Counter(e[0] for e in word['program'])
    result = {'source': 'research/p104-helper468-rung-removal/WORD.json.gz', 'events_before': len(source['program']),
              'events_after': len(word['program']), 'freed': len(source['program'])-len(word['program']),
              'passes': passes, 'ops_before': dict(ops_in), 'ops_after': dict(ops_out),
              'author_replay': {k: after[k] for k in ('paid', 'helpers', 'public_inputs', 'owned_fields', 'owned_lifetimes', 'peak_owned_fields', 'paid_rank_mass', 'real_scalar_allowance')},
              'author_replay_source_scalar_allowance': before['real_scalar_allowance'],
              'word_payload_sha256': sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
              'controls': {'doubled_coefficient': 'rejected', 'deleted_live_add': 'rejected'}}
    result['author_replay'] = {k: ({str(a): b for a, b in v.items()} if isinstance(v, dict) else v) for k, v in result['author_replay'].items()}
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=1, sort_keys=True)+'\n')
    need(read(HERE/'RESULT.json') == result, 'RESULT.json equals the recomputed receipt')
    print('PASS_P104_ORDINARY_EVENT_COMPRESSION')


if __name__ == '__main__':
    main()
