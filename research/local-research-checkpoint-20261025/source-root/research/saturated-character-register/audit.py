#!/usr/bin/env python3
"""Exact saturated-character obstruction. Apache-2.0, Douglas Colkitt.

Checks the finite inputs to the written matrix argument in REPORT.md.
No solver, proposed scalar matrices, or chronological search is used.
"""
import argparse
from collections import Counter
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'inventory_audit', ROOT.parent / 'unequal-coordinate-register' / 'audit.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def exponent(q, B):
    return sum(x*y for x, y in zip(q, (B[0], B[4], B[8], B[1], B[2], B[5]))) % 4


def inventory():
    calls = []
    for item in source.larger_inventory()['inventory']:
        for copy in range(item['copies']):
            calls.append(dict(line=item['line'], amplitude=item['amplitude'],
                              copy=copy, B=list(source.matrix(item['line'], item['amplitude']))))
    return calls


def screen(calls, W):
    bases = {}
    classes = Counter()
    for q in source.characters():
        residues = [exponent(q, c['B']) for c in calls]
        odd = sum(b % 2 for b in residues)
        selected = tuple(j for j, b in enumerate(residues) if b == 2)
        classes[odd, len(selected)] += 1
        if odd == 0 and len(selected) == W:
            bases.setdefault(selected, q)
    neighbors = [set() for _ in calls]
    for basis in bases:
        for i in basis:
            neighbors[i].update(set(basis) - {i})
    isolated = [i for i, ns in enumerate(neighbors) if len(ns) == len(calls)-1]
    # If all other factors annihilate image(N_i), the exact word requires A_i=I.
    target = [6, 0, 0, 0, 6, 0, 0, 0, 6]
    rejected = [i for i in isolated if calls[i]['B'] != target]
    return {
        'W': W, 'calls': len(calls),
        'character_classes': [dict(odd=k, even_two=l, count=n)
                              for (k, l), n in sorted(classes.items())],
        'saturated_bases': [dict(character=list(q), calls=list(b)) for b, q in bases.items()],
        'forced_isolated_calls': isolated, 'contradictory_calls': rejected,
    }


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def sector_witnesses(calls, result):
    """Reject if every factor fixes a nonzero image(N_i) modulo t^3.

    Co-membership in a saturated basis implies N_j N_i=0. All other
    factors must have exponent 0 mod 4 for the selected character.
    """
    neighbors = [0] * len(calls)
    for basis in result['saturated_bases']:
        mask = sum(1 << i for i in basis['calls'])
        for i in basis['calls']:
            neighbors[i] |= mask ^ (1 << i)
    zero_masks = []
    for q in source.characters():
        zero_masks.append((sum(1 << j for j, c in enumerate(calls)
                               if exponent(q, c['B']) == 0), q))
    full = (1 << len(calls))-1
    witnesses = []
    for i, adjacent in enumerate(neighbors):
        uncontrolled = full ^ adjacent
        for zeros, q in zero_masks:
            if zeros & uncontrolled == uncontrolled:
                ids = [j for j in range(len(calls)) if uncontrolled >> j & 1]
                assert i in ids
                assert all(exponent(q, calls[j]['B']) == 0 for j in ids)
                witnesses.append(dict(call=i, character=list(q), uncontrolled_calls=ids))
                break
    return witnesses


def lemma_controls():
    # Exhaust all decompositions I_2=N_1+N_2 by rank-one F2 matrices.
    matrices = [r for r in itertools.product(range(4), repeat=2) if binary_rank(r) == 1]
    def mul(A, B):
        return tuple((B[0] if row & 1 else 0) ^ (B[1] if row & 2 else 0) for row in A)
    checked = 0
    for A, B in itertools.product(matrices, repeat=2):
        if tuple(a ^ b for a, b in zip(A, B)) == (1, 2):
            assert mul(A, B) == mul(B, A) == (0, 0)
            assert mul(A, A) == A and mul(B, B) == B
            checked += 1
    assert checked == 6
    return checked


def audit():
    calls = inventory()
    result = screen(calls, 16)
    assert len(result['saturated_bases']) == 13
    assert result['contradictory_calls'] == [15, 18, 29, 32]
    assert result['forced_isolated_calls'] == result['contradictory_calls']
    # Every triple call lies in every saturated basis; those bases cover all calls.
    bases = [set(b['calls']) for b in result['saturated_bases']]
    assert set.intersection(*bases) == {15, 18, 29, 32}
    assert set.union(*bases) == set(range(40))
    # Independent second-order contradiction on any isolated triple image.
    # For q=(0,0,1,0,0,1), all four triple exponents are zero mod four,
    # whereas the target is 2. Other factors act as identity on that image.
    q = (0, 0, 1, 0, 0, 1)
    assert exponent(q, [6, 0, 0, 0, 6, 0, 0, 0, 6]) == 2
    assert all(exponent(q, calls[i]['B']) == 0 for i in result['contradictory_calls'])
    # Repeated copies do not repair the equality trap.
    doubled = screen(calls + calls, 32)
    assert doubled['contradictory_calls'] == [15, 18, 29, 32, 55, 58, 69, 72]
    # The usual three moves per register is a valid uniform word, and is not rejected.
    positive = [dict(B=list(source.matrix(v, 1))) for v in ((1,0,0),(0,1,0),(0,0,1))
                for _ in range(16)]
    control = screen(positive, 16)
    assert not control['contradictory_calls']
    assert len(control['saturated_bases']) == 3
    assert not sector_witnesses(positive, control)
    # A bounded escape test: insert opposite rank-one moves on each of the
    # 25 lines, at amplitudes 1 and 2. They preserve sum A=16I, but have
    # unspecified locations and scalar idempotents. Passing is NOT existence.
    extensions = []
    for v in source.lines():
        for amplitude in (1, 2):
            extended = calls + [dict(B=list(source.matrix(v, a)))
                                for a in (amplitude, -amplitude)]
            tested = screen(extended, 16)
            witnesses = sector_witnesses(extended, tested)
            extensions.append(dict(line=list(v), amplitude=amplitude,
                                   saturated_bases=len(tested['saturated_bases']),
                                   rejected=bool(witnesses), witness=witnesses[:1]))
    assert sum(e['rejected'] for e in extensions) == 28
    assert all(e['rejected'] == (e['amplitude'] == 2 or sum(x*x for x in e['line']) == 1)
               for e in extensions)
    assert 42**25 * 3**2 < 48**25
    result.update(
        status='Excluded inventory, all orders and rank-one scalar idempotents in the stated common-target abelian model. No new supplier or kappa.',
        inventory=calls,
        isolated_sector_contradiction_character=list(q),
        repeated_inventory_contradictory_calls=doubled['contradictory_calls'],
        coordinate_positive_control={'W':16, 'calls':48, 'rejected':False, 'saturated_bases':3},
        exhaustive_two_dimensional_basis_decompositions=lemma_controls(),
        opposite_pair_extensions=extensions,
        extension_summary={'tested':50, 'rejected':28, 'not_rejected':22,
                           'rank_one_calls':42, 'hypothetical_moment_below_one_at':'2/25',
                           'status':'No scalar matrices or schedule supplied for any extension.'},
    )
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    path = ROOT / 'certificate.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2)+'\n')
    else:
        assert json.loads(path.read_text()) == result, 'certificate drift'
    print(json.dumps({k:result[k] for k in ('status', 'W', 'calls', 'forced_isolated_calls',
                                           'exhaustive_two_dimensional_basis_decompositions')}, indent=2))
