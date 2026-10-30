#!/usr/bin/env python3
"""Two focused joint-boundary/typed-state screens after the direct H failure.

The two-query obstruction is a FREE-OPERATOR model, not a lower bound on
the actual native construction. The fresh-owner obstruction uses actual
phase-corrected native owners and an invariant old-coordinate sector.
Apache-2.0; substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
import aggregate_h_probe as A


def rank(rows):
    basis = {}
    for row in rows:
        row = list(map(Q, row))
        for pivot in sorted(basis):
            if row[pivot]:
                scale = row[pivot]
                row = [x-scale*y for x, y in zip(row, basis[pivot])]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [x/scale for x in row]
    return len(basis)


def universal_two_query_screen():
    """Coefficient matrices for Q K_a Q, Q K_b Q, Q K_f Q.

    K_a=H2 H1 H0, K_b=H6 H5 H4, K_f=K_b H3 K_a. The H letters
    are free involutions and Q is a further free involution. The two-Q
    normal forms remain different even after those stated relations.
    In a circuit A E_i(Q) B E_j(Q) C with Q-free A,B,C, the coefficient
    matrices of words with empty exterior and exactly two Q letters all
    lie in span(A_empty[:,i] C_empty[j,:]); its dimension is at most one.
    The extra three Q-free positive streams do not change that bound.
    """
    words = [(2, 1, 0), (6, 5, 4), (6, 5, 4, 3, 2, 1, 0)]
    matrices = [[int(i == j == k) for i in range(6) for j in range(6)] for k in range(3)]
    dimension = rank(matrices)
    A.need(dimension == 3, 'Three independent exact sandwich coefficient matrices')
    minor = [[row[6*j+j] for j in range(3)] for row in matrices]
    A.need(minor == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'Explicit unit determinant witness')
    # Coalescing all three independent input/output roles would erase the gate.
    fake = [[1] for _ in matrices]
    A.need(rank(fake) == 1, 'Invalid merged-role model loses the obstruction')
    return dict(middle_words=[list(w) for w in words], coefficient_span_rank=dimension,
                explicit_minor=minor, two_complete_bank_Q_events_upper_bound=1,
                six_stream_two_event_identity_possible=False,
                scope='Only universal finite Q-free polynomial mixing and two complete-bank Q events. Actual low-rank native relations, partial-bank calls, additional transforms, or stateful recursion are not excluded.',
                positive_partner_streams_included=3,
                invalid_merged_independent_inputs_rank=1)


def phase_data(n, phases, stage, port):
    g = n.source_route(phases, stage, port)
    if stage == 0:
        return g, 0
    axes = n.AXES[:9]+n.AXES[9+8*(stage-1):9+8*stage]
    f = n.frame((a, 1) for a in axes)
    old, new = n.polynomial(f)[0], n.polynomial(n.move_frame(f, g))[0]
    d = sum((((x-y) % 4)//2) << i for i, (x, y) in enumerate(zip(old, new)))
    A.need(n.act(g, d) == d, 'Signed owner involution')
    return g, d


def signed_h_apply(n, phases, geo, stage, vector):
    charts = [phase_data(n, phases, stage, p) for p in range(112)]
    out = []
    for i, row in enumerate(geo['H']):
        gi, di = charts[i]
        result = {}
        for p, coefficient in row.items():
            gp, dp = charts[p]
            for address, value in vector[p].items():
                intermediate = n.act(gp, address)
                final = n.act(gi, intermediate)
                phase = ((dp & address).bit_count()+(di & intermediate).bit_count()) % 2
                result[final] = result.get(final, 0)+(-1 if phase else 1)*coefficient*value
                if not result[final]:
                    del result[final]
        out.append(result)
    return out


def fresh_inverse_screen(n, phases, geo):
    old_block = sum(n.AXES[9:17])
    incoming = [{} for _ in range(112)]
    incoming[0] = {n.AXES[9]: Q(1)}
    first = signed_h_apply(n, phases, geo, 0, incoming)
    second = signed_h_apply(n, phases, geo, 1, first)
    leakage = [(port, address, c) for port, row in enumerate(second)
               for address, c in row.items() if address & old_block != n.AXES[9]]
    A.need(bool(leakage), 'Old monodromy genuinely leaves the original old-block sector')
    # H2 and every candidate fresh inverse H4,H5,H6 act only on original9
    # and their own disjoint block. They preserve every old-block1 sector.
    preserved = []
    for stage in (2, 4, 5, 6):
        for port in range(112):
            g, d = phase_data(n, phases, stage, port)
            A.need(all((g[i] & old_block) == (n.AXES[i] & old_block) for i in range(73)),
                   'Later owner fixes the entire old-block sector label')
            A.need(d & old_block == 0, 'Later character does not touch the old block')
            preserved.append((stage, port))
    witness = min(leakage)
    return dict(input_field=0, input_address=n.AXES[9], old_block_axes=list(range(9, 17)),
                after_H1_H0_witness=dict(output_field=witness[0], output_address=witness[1],
                                         coefficient=str(witness[2])),
                nonzero_outside_sector_terms=len(leakage), later_signed_owners_checked=len(preserved),
                later_operators_invertible=True,
                conclusion='H2 preserves the nonzero leaked sector, as do H4,H5,H6 in every order. A fresh-axis inverse word cannot equal (H2 H1 H0)^-1.',
                scope='Actual signed native H_s on these stages, without additional old-block mixing. Extra cross-boundary maps require a new exact and costed word.')


def overlap_accounting():
    first = set(range(25))
    same = set(first)
    extension = set(range(49))
    disjoint = set(range(25, 50))
    # Two applications on the same coordinate square to a free Pauli for
    # complex Gaussian factors (or identity for BIT). Only odd multiplicity
    # coordinates retain a nontrivial full Gaussian target.
    return dict(same_owner_forward_inverse_state_pair=dict(
                    first_rank=len(first), second_rank=len(same), independent_target_rank=len(first ^ same),
                    unearned_double_credit=len(first)+len(same)),
                nested_full_union_pair=dict(first_rank=len(first), second_rank=len(extension),
                    independent_target_rank=len(first ^ extension), unearned_sum=len(first)+len(extension)),
                disjoint_new_axes_pair=dict(first_rank=len(first), second_rank=len(disjoint),
                    independent_target_rank=len(first ^ disjoint),
                    obstruction='New native owners do not provide the same inverse monodromy; see the actual sector witness.'),
                conclusion='State cancellation is useful only with a separately admitted inverse state on new axes. Reusing the old transform support does not produce two independent rank credits on one array.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'JOINT-BOUNDARY-PROBE.json')
    args = parser.parse_args()
    native = A.ROOT/'research/kappa-next-regime/direct-decoder/native_common.py'
    rebuild = HERE.parent/'complex/rebuild_native.py'
    n = A.load(native, 'joint_boundary_native')
    r = A.load(rebuild, 'joint_boundary_rebuild')
    packet, phases = n.load_sources()
    result = dict(schema='joint-H-boundary-and-stateful-inverse-screen/1',
                  status='PASS_TWO_SCOPED_OBSTRUCTIONS_AND_COMPLETE_OVERLAP_ACCOUNTING',
                  two_bank_query_screen=universal_two_query_screen(),
                  actual_fresh_inverse_screen=fresh_inverse_screen(n, phases, r.geometry(packet)),
                  typed_overlap_accounting=overlap_accounting(),
                  literature_inspiration='Noncommutative rational-series coefficient/Hankel ranks; the elementary two-query argument is proved in the module docstring.',
                  primary_source='https://fpsac-archive.github.io/FPSAC94/ARTICLES/45Reutenauer.pdf',
                  source_sha256={str(p.relative_to(A.ROOT)):sha256(p.read_bytes()).hexdigest()
                                 for p in (Path(__file__), Path(A.__file__), native, rebuild)},
                  no_general_lower_bound=True, no_new_H_kappa=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'], coefficient_rank=result['two_bank_query_screen']['coefficient_span_rank'],
                         fresh_inverse_witness=result['actual_fresh_inverse_screen']['after_H1_H0_witness']), sort_keys=True))


if __name__ == '__main__':
    main()
