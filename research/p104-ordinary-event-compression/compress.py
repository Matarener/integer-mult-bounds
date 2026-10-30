#!/usr/bin/env python3
"""Semantics-preserving peephole compression of a P104 local word.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Standard library only.
Three passes, repeated to a fixed point, change only ordinary ADD/SCALE/COPY/CLEAR events; MOVE, INIT and CLEAR
events, every chart, every owned lifetime and every endpoint row are unchanged:
  M1  two ADD r <- s at the same chart with no intervening event that reads or writes r or writes s merge into
      one ADD with the summed coefficient (both are deleted when the sum is zero);
  M2  two SCALE r with no intervening event touching r merge into one SCALE with the product coefficient;
  D1  an ADD/COPY/SCALE into an owned field that is CLEARed before that field is read again is deleted.
compress(word) returns the new word; it is deterministic.  The merged coefficients stay dyadic because sums and
products of dyadic rationals are dyadic.
"""
from collections import defaultdict
from fractions import Fraction as Q
from copy import deepcopy


def reads_writes(e):
    op = e[0]
    if op in ('MOVE', 'SCALE'): return {e[1]}, {e[1]}
    if op in ('INIT', 'CLEAR'): return set(), {e[1]}
    if op == 'COPY': return {e[2]}, {e[1]}
    return {e[1], e[2]}, {e[1]}          # ADD reads r and s, writes r


def pass_merge(prog):
    n = len(prog); dead = [False]*n; merged = 0
    last_add, last_scale = {}, {}
    for i, e in enumerate(prog):
        op = e[0]
        if op == 'ADD':
            key = (e[1], e[2]); j = last_add.get(key)
            if j is not None and prog[j][-1] == e[-1]:
                q = Q(prog[j][-2])+Q(e[-2])
                if q == 0:
                    dead[j] = dead[i] = True; del last_add[key]
                else:
                    prog[j] = ['ADD', e[1], e[2], str(q), e[-1]]; dead[i] = True
                merged += 1
                continue
        if op == 'SCALE':
            j = last_scale.get(e[1])
            if j is not None and prog[j][-1] == e[-1]:
                prog[j] = ['SCALE', e[1], str(Q(prog[j][-2])*Q(e[-2])), e[-1]]; dead[i] = True; merged += 1
                continue
        rd, wr = reads_writes(e); touched = rd | wr
        for key in [k for k in last_add if k[0] in touched or k[1] in wr]:
            del last_add[key]
        for key in [k for k in last_scale if k in touched]:
            del last_scale[key]
        if op == 'ADD': last_add[(e[1], e[2])] = i
        elif op == 'SCALE': last_scale[e[1]] = i
    return [e for e, d in zip(prog, dead) if not d], merged


def pass_dead(prog, public):
    n = len(prog); dead = [False]*n; count = 0
    pending = defaultdict(list)
    for i, e in enumerate(prog):
        op, r = e[0], e[1]
        if op == 'CLEAR' and r >= public:
            for j in pending.pop(r, []):
                dead[j] = True; count += 1
            continue
        rd, wr = reads_writes(e)
        for x in rd:
            if x >= public and x in pending:
                pending[x] = []
        if op in ('ADD', 'COPY', 'SCALE') and r >= public:
            pending[r].append(i)
        elif op == 'INIT' and r >= public:
            pending[r] = []
    return [e for e, d in zip(prog, dead) if not d], count


def compress(word):
    prog = [list(e) for e in word['program']]
    passes = []
    while True:
        before = len(prog)
        prog, m = pass_merge(prog)
        prog, d = pass_dead(prog, word['public'])
        passes.append({'merged': m, 'dead': d, 'events': len(prog)})
        if len(prog) == before and m == 0:
            break
    out = deepcopy(word)
    out['program'] = prog
    return out, passes


if __name__ == '__main__':
    import gzip, json, sys
    w = json.loads(gzip.decompress(open(sys.argv[1], 'rb').read()))
    out, passes = compress(w)
    print(json.dumps(passes))
    if len(sys.argv) > 2:
        open(sys.argv[2], 'wb').write(gzip.compress(json.dumps(out, separators=(',', ':')).encode()))
