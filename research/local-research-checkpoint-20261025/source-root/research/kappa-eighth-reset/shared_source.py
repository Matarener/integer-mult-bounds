#!/usr/bin/env python3
"""Exact scoped screens for source caches and one encoded source pair.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
This rejects two templates; it does not construct a recursive supplier.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('source_reprice', HERE/'reprice.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
H = R.H


def add(A, B, scale=1):
    return [[x+scale*y for x, y in zip(a, b)] for a, b in zip(A, B)]


def audit():
    C, G, vectors, form, projectors = R.folded_geometry()
    # Re-establish, rather than merely read, the rational support capacities.
    spans = R.span_capacities(vectors)
    caps = [0, 1, 2, 4, 6, 10, 16]
    # Maximum sum of support bounds with exactly K nonempty channels and L
    # total span ranks. Overlap is ignored, making this a favorable bound.
    cover = {(0, 0): 0}
    for k in range(1, 17):
        for loss in range(k, 17):
            possible = [cover[k-1, loss-t]+caps[t] for t in range(1, 7)
                        if (k-1, loss-t) in cover]
            if possible:
                cover[k, loss] = max(possible)

    def lower_loss(n, rank):
        if not n:
            return 0
        return min(loss for (k, loss), capacity in cover.items()
                   if k >= rank and capacity >= n)

    columns = [sum(C[i][j] << i for i in range(16)) for j in range(16)]
    assert len(set(columns)) == 16 and all(columns)
    cached_cases = Counter()
    cached_minima = {k: 100 for k in range(17)}
    floors = {(n, r): lower_loss(n, r) for n in range(17)
              for r in range(7) if (n == r == 0) or (0 < r <= min(n, 6))}
    for remaining in range(1 << 16):
        ids = [i for i in range(16) if (remaining >> i) & 1]
        rank = H.binary_rank([columns[i] for i in ids])
        cached = 16-len(ids)
        loss = floors[len(ids), rank]
        cached_cases[cached, rank, loss] += 1
        cached_minima[cached] = min(cached_minima[cached], cached+loss)
    assert sum(cached_cases.values()) == 65536
    assert min(cached_minima.values()) == 11

    # A single row addition z_i=x_i+x_j changes scalar column j to C_j+C_i.
    # The 15 unchanged address labels must still occur in some channel.
    # Any rank-t channel contains at most caps[t] of those labels, even if
    # it also contains the newly chosen label. Six channels are necessary.
    at_nine = max(capacity for (k, loss), capacity in cover.items()
                  if k >= 6 and loss <= 9)
    assert at_nine == 11 < 15
    assert lower_loss(15, 6) == 10
    I = [[int(i == j) for j in range(6)] for i in range(6)]
    checked = 0
    path_histograms = Counter()
    for i in range(16):
        for j in range(16):
            if i == j:
                continue
            changed = columns.copy()
            changed[j] ^= changed[i]
            assert all(changed) and H.binary_rank(changed) == 6
            # Replay central-plus-side output on all independent input bits.
            encoded = [1 << q for q in range(16)]
            encoded[i] ^= encoded[j]
            for t in range(16):
                central = 0
                side = 0
                for q in range(16):
                    if (changed[q] >> t) & 1:
                        central ^= encoded[q]
                    if C[t][q] ^ int(t == q):
                        side ^= 1 << q
                assert central ^ side == 1 << t
            # Both sources meet at the rank-two projector onto their span.
            U = [vectors[i], vectors[j]]
            Ut = list(map(list, zip(*U)))
            gram = H.mm(H.mm(U, form), Ut)
            M = H.mm(H.mm(H.mm(Ut, R.inverse(gram)), U), form)
            assert H.rank(M) == 2 and H.mm(M, M) == M
            Pi, Pj = projectors[i], projectors[j]
            assert H.mm(M, Pi) == Pi and H.mm(M, Pj) == Pj
            # Concrete new line Pj. A different rank-one line within M has
            # the same path lower bound. Both sources restore at full I.
            widths = (H.rank(add(M, Pi, -1)),
                      H.rank(add(Pj, M, -1)),
                      H.rank(add(I, Pj, -1)),
                      H.rank(add(M, Pj, -1)),
                      H.rank(add(I, M, -1)))
            assert widths == (1, 1, 5, 1, 4)
            assert sum(widths)-2*(6-1) == 2
            # Inverse row addition at full frame restores both arbitrary
            # original source values; no clean-source hypothesis.
            encoded[i] ^= encoded[j]
            assert encoded == [1 << q for q in range(16)]
            path_histograms[widths] += 1
            checked += 1
    assert checked == 240
    pair_full_span = R.B.ideal_budget(6, 1, Q(1, 256), Q(6, 16), Q(10, 96))
    assert pair_full_span['moment_interval'][0] > 1
    # The first dependent scalar column sets have size four. They admit
    # z_i=x_i+x_p for the other three indices, making column p disappear.
    assert all(H.binary_rank([columns[i] for i in ids]) == len(ids)
               for size in (2, 3) for ids in combinations(range(16), size))
    quartets = []
    for ids in combinations(range(16), 4):
        if H.binary_rank([columns[i] for i in ids]) == 4:
            continue
        assert H.binary_rank([columns[i] for i in ids]) == 3
        assert H.rank([vectors[i] for i in ids]) == 3
        U = [vectors[i] for i in ids[:3]]
        Ut = list(map(list, zip(*U)))
        gram = H.mm(H.mm(U, form), Ut)
        M = H.mm(H.mm(H.mm(Ut, R.inverse(gram)), U), form)
        assert H.rank(M) == 3 and H.mm(M, M) == M
        assert all(H.mm(M, projectors[i]) == projectors[i] for i in ids)
        rest = [i for i in range(16) if i not in ids]
        assert H.binary_rank([columns[i] for i in rest]) == 6
        for pivot in ids:
            changed = columns.copy()
            encoded = [1 << q for q in range(16)]
            for i in ids:
                if i != pivot:
                    changed[pivot] ^= columns[i]
                    encoded[i] ^= encoded[pivot]
            assert changed[pivot] == 0
            assert sum(bool(c) for c in changed) == 15
            for t in range(16):
                central = side = 0
                for q in range(16):
                    if (changed[q] >> t) & 1:
                        central ^= encoded[q]
                    if C[t][q] ^ int(t == q):
                        side ^= 1 << q
                assert central ^ side == 1 << t
            for i in ids:
                # All four sources can finish at I along monotone paths.
                assert H.rank(add(M, projectors[i], -1)) == 2
            assert H.rank(add(I, M, -1)) == 3
            for i in ids:
                if i != pivot:
                    encoded[i] ^= encoded[pivot]
            assert encoded == [1 << q for q in range(16)]
        quartets.append(list(ids))
    assert len(quartets) == 60
    # The untouched twelve columns alone require six channels and loss>=10.
    old_floor = lower_loss(12, 6)
    assert old_floor == 10
    dimension_bounds = []
    for dims in product(range(4), repeat=3):
        # Grant one dependent copy per encoded stream, lowered to dimension
        # t and reused freely. No return cost is charged on an erased copy.
        copy_loss = sum(3-t for t in dims)
        if min(dims) > 0:
            # Rank-three encoded column block forces three distinct factor
            # rows containing respective encoded inputs (a nonzero minor).
            # These cost at least sum(dims); >=6 nonzero rows cost >=1 each.
            center_floor = max(old_floor, 3+sum(dims))
        else:
            # Zero-frame copies can broadcast directly. The old twelve
            # inputs still require loss >=10; do not charge zero channels.
            center_floor = old_floor
        total = copy_loss+center_floor
        assert total >= 12
        dimension_bounds.append(dict(dimensions=list(dims), copy_loss=copy_loss,
                                     center_loss_lower_bound=center_floor,
                                     combined_loss_lower_bound=total))
    sources = [HERE/'shared_source.py', HERE/'reprice.py',
               HERE.parent/'higher-rank-sixteenth/screen.py',
               HERE.parent/'shared-core-blocks/audit.py']
    return dict(
        status='Static caches and the two bounded recodings rejected; no new supplier or kappa.',
        target='1/256',
        capacities=caps,
        cache=dict(subsets_checked=65536,
                   minimum_total_loss_by_cached_count=cached_minima,
                   combined_loss_lower_bound=11, rank_deficit_upper_bound=-1,
                   interpretation='Static source copies are already allowed by the previous overcomplete-factor screen.'),
        one_pair=dict(ordered_pairs_checked=checked,
                      unchanged_labels=15, scalar_rank=6,
                      maximum_unchanged_coverage_at_loss_nine=at_nine,
                      center_loss_lower_bound=10, extra_source_rank=2,
                      direct_line_combined_loss_lower_bound=12,
                      copied_line_combined_loss_lower_bound=11,
                      full_span_loss_lower_bound=10,
                      full_span_optimistic_budget=H.encode(pair_full_span),
                      concrete_source_path_histogram=[dict(widths=list(k), count=v)
                                                       for k, v in path_histograms.items()],
                      interpretation='One pair mixes at its rank-two span, one encoded stream contracts to a line, and inverse mixing restores sources at the full frame.'),
        quartet=dict(minimum_scalar_dependency_size=4, circuits=quartets,
                     circuits_checked=60, pivot_choices_checked=240,
                     rational_span_dimension=3, unchanged_scalar_rank=6,
                     unchanged_input_loss_lower_bound=old_floor,
                     copied_dimension_cases=dimension_bounds,
                     combined_loss_lower_bound=12, rank_deficit_upper_bound=-4),
        scope='Folded-five-cube labels and retained shared-cover ledger. Static source caches, one pair recoding (full-span case uses zero gauges), or one dependency quartet with separately lowered encoded copies, followed by a conservative producer. No exclusion of arbitrary encoded interfaces, joint array transformations, or several interacting recoding blocks.',
        source_sha256={str(p.relative_to(HERE.parents[1])):
                       hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    # JSON normalizes integer dictionary keys for reproducible comparisons.
    result = json.loads(json.dumps(result))
    dest = HERE/'shared-source.json'
    if args.write:
        dest.write_text(json.dumps(result, indent=2)+'\n')
    else:
        assert json.loads(dest.read_text()) == result, 'certificate drift'
    print(json.dumps(dict(status=result['status'],
                         cache_loss=result['cache']['combined_loss_lower_bound'],
                         encoded_pair_copied_line_loss=result['one_pair']['copied_line_combined_loss_lower_bound'],
                         quartet_loss=result['quartet']['combined_loss_lower_bound']), indent=2))
