#!/usr/bin/env python3
"""Exact finite H6 child-grid and standalone asymmetric K grid calculation.

This is an exact-child mathematical ledger, not an approximate-child or
finite-tape implementation. It verifies native coefficient formulas using
Gaussian integers and reconstructs the two complete actual pure-bank labels.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import sys

sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/ross/git/math/integer-mult-bounds')
INPUT = HERE.parent / 'bulk-partial'


def need(value, message):
    if not value:
        raise ValueError(message)


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def gaussian_power(a, exponent):
    out = (1, 0)
    for _ in range(exponent):
        out = mul(out, a)
    return out


def native_child_ledger():
    rows = []
    for rank in range(18):
        depth = 0
        component_norm = Fraction(0)
        support = 0
        for weight in range(rank + 1):
            re, im = mul(gaussian_power((1, 1), rank - weight), gaussian_power((1, -1), weight))
            d = rank
            component_norm += Fraction(math.comb(rank, weight) * (abs(re) + abs(im)), 1 << rank)
            while d and re % 2 == 0 and im % 2 == 0:
                re //= 2
                im //= 2
                d -= 1
            need(re or im, 'native Fourier coefficient unexpectedly zero')
            support += math.comb(rank, weight)
            depth = max(depth, d)
        need(depth == (rank + 1) // 2, 'exact native child dyadic depth formula')
        need(component_norm == 1 << ((rank + 1) // 2), 'independent real component row norm formula')
        need(support == 1 << rank, 'native child complete row support')
        rows.append(dict(rank=rank, gaussian_dyadic_depth=depth,
                         independent_real_component_linf_norm=str(component_norm),
                         complex_row_l1_norm_squared=1 << rank, nonzero_coefficients_per_row=support))
    return rows


def actual_geometry():
    geo_dir = ROOT / 'research/niemeier-lattices/code'
    sys.path.insert(0, str(geo_dir))
    import e8_cubed as geo
    roots, _, shell, profiles = geo.construct_shell()
    ports = shell[(profiles & 4) == 0, :16].astype(np.int64)
    _, packed, _ = geo.binary_labels(roots, ports)
    frozen = json.loads((INPUT / 'FRAME-INPUT.json').read_text())
    need(len(ports) == 30960, 'complete actual H6 port census')
    need(len(set(map(int, packed))) == 14670 and all(int(p).bit_count()%2 == 1 and int(p) != (1<<17)-1 for p in packed),
         'complete actual unchanged norm-one endpoint family')
    all_pure = np.zeros(len(ports), dtype=bool)
    banks = []
    for bank in range(2):
        other = ports[:, 8 * (1 - bank):8 * (2 - bank)]
        mask = np.all(other == 0, axis=1)
        need(not np.any(all_pure & mask), 'pure banks overlap')
        all_pure |= mask
        labels = Counter(map(int, packed[mask]))
        supplied = {int(t['source_label']):int(t['port_multiplicity']) for t in frozen['banks'][bank]['source_transitions']}
        need(labels == supplied, 'frozen source transition list is not the complete actual pure-bank label census')
        need(sum(labels.values()) == 1080 and len(labels) == 135 and set(labels.values()) == {8}, 'actual pure-bank support count')
        banks.append(dict(bank=bank, actual_ports=sum(labels.values()), distinct_labels=len(labels),
                          multiplicities=dict(sorted(labels.items()))))
    need(int(all_pure.sum()) == 2160, 'complete disjoint pure-bank union')
    return banks


def main():
    children = native_child_ledger()
    banks = actual_geometry()
    scalar = json.loads((INPUT / 'ASYMMETRIC.json').read_text())['full_scalar_invoice']
    need(scalar['denominator_depth_above_entrance_grid'] == 10, 'scalar coefficient depth')
    # Every number below is the number of bits above the initial physical grid.
    # A completed private descent is tightened using its exact frame identity:
    # T_U^-1 T_U(d+A^T C_p^-1 h) = d+A^T C_p^-1 h.
    forward = dict(
        initial_physical_roles=0, initial_logical_sources=1,
        pure_sources_at_U=4, mixed_sources_at_FULL=8, pure_sources_at_FULL=8,
        partial_centres_at_U_after_gather=5, full_centres_after_gather=9,
        partial_private_native_prefix=10, full_private_native_prefix=18,
        completed_private_at_ZERO=1,
        target_precompensation_at_ZERO=10, target_scatter_at_ZERO=11,
        partial_centres_at_FULL=9, full_centres_cleanup=9,
        target_final_cap_native_prefix=19,
    )
    dual = dict(
        initial_physical_roles=0, initial_logical_sources=1,
        precompensation_centres_at_ZERO=10,
        partial_centres_at_U=15, full_centres_at_FULL=19,
        pure_source_after_partial_dual_gather_at_U=15,
        pure_source_native_ascent_to_FULL=19,
        mixed_source_after_full_dual_gather=19,
        private_gather_at_ZERO=10, partial_private_native_prefix=15,
        full_private_native_prefix=19,
        restored_partial_centre_at_U=5, restored_centres_at_FULL=9,
        source_after_full_cleanup=19, target_final_cap_native_prefix=8,
    )
    need(forward['pure_sources_at_U'] + 4 == forward['pure_sources_at_FULL'], 'split source grid')
    need(forward['partial_centres_at_U_after_gather'] + 5 == forward['partial_private_native_prefix'], 'partial private grid')
    need(forward['full_centres_after_gather'] + 9 == forward['full_private_native_prefix'], 'full private grid')
    need(forward['completed_private_at_ZERO'] + 10 == forward['target_scatter_at_ZERO'], 'scatter grid')
    need(forward['target_scatter_at_ZERO'] + 8 == forward['target_final_cap_native_prefix'], 'final target grid')
    need(dual['precompensation_centres_at_ZERO'] + 5 == dual['partial_centres_at_U'], 'dual U grid')
    need(dual['precompensation_centres_at_ZERO'] + 9 == dual['full_centres_at_FULL'], 'dual FULL grid')
    need(dual['pure_source_after_partial_dual_gather_at_U'] + 4 == dual['pure_source_native_ascent_to_FULL'], 'dual pure source tail grid')
    range_bounds = {}
    for name in ('forward', 'dual'):
        logical = Fraction(scalar[name + '_logical_prefix_l1_upper'])
        horner = Fraction(scalar[name + '_Horner_work_l1_upper'])
        need(horner <= 16 * logical, 'scalar Horner range premise')
        # Input physical independent real/imaginary components bounded by M.
        # Initial logical C_p^-1 inputs are bounded by 2M. Exact cut frames
        # have real component row norm <=512. Exposed coordinate-C prefixes
        # have the same <=512 bound. No child executes inside scalar Horner.
        native_prefix_gain = 2 * 512 * 512 * logical
        horner_gain = 2 * 512 * horner
        gain = max(native_prefix_gain, horner_gain)
        need(gain.denominator == 1, 'range upper bound is not integral')
        bits = (gain.numerator - 1).bit_length()
        range_bounds[name] = dict(
            logical_prefix_l1_upper=str(logical), cleared_Horner_work_l1_upper=str(horner),
            physical_macro_prefix_component_gain_upper=str(gain),
            component_magnitude_bits_upper=bits,
            numerator_bits_above_input_upper=19 + bits,
            note='Conditional on the scalar word identity/prefix bounds. Counts values at scalar macro cuts and coordinate-C prefix states; excludes child internal machine arithmetic and all-size approximation.')
    result = dict(
        status='PASS_EXACT_NATIVE_CHILD_DEPTH_AND_STANDALONE_K_PHYSICAL_GRID',
        exact_native_child_coefficients=children, actual_pure_bank_label_crosscheck=banks,
        adapter_extra_fractional_bits=0, adapter_real_component_linf_norm=1,
        rank8_child_exact_depth=4, rank9_child_exact_depth=5,
        split_source_chain_exact_depth_upper=8, ordinary_partial_chain_exact_depth_upper=9,
        private_U_to_ZERO_exact_depth_upper=5,
        standalone_K_forward_stage_extra_fractional_bits=forward,
        standalone_K_same_order_inverse_transpose_extra_fractional_bits=dual,
        standalone_K_common_extra_fractional_bits=max(max(forward.values()), max(dual.values())),
        conditional_physical_range=range_bounds,
        common_grid_statement='For arbitrary physical Gaussian-dyadic sources at their actual C_p entrance frames, targets at ZERO and arbitrary independent ordinary centre dirt at ZERO on grid 2^-f, the standalone full asymmetric K word with exact native children stays on grid 2^-(f+19) in both orientations, including emitted coordinate-C prefix states and scalar Horner work. Private scratch has the declared cleared/erased contract. This excludes an integrated compensation network and approximate children.',
        source_hashes={str(INPUT / p):hashlib.sha256((INPUT / p).read_bytes()).hexdigest() for p in ('FRAME-INPUT.json','ASYMMETRIC.json')},
        geometry_source_sha256=hashlib.sha256((ROOT / 'research/niemeier-lattices/code/e8_cubed.py').read_bytes()).hexdigest(),
        scope='Finite exact-child K operator and declared physical entrance normalization only. The denominator and row-norm child formulas are written all-r identities; the source census is finite. No all-size supplier, approximate-child error, literal tape or joint kappa admission.')
    (HERE / 'PRECISION.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status=result['status'], common_extra_bits=result['standalone_K_common_extra_fractional_bits'],
                          conditional_physical_range=range_bounds), indent=2))


if __name__ == '__main__':
    main()
