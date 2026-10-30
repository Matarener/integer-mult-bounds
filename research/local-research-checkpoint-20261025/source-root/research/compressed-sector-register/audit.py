#!/usr/bin/env python3
"""Exact compressed-sector rejection certificates. Apache-2.0.

Douglas Colkitt, with OpenAI Codex assistance. No external dependencies.
Verifies finite premises of the order-independent lemma in REPORT.md.
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


def compressed_witness(calls, W):
    result = previous.screen(calls, W)
    bases = [set(b['calls']) for b in result['saturated_bases']]
    if not bases:
        return None
    common = set.intersection(*bases)
    if not common:
        return None
    covered = set.union(*bases)
    # Every member of covered-common annihilates the common sector on both sides.
    exposed = set(range(len(calls))) - (covered - common)
    for q in previous.source.characters():
        residues = {j: previous.exponent(q, calls[j]['B']) for j in exposed}
        if all(b % 2 == 0 for b in residues.values()):
            active = [j for j, b in sorted(residues.items()) if b == 2]
            if len(active) < len(common):
                return dict(
                    bases=result['saturated_bases'], sector_calls=sorted(common),
                    sector_dimension=len(common), exposed_calls=sorted(exposed),
                    character=list(q), active_even_calls=active,
                    compressed_rank_upper_bound=len(active))
    return None


def verify(calls, W, witness):
    """Check a supplied witness without running the witness search."""
    sector = set(witness['sector_calls'])
    assert sector and witness['sector_dimension'] == len(sector)
    assert witness['bases']
    covered = set()
    for record in witness['bases']:
        q = record['character']
        assert sum(q[:3]) % 2 == 1
        residues = [previous.exponent(q, c['B']) for c in calls]
        assert all(b % 2 == 0 for b in residues)
        selected = {j for j, b in enumerate(residues) if b == 2}
        assert selected == set(record['calls']) and len(selected) == W
        assert sector <= selected
        covered |= selected
    exposed = set(range(len(calls))) - (covered-sector)
    assert exposed == set(witness['exposed_calls'])
    q = witness['character']
    assert sum(q[:3]) % 2 == 1
    residues = {j: previous.exponent(q, calls[j]['B']) for j in exposed}
    assert all(b % 2 == 0 for b in residues.values())
    active = {j for j, b in residues.items() if b == 2}
    assert active == set(witness['active_even_calls'])
    assert len(active) == witness['compressed_rank_upper_bound'] < len(sector)


def audit():
    base = previous.inventory()
    cases = []
    for v in previous.source.lines():
        for amplitude in (1, 2):
            calls = base + [dict(B=list(previous.source.matrix(v, a)))
                            for a in (amplitude, -amplitude)]
            witness = compressed_witness(calls, 16)
            if witness:
                verify(calls, 16, witness)
            cases.append(dict(line=list(v), amplitude=amplitude,
                              rejected=witness is not None, witness=witness))
    assert sum(c['rejected'] for c in cases) == 46
    assert all(c['rejected'] == (c['amplitude'] == 2 or sum(x*x for x in c['line']) != 3)
               for c in cases)
    counts = Counter((sum(x*x for x in c['line']), c['amplitude'], c['rejected'])
                     for c in cases)
    # Positive controls are known exact words: coordinate moves for every
    # register, with consecutive inverse calls acting on one chosen register.
    coordinate = [dict(B=list(previous.source.matrix(v, 1)))
                  for v in ((1,0,0),(0,1,0),(0,0,1)) for _ in range(16)]
    assert compressed_witness(coordinate, 16) is None
    positive_controls = []
    for v in ((1,0,0),(0,1,1),(1,1,1),(1,1,2)):
        calls = coordinate + [dict(B=list(previous.source.matrix(v, a))) for a in (1,-1)]
        assert compressed_witness(calls, 16) is None
        positive_controls.append(list(v))
    # A malformed certificate must fail the direct verifier.
    first = next(c for c in cases if c['rejected'])
    calls = base + [dict(B=list(previous.source.matrix(first['line'], a)))
                    for a in (first['amplitude'], -first['amplitude'])]
    corrupted = dict(first['witness'], compressed_rank_upper_bound=16)
    try:
        verify(calls, 16, corrupted)
    except AssertionError:
        pass
    else:
        raise AssertionError('Corrupt rank claim accepted')
    assert 42**25 * 3**2 < 48**25
    # Residual signed-triple case: each original 16-term identity is now
    # an 18-term identity with the same six distinguished summands.
    triples = {i for i,c in enumerate(base) if sum(x*x for x in c['line']) == 3}
    assert triples == {15,18,29,32}
    distinguished = triples | {40,41}
    residual = base + [dict(B=list(previous.source.matrix((1,1,1),a))) for a in (1,-1)]
    decompositions = []
    for b in previous.screen(base,16)['saturated_bases']:
        q = b['character']
        residues = [previous.exponent(q,c['B']) for c in residual]
        assert all(x%2 == 0 for x in residues)
        selected = {j for j,x in enumerate(residues) if x == 2}
        assert selected == set(b['calls']) | {40,41}
        assert distinguished <= selected and len(selected) == 18
        complement = sorted(selected-distinguished)
        assert len(complement) == 12
        decompositions.append(dict(character=q, twelve_term_calls=complement))
    assert len(decompositions) == 13
    # Diagonal sign conjugations identify the four remaining cases and
    # preserve the entire original frame multiset.
    base_counts = Counter(tuple(c['B']) for c in base)
    for c in cases:
        if not c['rejected']:
            signs = c['line']
            assert all(abs(x)==1 for x in signs)
            transformed = Counter(tuple(B[i*3+j]*signs[i]*signs[j]
                                        for i in range(3) for j in range(3))
                                  for B in (b['B'] for b in base))
            assert transformed == base_counts
    return dict(
        status='No new supplier or kappa. All tested signed-pair and unequal-coordinate opposite-pair extensions are excluded in the stated model.',
        cases=cases,
        summary=[dict(norm=n, amplitude=a, rejected=r, count=count)
                 for (n,a,r),count in sorted(counts.items())],
        tested=50, rejected=46, undecided=4,
        uniform_coordinate_control_not_rejected=True,
        uniform_inverse_pair_controls_not_rejected=positive_controls,
        corrupt_certificate_rejected=True,
        hypothetical_42_call_moment_below_one_at='2/25',
        residual_signed_triple_system=dict(distinguished_calls=sorted(distinguished),
                                          twelve_term_decompositions=decompositions,
                                          symmetry_verified=True,
                                          status='Necessary equations only; no scalar solution supplied.'))


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
    print(json.dumps({k:result[k] for k in ('status','tested','rejected','undecided')}, indent=2))
