#!/usr/bin/env python3
"""Price emitted Gaussian adapters, including explicit phase/index circuits.

All data-operation totals below are semantic coordinate actions. Boolean
address/phase work is itemized separately and is not a fixed-tape step count.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('partial_native_independent_audit', HERE / 'audit.py')
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)
np = audit.np
N, SIZE = audit.N, audit.SIZE


def adapter_detail(m):
    if m is None:
        return {}
    quadratic = sum((row >> (i + 1)).bit_count() for i, row in enumerate(m['quadratic_rows']))
    alpha = Counter(m['linear_Z4'])
    phase = audit.phase_values(tuple(m['quadratic_rows']), tuple(m['linear_Z4']), m['phase'])
    distribution = dict(enumerate(map(int, np.bincount(phase, minlength=4))))
    # Evaluate each output affine bit by its row parity and its offset bit.
    address_xors = sum(row.bit_count() - 1 for row in m['matrix_rows']) + m['offset'].bit_count()
    # Add alpha_i*x_i modulo 4 to a two-bit accumulator. Alpha1 needs
    # one AND/two XOR, alpha2 one XOR, alpha3 one AND/three XOR.
    # A quadratic 2*x_i*x_j needs one AND and one high-bit XOR.
    phase_ands = quadratic + alpha[1] + alpha[3]
    phase_xors = quadratic + 2 * alpha[1] + alpha[2] + 3 * alpha[3]
    moved = tuple(m['matrix_rows']) != tuple(1 << i for i in range(N)) or m['offset'] != 0
    return dict(phase_distribution_Z4=distribution,
                nonidentity_fused_complex_unit_actions=SIZE - distribution[0],
                direct_fused_real_negations=distribution[1] + distribution[3] + 2 * distribution[2],
                address_bit_xors_per_coordinate=address_xors if moved else 0,
                phase_bit_ands_per_coordinate=phase_ands,
                phase_bit_xors_per_coordinate=phase_xors,
                factorized_active_complex_unit_actions=quadratic * (SIZE // 4) + (alpha[1] + alpha[2] + alpha[3]) * (SIZE // 2) + int(m['phase'] != 0) * SIZE)


def rec_detail(rec):
    detail = {s:adapter_detail(rec[s]) for s in ('left','right')}
    totals = Counter()
    for side in detail.values():
        totals.update({k:v for k,v in side.items() if k != 'phase_distribution_Z4'})
    return dict(sides=detail, totals=dict(totals))


def aggregate(details, weights):
    totals = Counter()
    for name, amount in weights.items():
        totals.update({k:amount*v for k,v in details[name]['totals'].items()})
    for name in ('address_bit_xors', 'phase_bit_ands', 'phase_bit_xors'):
        totals[name + '_all_coordinates'] = totals[name + '_per_coordinate'] * SIZE
    return dict(totals)


def full_monomial(aff):
    return dict(matrix_rows=aff['matrix_rows'], offset=aff['offset'], quadratic_rows=[0]*N,
                linear_Z4=[0]*N, phase=0)


def main():
    source = audit.validate_inputs()
    native = json.loads((HERE / 'RECIPES.json').read_text())
    receipt = json.loads((HERE / 'RESULT.json').read_text())
    audit.need(hashlib.sha256((HERE/'RECIPES.json').read_bytes()).hexdigest() == receipt['recipe_sha256'], 'new recipe hash changed')
    details = {r['name']:rec_detail(r) for r in native['recipes']}
    universal = audit.load_module('partial_native_old_universal', audit.ROOT / 'research/h6-compensation-network/physical_compiler/universal.py')
    baselines = []
    baseline_weights = {}
    ce = audit.ce
    I, F = ce.ident(N), ce.fourier(N)
    for bank in source['banks']:
        for src in bank['source_transitions']:
            label = int(src['source_label'])
            inherited = universal.residual_recipe((label,))
            universal.verify_symbolic(inherited)
            rec = dict(rank=16, left=full_monomial(inherited['left']), right=full_monomial(inherited['right']),
                       name=f'old_bank{bank["bank"]}_line{label}_to_FULL', source_label=label)
            rec['independent_phase_witness'] = audit.check_recipe(rec, ce.cgate(N,label).adjoint().then(F))
            rec['local_counts'] = audit.counts(rec)
            baselines.append(rec)
            baseline_weights[rec['name']] = int(src['port_multiplicity'])
    identity = dict(matrix_rows=[1<<i for i in range(N)], offset=0, quadratic_rows=[0]*N, linear_Z4=[0]*N, phase=0)
    for name, inverse in [('old_ordinary_ZERO_to_FULL',False), ('old_private_FULL_to_ZERO',True)]:
        right = dict(identity)
        right['offset'] = SIZE - 1 if inverse else 0
        rec = dict(rank=17, left=identity, right=right, name=name)
        rec['independent_phase_witness'] = audit.check_recipe(rec, F.adjoint() if inverse else F)
        rec['local_counts'] = audit.counts(rec)
        baselines.append(rec)
        baseline_weights[name] = 16
    old_forward = audit.weighted_count(baselines, baseline_weights)
    old_dual_weights = dict(baseline_weights)
    del old_dual_weights['old_private_FULL_to_ZERO']
    old_dual_weights['old_ordinary_ZERO_to_FULL'] += 16
    old_dual = audit.weighted_count(baselines, old_dual_weights)
    scalar = json.loads((audit.INPUT/'ASYMMETRIC.json').read_text())['full_scalar_invoice']
    comparisons = {}
    weighted = {}
    for orientation, weights, old in [
        ('forward',native['forward_chronological_multiplicities'],old_forward),
        ('same_order_inverse_transpose',native['same_order_inverse_transpose_multiplicities'],old_dual),
    ]:
        new = audit.weighted_count(native['recipes'],weights)
        weighted[orientation] = aggregate(details,weights)
        scalar_change = scalar['forward_component_primitive_change' if orientation == 'forward' else 'dual_component_primitive_change']
        address_change = new['affine_address_passes'] - old['affine_address_passes']
        phase_change = new['unit_phase_factors'] - old['unit_phase_factors']
        total = scalar_change + address_change + phase_change
        audit.need(total < 0, 'finite semantic scalar-plus-factorized-adapter comparison failed')
        fused_real_data_change = 2 * SIZE * (scalar_change + address_change) + weighted[orientation]['direct_fused_real_negations']
        comparisons[orientation] = dict(
            old_changed_role_adapter_counts=old,
            new_changed_role_adapter_counts=new,
            scalar_primitive_change_per_coordinate=scalar_change,
            affine_address_pass_change_per_coordinate=address_change,
            factorized_unit_phase_upper_change_per_coordinate=phase_change,
            scalar_plus_factorized_adapter_semantic_complex_action_upper_change_per_coordinate=total,
            expanded_complex_action_upper_change=total*SIZE,
            fused_real_data_action_upper_change=fused_real_data_change,
            convention='One semantic complex coordinate action per inherited scalar primitive, affine address movement, or unit Gaussian factor. The fused real data comparison separately doubles scalar/movement actions and charges actual real sign changes, with component swaps selected inside affine movement. Excludes index Boolean operations, dispatch and physical routing/tape.')
    base_raw = json.dumps(dict(h=N, recipes=baselines, forward_multiplicities=baseline_weights,
                              same_order_inverse_transpose_multiplicities=old_dual_weights), sort_keys=True,separators=(',',':')).encode()+b'\n'
    (HERE/'BASELINE-RECIPES.json').write_bytes(base_raw)
    result = dict(status='PASS_PAID_GAUSSIAN_ADAPTER_AND_EXACT_REPLACED_BASELINE_CENSUS',
                  full_baseline_recipes_phase_checked=len(baselines),
                  baseline_recipe_sha256=hashlib.sha256(base_raw).hexdigest(),
                  emitted_recipe_details=details, weighted_details=weighted,
                  semantic_scalar_comparisons=comparisons,
                  index_circuit_contract='For each address, row parities use sum(row_weight-1)+offset_weight XOR gates. Phase q(x) is accumulated modulo4 with the stated exact AND/XOR circuit. Address/input-bit access, predicates/dispatch, in-place permutation strategy, controller and tape costs remain separate.',
                  scalar_data_contract='Fused phases have the exact displayed Z4 distribution. One full affine pass moves two real components per complex coordinate; selecting swapped source components can be fused with that pass. The direct four-unit casework uses the displayed exact number of real sign changes. These semantic data actions do not declare phase or index work free.',
                  source_hashes=dict(audit_py=hashlib.sha256((HERE/'audit.py').read_bytes()).hexdigest(),
                                     RECIPES_json=receipt['recipe_sha256'],
                                     universal_py=hashlib.sha256((audit.ROOT/'research/h6-compensation-network/physical_compiler/universal.py').read_bytes()).hexdigest()),
                  scope='Complete local new Gaussian adapter census and all replaced old source/centre recipe checks. Scalar comparison is in the inherited semantic action convention only, not a complete literal finite-tape or asymptotic supplier admission.')
    (HERE/'ADAPTER-WORK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'], baseline_recipes=len(baselines), weighted=weighted,
                          comparisons={k:{f:v[f] for f in ('scalar_primitive_change_per_coordinate','affine_address_pass_change_per_coordinate','factorized_unit_phase_upper_change_per_coordinate','scalar_plus_factorized_adapter_semantic_complex_action_upper_change_per_coordinate')} for k,v in comparisons.items()}),indent=2))


if __name__ == '__main__':
    main()
