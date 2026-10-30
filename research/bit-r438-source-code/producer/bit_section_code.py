#!/usr/bin/env python3
"""R438 source coding with three actual repaired target rows over F2.

The source code is invertible and generally not an involution.  Its literal
inverse is used on the backward local call.  This is a local changed interface,
with native/global/precision admission left to independent work.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import bit_transvection as base

HERE = Path(__file__).resolve().parent
need, prod, inv, bits, rank = base.require, base.product, base.inverse, base.bits, base.rank


def transpose(rows, n):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(n)]


def kernel(rows, n):
    rows, pivots, used = rows[:], [], 0
    for j in range(n):
        p = next((i for i in range(used, len(rows)) if rows[i] >> j & 1), None)
        if p is None:
            continue
        rows[used], rows[p] = rows[p], rows[used]
        for i in range(len(rows)):
            if i != used and rows[i] >> j & 1:
                rows[i] ^= rows[used]
        pivots.append(j)
        used += 1
    result = []
    for j in range(n):
        if j not in pivots:
            value = 1 << j
            for i, p in enumerate(pivots):
                if rows[i] >> j & 1:
                    value |= 1 << p
            result.append(value)
    need(prod(rows, transpose(result, n)) == [0] * len(rows), 'Kernel failed')
    return result


def particular(left, right):
    """Solve left X=right with all nonpivot variables zero."""
    n = len(left)
    rows = [a | (b << n) for a, b in zip(left, right)]
    pivots, used = [], 0
    for j in range(n):
        p = next((i for i in range(used, n) if rows[i] >> j & 1), None)
        if p is None:
            continue
        rows[used], rows[p] = rows[p], rows[used]
        for i in range(n):
            if i != used and rows[i] >> j & 1:
                rows[i] ^= rows[used]
        pivots.append(j)
        used += 1
    need(all(row >> n == 0 for row in rows[used:]), 'Inconsistent right-hand side')
    result = [0] * n
    for i, p in enumerate(pivots):
        result[p] = rows[i] >> n
    need(prod(left, result) == right, 'Particular solution failed')
    return result


def cnot_word(matrix):
    """A literal row-ADD circuit for an invertible binary square matrix."""
    rows, ops = matrix[:], []
    n = len(rows)
    def add(dst, src):
        rows[dst] ^= rows[src]
        ops.append((dst, src))
    for j in range(n):
        p = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        need(p is not None, 'Singular CNOT matrix')
        if p != j:
            add(j, p)
            add(p, j)
            add(j, p)
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                add(i, j)
    need(rows == [1 << i for i in range(n)], 'CNOT elimination failed')
    rows = [1 << i for i in range(n)]
    result = list(reversed(ops))
    for dst, src in result:
        rows[dst] ^= rows[src]
    need(rows == matrix, 'CNOT circuit order failed')
    return result


def section(data):
    R, K, M, J = (data[k] for k in ('R', 'K', 'M', 'J'))
    N = [(1 << i) ^ row for i, row in enumerate(M)]
    C0 = kernel(transpose(N, 9), 9)
    need(len(C0) == 3, 'Wrong left-nullity')
    C = prod(C0, R)
    selected, columns = [], []
    for p in range(111):
        column = sum(((row >> p) & 1) << j for j, row in enumerate(C))
        if rank(columns + [column]) > len(columns):
            selected.append(p)
            columns.append(column)
        if len(selected) == 3:
            break
    S = [sum(((row >> p) & 1) << j for j, p in enumerate(selected)) for row in R]
    B0 = prod(inv(prod(C0, S)), C0)
    need(prod(B0, S) == [1 << j for j in range(3)], 'Bad rank3 section')
    F9 = [(1 << j) ^ row for j, row in enumerate(prod(S, B0))]
    X0 = particular(N, F9)
    T = transpose(kernel(N, 9), 9)
    X = [a ^ b for a, b in zip(X0, prod(T, B0))]
    need(rank(X) == 9 and prod(N, X) == F9, 'Invertible quotient lift failed')
    PB = [0] * 111
    for j, p in enumerate(selected):
        PB[p] = B0[j]
    W = [a ^ b for a, b in zip(prod(K, X), PB)]
    Hinv = [(1 << p) ^ row for p, row in enumerate(prod(W, R))]
    need(rank(Hinv) == 111, 'Source inverse code singular')
    H = inv(Hinv)
    Q = prod(PB, R)
    need(prod(J, Hinv) == [(1 << p) ^ row for p, row in enumerate(Q)], 'JHinv residual failed')
    need([a ^ b for a,b in zip(J, prod(Q, H))] == H, 'Coded target identity failed')
    need(prod(H, Hinv) == [1 << p for p in range(111)], 'Source code inverse failed')
    need([p for p,row in enumerate(Q) if row] == selected, 'Wrong target support')
    return dict(R=R, K=K, M=M, J=J, N=N, C0=C0, C=C, selected=selected,
                S=S, B0=B0, F9=F9, X0=X0, T=T, X=X, W=W,
                H=H, Hinv=Hinv, Q=Q)


def compact_code(data, pivots):
    # Replace nine physical pivot coordinates by a normalized query basis.
    R = data['R']
    S = [sum(((row >> p) & 1) << j for j,p in enumerate(pivots)) for row in R]
    query = prod(inv(S), R)
    B = [1 << p for p in range(111)]
    prepare = []
    for j, p in enumerate(pivots):
        B[p] = query[j]
        for src in bits(query[j] ^ (1 << p)):
            need(src not in pivots, 'Normalized query still mixes pivots')
            prepare.append([1, p, src, 1, 1, 21])
    need(prod(B, B) == [1 << p for p in range(111)], 'Query change not involutive')
    middle = prod(prod(B, data['H']), B)
    pivot_set = set(pivots)
    D = [sum(((middle[p] >> q) & 1) << j for j,q in enumerate(pivots)) for p in pivots]
    fanout = []
    for p in range(111):
        allowed = sum(1 << q for q in pivots) | ((1 << p) if p not in pivot_set else 0)
        need(middle[p] & ~allowed == 0, 'Source code has a non-query middle term')
        if p not in pivot_set:
            need(middle[p] >> p & 1, 'Nonpivot identity diagonal missing')
            for src in bits(middle[p] ^ (1 << p)):
                fanout.append([1, p, src, 1, 1, 22])
    small = [[1, pivots[d], pivots[s], 1, 1, 23] for d,s in cnot_word(D)]
    unprepare = [rec[:5] + [24] for rec in reversed(prepare)]
    records = prepare + fanout + small + unprepare
    rows = [1 << p for p in range(111)]
    for op, dst, src, coefficient, frame, phase in records:
        rows[dst] ^= rows[src]
    need(rows == data['H'], 'Compact source word differs from its code')
    return records, dict(query=query, pivots=pivots, B=B, middle=middle, D=D,
                         prepare_adds=len(prepare), fanout_adds=len(fanout),
                         quotient_adds=len(small), unprepare_adds=len(unprepare))


def main():
    word, builder, baseline, old_records = base.load()
    old_data = base.matrices(word)
    _, old_parts = base.construct(word, old_records, old_data)
    data = section(old_data)
    code, code_data = compact_code(data, old_data['selected'])
    repair = []
    b, count, v = 222, 660, 111
    for p in data['selected']:
        cap = word['final'][v+p]
        episode = [[2,b,count,1,cap,1], [1,v+p,count,1,cap,15], [3,b,count,1,cap,0]]
        gather = [[1,b,src,1,1,16] for src in bits(data['Q'][p])]
        repair.extend(episode + gather + episode + [rec[:5]+[17] for rec in gather])
    records = old_parts['prefix'] + old_parts['clean'] + code + repair
    forward = base.replay(word, builder, records, data)
    reverse = base.replay(word, builder, records, data, reverse=True)
    expect = Counter({int(k):n for k,n in baseline['profile'].items()})
    expect[7] -= 9
    expect[1] += 6
    need(forward['profile'] == dict(sorted(expect.items())), 'Profile differs')
    need(reverse['profile'] == forward['profile'], 'Reverse profile differs')
    need(forward['rank_mass'] == 5064 and forward['copies'] == 6, 'Wrong paid bill')
    controls = [
        base.must_fail('omit_changed_D', lambda: base.replay(
            word,builder,records[len(old_parts['prefix']):],data)),
        base.must_fail('omit_query_unprepare', lambda: base.replay(
            word,builder,[r for r in records if not(r[0] == 1 and r[5] == 24)],data)),
        base.must_fail('omit_dirty_repair_restore', lambda: base.replay(
            word,builder,[r for r in records if not(r[0] == 1 and r[5] == 17)],data)),
        base.must_fail('mutate_copied_snapshot', lambda: base.replay(
            word,builder,records,data,mutate_snapshot=True)),
        base.must_fail('use_same_noninvolutive_code_in_reverse', lambda: base.replay(
            word,builder,records,{**data,'Hinv':data['H']},reverse=True)),
    ]
    container = dict(format='coded-r438-three-row-local-records-v1',
                     public_registers=660,private_register=660,
                     source_word=str(base.WORD),source_gzip_sha256=base.WORD_SHA,
                     start=word['start'],final=word['final'],records=records,
                     copy_schema='[2,physical_source,660,sourceframe,privateframe,rank]',
                     erase_schema='[3,physical_source,660,sourceframe,privateframe,0]')
    raw = base.canonical(container)
    outword = HERE/'BIT-THREE-ROW-WORD.json.gz'
    outword.write_bytes(gzip.compress(raw,mtime=0))
    output = dict(status='PASS_LOCAL_THREE_TARGET_ROWS_NO_GLOBAL_SUPPLIER_NO_NEW_KAPPA',
                  source_pin=base.MAIN_PIN,source_word=str(base.WORD),source_gzip_sha256=base.WORD_SHA,
                  baseline_builder_sha256=base.BUILDER_SHA,
                  output_word=str(outword),output_canonical_sha256=hashlib.sha256(raw).hexdigest(),
                  output_gzip_sha256=hashlib.sha256(outword.read_bytes()).hexdigest(),
                  matrices=data,source_code=code_data,forward=forward,reverse=reverse,
                  source_code_rank=rank([row^(1<<p) for p,row in enumerate(data['H'])]),
                  adds=sum(r[0] == 1 for r in records),records=len(records),
                  part_adds=dict(changed_D=len(old_parts['prefix']),
                                 clean=sum(r[0] == 1 for r in old_parts['clean']),
                                 code=len(code),repairs=sum(r[0] == 1 for r in repair)),
                  positive=base.positive_bounds(records,660),negative_controls=controls,
                  contract=dict(forward='(x,y,h)->(Ax,y+Ax,h)',
                                literal_inverse='(x,y,h)->(A^-1 x,y+x,h)',
                                matrix_names='H=A, Hinv=A^-1; J Hinv=I+Q',
                                initial_frames='source Pp; target0; helper0',
                                final_frames='source FULL; target Pp-perp; helper FULL',
                                copied_snapshots='Two unchanged arbitrary-helper snapshots per each of three target rows'),
                  scope='Finite660-column F2 proof and complete literal local frame/rank invoice; no native global admission',
                  unresolved=['Actual native operator lift and complementary backward frame interpretation',
                              'Signed integer lift, new precision reserve, and physical scalar scratch',
                              'Global19-event code and terminal cap decoder',
                              'Chronological owners, unused remainders, full recursive supplier contract'])
    (HERE/'BIT-THREE-ROW.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:output[k] for k in ('status','forward','adds','part_adds','source_code_rank','positive')},
                     indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
