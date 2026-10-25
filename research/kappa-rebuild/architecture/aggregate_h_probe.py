#!/usr/bin/env python3
"""Exact scoped probes of the p3 H endpoint, phases and dyadic completions.

This is not a closed H supplier.  It separates the noncommuting six-bank
controller identity from physical per-port head operators and from native
whole-word adapter admission.  Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE.parent/'bit')]
import complex_controller_factor as C
import controller_tariff as T
import mixed_forest_search as F
import mixed_target_probe as E


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def need(ok, label):
    if not ok:
        raise AssertionError(label)


def plus(a, b, c=1):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0)+c*value
        if not out[key]:
            del out[key]
    return out


def prepend(poly, stage):
    return {(stage,)+word: value for word, value in poly.items()}


def nc_controller():
    """Replay the SAME p3 physical role program over the free associative ring.

    T_s is an arbitrary stage multiplier and is NOT assumed invertible,
    commuting with another T, or order two. Q has already been removed from
    the local shears by the separately stated two-sector gauge. The result
    therefore cannot by itself remove a physical per-port Q boundary.
    """
    coefficients, events, _ = C.controller(3, 43)
    factored = C.factor(coefficients)
    matrix = [[{(): 1} if i == j else {} for j in range(6)] for i in range(6)]
    for event in events:
        kind = event[0]
        if kind == 'LOCAL':
            _, stage, pair, backward = event
            x, y = 2*pair, 2*pair+1
            dst, src, sign = (x, y, -1) if backward else (y, x, 1)
            matrix[dst] = [plus(a, b, sign) for a, b in zip(matrix[dst], matrix[src])]
            for role in (x, y):
                matrix[role] = [prepend(poly, stage) for poly in matrix[role]]
        elif kind == 'IDLE':
            _, pair, stages = event
            for stage in stages:
                for role in (2*pair, 2*pair+1):
                    matrix[role] = [prepend(poly, stage) for poly in matrix[role]]
        elif kind == 'ADD':
            _, dst, src, sign = event
            matrix[dst] = [plus(a, b, sign) for a, b in zip(matrix[dst], matrix[src])]
        else:
            need(kind == 'SIGNED_SWAP', 'Known role event')
            _, a, b = event
            matrix[a], matrix[b] = matrix[b], [{w: -v for w, v in p.items()} for p in matrix[a]]

    def scalar_left(a, b):
        return [[sum_polys((b[k][j], a[i][k]) for k in range(6))
                 for j in range(6)] for i in range(6)]

    def scalar_right(a, b):
        return [[sum_polys((a[i][k], b[k][j]) for k in range(6))
                 for j in range(6)] for i in range(6)]

    out = scalar_right(scalar_left(factored['left'], matrix), factored['right'])
    words = [tuple(s for s in reversed(range(7)) if term[s+1]) for term in factored['diagonal']]
    expected = [[{words[i]: Q(1)} if i == j else {} for j in range(6)] for i in range(6)]
    need(out == expected, 'All free noncommuting coefficients match the six interval endpoints')
    wrong = [list(row) for row in expected]
    wrong[0] = list(wrong[0]); wrong[0][0] = {tuple(reversed(words[0])): Q(1)}
    need(wrong != out, 'Reversing a noncommuting interval is rejected')
    return dict(diagonal_words=[list(word) for word in words],
                all_36_free_polynomial_entries_checked=True,
                no_relations_between_stage_multipliers=True,
                left=C.serialize_matrix(factored['left']), right=C.serialize_matrix(factored['right']),
                boundary_warning='The physical Q gauges remain on opposite sides of each of three interval products.',
                wrong_stage_order_rejected=True)


def sum_polys(terms):
    out = {}
    for poly, coefficient in terms:
        if coefficient:
            out = plus(out, poly, coefficient)
    return out


def phase_lifts(n, phases):
    records = []
    bare_failures = 0
    # A degree-at-most-two Z4 phase is determined by these evaluations.
    # Outside the seventeen active coordinates every map fixes the coordinate.
    for stage in range(1, 9):
        axes = n.AXES[:9]+n.AXES[9+8*(stage-1):9+8*stage]
        support = sum(axes)
        old = (1 << 9)-1
        fresh = support ^ old
        tests = [0]+list(axes)+[a ^ b for j, a in enumerate(axes) for b in axes[j+1:]]
        full = n.frame((a, 1) for a in axes)
        for port, recipe in enumerate(phases['recipes']):
            g = n.source_route(phases, stage, port)
            need(n.product(g, g) == n.AXES, 'Native owner map is involutive')
            q = recipe['q']
            wanted = n.polynomial(full)
            moved = n.polynomial(n.move_frame(full, g))
            need(wanted[1] == moved[1], 'Full tensor polar form is preserved')
            delta = [(a-b) % 4 for a, b in zip(wanted[0], moved[0])]
            need(all(v in (0, 2) for v in delta), 'Only even linear phase defect')
            d = sum((v//2) << i for i, v in enumerate(delta))
            need(d != 0, 'Bare G has an actual absolute phase defect')
            bare_failures += 1
            need(d.bit_count() in (4, 8) and d.bit_count() % 4 == 0, 'Zero global Pauli phase')
            need(n.act(g, d) == d, 'Signed monomial squares to identity')
            need((d & q).bit_count() % 2 == 0, 'Signed monomial preserves each port q')

            def transform(y):
                # In Fourier coordinates Z_d G is the affine map y -> G(y+d).
                return n.act(g, y ^ d)

            for y in tests:
                z = transform(y)
                need((z & support).bit_count() % 4 == (y & support).bit_count() % 4,
                     'Exact full Gaussian phase under signed monomial')
                need((z & q).bit_count() % 2 == (y & q).bit_count() % 2,
                     'Exact per-port q Gaussian phase')
                need(((z & old).bit_count()+(z & q).bit_count() % 2) % 4 ==
                     (1+(y & fresh).bit_count()) % 4,
                     'Old hole F9*Cq maps to i times the common fresh8 Gaussian')
            records.append(dict(stage=stage, port=port, q=q, character_mask=d,
                                character_weight=d.bit_count(), owner_columns=list(g),
                                Fourier_affine_order='G(y+d)', physical_operator='Z_d G',
                                full_tensor_global_phase_Z4=0, old_hole_to_fresh_global_phase_Z4=1))
    return dict(records=records, checked_owner_lifts=len(records),
                bare_owner_absolute_phase_failures=bare_failures,
                bare_owner_is_not_made_commuting_by_a_physical_translation=True,
                evidence='Complete quadratic phase evaluations; all other coordinates fixed.',
                tensor_lift='Each displayed affine Fourier substitution lifts column by column; the constant i becomes i^f.',
                scope='The signed monomial is proved. Replacing the native whole-word contacts by it remains a separate integration task.')


def h_lambda(geo, value):
    out = [dict(row) for row in geo['J']]
    for k, a in enumerate(geo['selected']):
        for p, coefficient in {a: Q(1), **geo['L'][k]}.items():
            out[a][p] = out[a].get(p, 0)+(13+value)*coefficient
            if not out[a][p]:
                del out[a][p]
    return out


def sparse_matrix_product(a, b):
    out = []
    for row in a:
        new = {}
        for k, coefficient in row.items():
            new = plus(new, b[k], coefficient)
        out.append(new)
    return out


def mapped_kernel(n, phases, matrix, stage):
    routes = [n.source_route(phases, stage, p) for p in range(112)]
    return [{(p, n.product(routes[i], routes[p])): c for p, c in row.items()}
            for i, row in enumerate(matrix)]


def apply_mapped(n, matrix, vector):
    out = []
    for row in matrix:
        new = {}
        for (p, route), coefficient in row.items():
            for address, value in vector[p].items():
                at = n.act(route, address)
                new[at] = new.get(at, 0)+coefficient*value
                if not new[at]:
                    del new[at]
        out.append(new)
    return out


def dyadic_family(n, geo, phases):
    values = (Q(-1, 2), Q(1), Q(-2))
    matrices = [h_lambda(geo, value) for value in values]
    identity = [{i: Q(1)} for i in range(112)]
    actual = sparse_matrix_product(matrices[2], sparse_matrix_product(matrices[1], matrices[0]))
    need(actual == identity, 'Three dyadic completions multiply to identity in one chart')
    need(h_lambda(geo, Q(-1)) == geo['H'], 'Original involution is the lambda=-1 member')
    # A real physical column catches replacing distinct stage owners by one chart.
    basis = [{} for _ in range(112)]
    basis[0] = {n.AXES[9]: Q(1)}
    vector = basis
    for stage, matrix in enumerate(matrices):
        vector = apply_mapped(n, mapped_kernel(n, phases, matrix, stage), vector)
    need(vector != basis, 'Same-chart lambda cancellation is not valid across actual stage owners')
    witness = None
    for port in range(112):
        delta = plus(vector[port], basis[port], -1)
        if delta:
            at = min(delta)
            witness = dict(input_field=0, input_address=n.AXES[9], output_field=port,
                           output_address=at, difference=str(delta[at]))
            break
    return dict(formula='H_lambda=J+(13+lambda) E_A [L,I]',
                low_rank_form='H_lambda=I+[-K;(12+lambda)I] [L,I]',
                inverse='I-lambda^-1 [-K;(12+lambda)I] [L,I]',
                permitted_parameter='Any nonzero signed power of two keeps both lambda and lambda^-1 dyadic.',
                same_chart_product={'chronological_lambda':[str(v) for v in values], 'exact_identity':True},
                actual_different_owner_negative_control=witness,
                recursive_profile_if_natively_replayed='The same eight rank-one selected-row completions; scalar coefficients change.',
                native_lambda_word_replayed=False)


def funding():
    windows, targets, _ = T.geometry(3, 43)
    case = F.verify(3, 6, T.simple_p3(), 'H', custom_windows=windows, custom_targets=targets)
    output = F.serialize(case, ('0.001745', '0.0023', '0.004', '0.006'))
    repaired = Counter(case['signed']); repaired[1] -= 3*224
    output['direct_three_head_conjugations'] = dict(paid_H1=3*224,
        rank_margin=str(sum(r*c for r, c in repaired.items())),
        moment_at_004=E.show(E.moment(repaired, Q('0.004'))),
        warning='This is only the direct implementation, not a lower bound on a new coupled boundary algorithm.')
    hypothetical = Counter(case['signed']); hypothetical[1] -= 224
    output['unproved_single_shared_head_conjugation'] = dict(paid_H1=224,
        moment_at_004=E.show(E.moment(hypothetical, Q('0.004'))),
        established=False, obligation='A new identity must couple the three independent negative-bank endpoint jobs.')
    return output


def run():
    native_path = ROOT/'research/kappa-next-regime/direct-decoder/native_common.py'
    rebuild_path = HERE.parent/'complex/rebuild_native.py'
    n = load(native_path, 'architecture_aggregate_native')
    r = load(rebuild_path, 'architecture_aggregate_h')
    packet, phases = n.load_sources()
    geo = r.geometry(packet)
    out = dict(schema='aggregate-H-independent-phase-and-controller-probes/1',
               status='PASS_SCOPED_IDENTITIES_AND_EXPLICIT_DIRECT_CLOSURE_OBSTRUCTION',
               noncommuting_p3=nc_controller(), phase_lifts=phase_lifts(n, phases),
               dyadic_completion_family=dyadic_family(n, geo, phases), conditional_funding=funding(),
               source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()
                              for p in (Path(__file__), native_path, rebuild_path,
                                        HERE/'controller_tariff.py', HERE/'mixed_forest_search.py',
                                        HERE.parent/'bit/complex_controller_factor.py')},
               native_source_pins=n.PINS,
               no_new_H_kappa=True,
               missing=['Actual whole-word signed-owner wrappers',
                        'A coupled boundary identity costing at most the complete conditional budget',
                        'Arbitrary-input restoration and output independence for any new logger/catalyst'])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'AGGREGATE-H-PROBE.json')
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'], phase_lifts=result['phase_lifts']['checked_owner_lifts'],
                         direct_closure=result['conditional_funding']['direct_three_head_conjugations']), sort_keys=True))


if __name__ == '__main__':
    main()
