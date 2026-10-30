#!/usr/bin/env python3
"""Exact data for the balanced-decomposition obstruction. Apache-2.0.

Douglas Colkitt, with OpenAI Codex assistance. Standard library only.
The arbitrary-matrix rank lemma is proved in REPORT.md, not by enumeration.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'saturated_audit', ROOT.parent / 'saturated-character-register' / 'audit.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
W = 16
IDENTITY = tuple(1 << i for i in range(W))


def add(*matrices):
    rows = [0] * W
    for M in matrices:
        for i, row in enumerate(M):
            rows[i] ^= row
    return tuple(rows)


def multiply(A, B):
    result = []
    for row in A:
        out = 0
        for j in range(W):
            if row >> j & 1:
                out ^= B[j]
        result.append(out)
    return tuple(result)


def unit(i):
    return tuple((1 << i) if j == i else 0 for j in range(W))


def transpose(A):
    return tuple(sum(((A[i] >> j) & 1) << i for i in range(W)) for j in range(W))


def rank(A):
    return previous.binary_rank(A)


def decomposition_data():
    calls = previous.inventory()
    triple = {j for j,c in enumerate(calls) if sum(x*x for x in c['line']) == 3}
    assert triple == {15,18,29,32}
    all_bases = previous.screen(calls, W)['saturated_bases']
    bases = []
    for b in all_bases:
        remainder = set(b['calls']) - triple
        assert len(remainder) == 12
        # Omit the thirteenth, all-coordinate remainder. The remaining
        # twelve form an exact fourfold cover of all 36 nontriple calls.
        if all(sum(x*x for x in calls[j]['line']) == 1 for j in remainder):
            continue
        bases.append(dict(character=b['character'], calls=sorted(remainder)))
    nontriple = sorted(set(range(40))-triple)
    counts = Counter(j for b in bases for j in b['calls'])
    assert len(bases) == 12 and len(nontriple) == 36
    assert counts == Counter({j:4 for j in nontriple})
    for b in bases:
        residues = [previous.exponent(b['character'], c['B']) for c in calls]
        assert all(x%2 == 0 for x in residues)
        assert {j for j,x in enumerate(residues) if x == 2} == set(b['calls']) | triple
    return calls, triple, nontriple, bases, all_bases


COLORS = {
    0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9,
    10:4, 11:5, 12:6, 13:9, 14:0, 16:0, 17:1, 19:1,
    20:6, 21:7, 22:4, 23:5, 24:10, 25:11, 26:7, 27:8,
    28:2, 30:2, 31:3, 33:3, 34:9, 35:8, 36:10, 37:10, 38:11, 39:11,
}


def shared_system_controls(triple, nontriple, all_bases):
    """Exact feasible controls at Q-ranks 10,11,12, not uniform words.

    They demonstrate why checking only the shared equations is too weak.
    The rank-11 example is noncommuting. No solver is used to check them.
    """
    assert set(COLORS) == set(nontriple)
    for b in all_bases:
        assert sorted(COLORS[j] for j in set(b['calls'])-triple) == list(range(12))
    output = []
    for requested_rank in (10,11,12):
        atoms = [unit(i) for i in range(12)]
        if requested_rank == 10:
            atoms = [unit(0) if c < 3 else unit(c-2) for c in range(12)]
            special = [unit(i) for i in range(10,16)]
        elif requested_rank == 11:
            a = [0]*W; a[1] = (1<<1) | (1<<2)
            b = [0]*W; b[2] = (1<<1) | (1<<2)
            atoms[1], atoms[2] = tuple(a), tuple(b)
            c = [0]*W; c[2] = (1<<1) | (1<<2)
            d = [0]*W; d[1] = d[2] = 1<<2
            special = [unit(i) for i in range(12,16)] + [tuple(c),tuple(d)]
        else:
            special = [unit(i) for i in range(12,16)] + [unit(12),unit(12)]
        matrices = {j:atoms[COLORS[j]] for j in nontriple}
        matrices.update(zip(sorted(triple)+[40,41],special))
        assert set(matrices) == set(range(42))
        assert all(rank(N)==1 and multiply(N,N)==N for N in matrices.values())
        T = add(*(matrices[j] for j in sorted(triple)+[40,41]))
        Q = add(IDENTITY,T)
        assert rank(Q) == requested_rank
        for b in all_bases:
            assert add(*(matrices[j] for j in set(b['calls'])-triple)) == Q
        row_span = rank([row for j in nontriple for row in matrices[j]])
        column_span = rank([row for j in nontriple for row in transpose(matrices[j])])
        assert row_span + column_span + rank(Q) <= 36
        assert min(row_span,column_span) < W
        commuting = all(multiply(A,B)==multiply(B,A)
                        for A in matrices.values() for B in matrices.values())
        assert commuting == (requested_rank != 11)
        output.append(dict(rank_Q=rank(Q), rank_T=rank(T),
                           nontriple_row_span=row_span, nontriple_column_span=column_span,
                           commuting=commuting, matrices=[list(matrices[j]) for j in range(42)],
                           status='Shared equations satisfied; full-word span condition fails.'))
    return output


def audit():
    calls, triple, nontriple, bases, all_bases = decomposition_data()
    killing_character = (0,0,1,0,0,1)
    target = [6,0,0,0,6,0,0,0,6]
    assert previous.exponent(killing_character,target) == 2
    assert all(previous.exponent(killing_character,calls[j]['B'])==0 for j in triple)
    triple_lines = [v for v in previous.source.lines() if sum(x*x for x in v)==3]
    for v in triple_lines:
        for amplitude in range(-4,5):
            B = previous.source.matrix(v,amplitude)
            assert previous.exponent(killing_character,B)==0
            for b in bases:
                assert previous.exponent(b['character'],B)==2*(amplitude%2)
        # All integer amplitudes are covered: increasing by 2 changes B
        # by a multiple of 4 in every entry.
        assert all((x-y)%4==0 for x,y in zip(previous.source.matrix(v,3),
                                            previous.source.matrix(v,1)))
    controls = shared_system_controls(triple,nontriple,all_bases)
    # Consequence of the written quotient-space/Sylvester lemma:
    # 4(c+d-2r) <= 12(12-r), hence c+d+r <= 36.
    # A uniform word requires c=d=16, so r<=4 and rank(T)>=12.
    maximum_Q_rank = 36-2*W
    minimum_T_rank = W-maximum_Q_rank
    minimum_odd_additions = minimum_T_rank-len(triple)
    assert (maximum_Q_rank,minimum_T_rank,minimum_odd_additions)==(4,12,8)
    assert 40+minimum_odd_additions == 3*W
    return dict(
        status='Excluded: the fixed 40-call inventory cannot gain a positive rank-one saving by adding only signed-triple calls with integer amplitudes. No new supplier or kappa.',
        W=W, nontriple_calls=nontriple, original_triple_calls=sorted(triple),
        balanced_decompositions=bases, incidence_multiplicity=4,
        killing_character=list(killing_character),
        rank_inequality='nontriple_row_span + nontriple_column_span + rank(Q) <= 36',
        required_row_and_column_spans=[16,16], maximum_Q_rank=maximum_Q_rank,
        minimum_T_rank=minimum_T_rank, minimum_added_odd_triple_calls=minimum_odd_additions,
        minimum_total_calls=48,
        shared_system_controls=controls,
        interpretation='The shared equations alone are feasible, including a noncommuting rank-11 example. The necessary full input/output spans make them impossible at the proposed budget.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    result = audit()
    path = ROOT/'certificate.json'
    if args.write:
        path.write_text(json.dumps(result,indent=2)+'\n')
    else:
        assert json.loads(path.read_text())==result,'certificate drift'
    print(json.dumps({k:result[k] for k in ('status','maximum_Q_rank',
                    'minimum_T_rank','minimum_added_odd_triple_calls','minimum_total_calls')},indent=2))
