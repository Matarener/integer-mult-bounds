#!/usr/bin/env python3
"""Assemble the corrected claim from actual finite execution receipts.

This does not introduce an all-size theorem. It explicitly rejects the
previously used complex overlay and retains the earlier valid conditional
complex supplier. Apache-2.0; substantial OpenAI assistance.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_SHA = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'


def read(name):
    return json.loads((HERE/name).read_text())


def decimal(value):
    with localcontext() as ctx:
        ctx.prec = 110
        return format(Decimal(value.numerator)/Decimal(value.denominator), 'f')


def main():
    invoice = read('bit-integration/early-birth-prefixes/RESULT.json')
    review = read('bit-geometry/BIT-FINAL-INDEPENDENT-REVIEW.json')
    native = read('bit-integration/FINAL-NATIVE-REVIEW.json')
    whole = read('bit-integration/FINAL-WHOLE-WORD.json')
    physical = read('bit-integration/FINAL-PHYSICAL-PROBE.json')
    execution = read('bit-integration/FINAL-NATIVE-EXECUTION.json')
    witness = read('operator-audit/INDEPENDENT-WITNESS.json')
    prior_bit = json.loads((HERE.parent/'kappa-next-regime/CLAIM.json').read_text())
    prior_complex = json.loads((HERE.parent/'kappa-adaptive-continuation/CLAIM.json').read_text())
    target = Q('.001745')
    lower, upper = Q(invoice['bit_endpoint_lower']), Q(invoice['bit_endpoint_upper'])
    assert lower == Q('.001738137188329345368427')
    assert upper-lower == Q(1, 10**24) and upper < target
    assert invoice['word_content_sha256'] == review['word_canonical_sha256'] == WORD_SHA
    assert native['actual_word_content_sha256'] == whole['native_binding']['actual_word_content_sha256'] == physical['word_content_sha256'] == WORD_SHA
    assert native['binding_sha256'] == whole['native_binding']['binding_sha256'] == physical['catalogue']['binding_sha256'] == execution['binding_sha256']
    assert invoice['profile'] == review['complete_invoice']['profile']
    assert invoice['paid_requests'] == native['canonical_requests'] == whole['complete']['residuals'] == 987525
    assert physical['complete_GL64_payload_executed'] is False
    assert execution['status'] == 'PASS_FINAL_NATIVE_SYMBOLIC_AND_CONTROLLED_PHYSICAL_EXECUTION'
    assert witness['prior_complex_claim_supported'] is False
    assert all(step['exit_code'] == 0 for step in execution['steps'])
    complex_lower = Q(prior_complex['root_lower_decimal'])
    complex_upper = Q(prior_complex['root_upper_decimal'])
    assert complex_lower == Q('.001730739780298357321619') < lower
    loss = Q(1, 10**46)+Q(1, 10**70)
    retained_kappa = min(lower, complex_lower)-loss
    old_bit = Q(prior_bit['bit_root_lower'])
    word_path = HERE/'bit-word/early-birth-prefixes/WORD.json.gz'
    assert sha256(gzip.decompress(word_path.read_bytes())).hexdigest() == WORD_SHA
    evidence = [
        'bit-word/CURRENT.json', 'bit-word/early-birth-prefixes/RESULT.json',
        'bit-integration/early-birth-prefixes/RESULT.json',
        'bit-geometry/BIT-FINAL-INDEPENDENT-REVIEW.json',
        'bit-integration/FINAL-NATIVE-REVIEW.json', 'bit-integration/FINAL-WHOLE-WORD.json',
        'bit-integration/FINAL-PHYSICAL-PROBE.json', 'bit-integration/FINAL-NATIVE-EXECUTION.json',
        'operator-audit/FRESH-REPLAY.json', 'operator-audit/INDEPENDENT-WITNESS.json',
        'operator-audit/RIGIDITY-REVIEW.json', 'complex/CELLMAP-INVARIANCE.json',
        'complex/SLOT-PROJECTOR-RIGIDITY.json', 'complex/TARGET-BUDGET.json',
        'bit-geometry/ACHIEVED-BIT-CLOCK-REPRICE.json', 'bit-geometry/LARGER-PAIR-BUDGET.json',
        'bit-geometry/FINAL-ENTRANCE-CLOSURE.json', 'complex-controller/REVIEW.json',
        'complex-birth/REVIEW.json',
    ]
    for name in evidence:
        assert (HERE/name).is_file(), name
    result = {
        'schema_version': 1,
        'status': 'PARTIAL_VALID_BIT_GAIN_TARGET_NOT_REACHED',
        'target': str(target), 'target_decimal': '.001745', 'strictly_exceed_required': True,
        'target_reached': False, 'new_combined_kappa': False,
        'finite_bit_gain_certified': True,
        'canonical_main': '20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'bit_supplier': {
            'status': 'COMPLETE_FINITE_WORD_AND_CONDITIONAL_PRICE_CHECKED',
            'lower': str(lower), 'upper': str(upper),
            'lower_decimal': decimal(lower), 'upper_decimal': decimal(upper),
            'previous_valid_BIT_lower': str(old_bit),
            'gain_over_previous_BIT_lower': str(lower-old_bit),
            'gain_over_previous_BIT_lower_decimal': decimal(lower-old_bit),
            'gap_to_target': str(target-lower), 'gap_to_target_decimal': decimal(target-lower),
            'previous_BIT_gap_closed_percent': decimal(100*(lower-old_bit)/(target-old_bit)),
            'word_path': str(word_path.relative_to(ROOT)), 'word_content_sha256': WORD_SHA,
            'word_gzip_sha256': sha256(word_path.read_bytes()).hexdigest(),
            'template_content_sha256': invoice['template_content_sha256'],
            'binding_sha256': native['binding_sha256'],
            'local_profile': invoice['local_profile'], 'complete_profile': invoice['profile'],
            'm': invoice['m'], 'productive_families': invoice['productive_families'],
            'physical_families': invoice['physical_families'], 'replicas': invoice['replicas'],
            'local_calls': invoice['local_calls'], 'helpers_per_call': 437,
            'paid_requests': invoice['paid_requests'], 'rank_mass': invoice['rank_mass'],
            'raw_deficit': invoice['raw_deficit'],
            'forward_prefix_bound': invoice['block_proof']['forward_norm'],
            'reverse_prefix_bound': invoice['block_proof']['reverse_norm'],
            'actual_prefix_bits': invoice['coefficient_invoice']['prefix_bits'],
            'charged_prefix_bits': invoice['coefficient_invoice']['charged_prefix_bits'],
            'actual_two_level_bits': invoice['coefficient_invoice']['two_level_bits'],
            'charged_two_level_bits': invoice['coefficient_invoice']['charged_two_level_bits'],
            'ROW': invoice['coefficient_invoice']['ROW'],
        },
        'complex_supplier': {
            'status': 'RETAINED_VALID_PREDECESSOR',
            'lower': str(complex_lower), 'upper': str(complex_upper),
            'lower_decimal': decimal(complex_lower), 'upper_decimal': decimal(complex_upper),
            'gap_to_target': str(target-complex_lower), 'gap_to_target_decimal': decimal(target-complex_lower),
            'source_claim': 'research/kappa-adaptive-continuation/CLAIM.json',
            'source_invoice': 'research/kappa-adaptive-continuation/global-budget/receiver-sharing/RESULT.json',
            'native_and_physical_release_reexecuted_this_turn': False,
            'scope': 'The valid receiver-sharing predecessor and its inherited all-size hypotheses; none of the invalid idle-axis overlays is used.',
        },
        'prior_complex_claim': {
            'supported': False,
            'invalid_arithmetic_endpoint_decimal': '.0017411725885452521674224',
            'superseded_combined_claim': 'research/kappa-next-regime/CLAIM.json',
            'reason': 'Fresh unchanged PR4046 operator replay and an independent dense Gaussian-integer counterexample against the actual previous MOVES. Cell-to-axis permutations do not repair the literal T740 chronology.',
            'witness': 'research/kappa-1745-continuation/operator-audit/INDEPENDENT-WITNESS.json',
        },
        'retained_conditional_kappa': {
            'formula': 'min(valid_BIT_lower,valid_complex_lower)-10^-46-10^-70',
            'value': str(retained_kappa), 'decimal': decimal(retained_kappa),
            'outer_loss': str(loss), 'binding_supplier': 'complex',
            'new_gain_claimed': False,
        },
        'verification': {
            'independent_rational_price_implementations': 3,
            'local_columns_per_direction': 659, 'native_five_stage_columns': 881,
            'rational_frames': 758, 'independent_native_gauge_identities': 141,
            'changed_paths_in_final_review': 37,
            'native_requests': native['canonical_requests'],
            'owner_pairs': native['same_family_owner_pairs'],
            'symbolic_XORs': whole['complete']['complete_xor_count'],
            'symbolic_checkpoints': whole['complete']['checkpoints'],
            'physical_controlled_payload_bits': physical['controlled_payload_bits'],
            'physical_calls': physical['counts']['calls'], 'physical_returns': physical['counts']['returns'],
            'physical_rejecting_controls': len(physical['rejected_gates'])+len(physical['semantic_rejections']),
            'complete_GL64_physical_execution': False,
        },
        'inherited_hypotheses': [
            'Native packet, chart preparation, recursive-D and all-size source interfaces for the changed R437 word.',
            'Actual physical primitive realization, stock and precision/recovery interfaces beyond the controlled finite protocol.',
            'Applicability of the retained bad-event and compiler tariff to the changed source-bound word.',
            'Five-replica pooled helper ownership and finite coefficient invoices extend through the retained recursive construction.',
            'Valid receiver-sharing complex source and its native/physical/all-size hypotheses.',
            'Fine-prime-padding, gauge-free, stopped-supplier and outer-composition theorems.',
        ],
        'independent_human_review': False, 'formal_kernel_acceptance': False,
        'maintainer_admitted': False, 'unconditional_multiplication_theorem': False,
        'evidence_sha256': {name: sha256((HERE/name).read_bytes()).hexdigest() for name in evidence},
        'source_sha256': {
            str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__), word_path, HERE.parent/'kappa-next-regime/CLAIM.json',
                      HERE.parent/'kappa-adaptive-continuation/CLAIM.json',
                      HERE.parent/'kappa-adaptive-continuation/global-budget/receiver-sharing/RESULT.json')
        },
        'scope': 'A stronger valid finite BIT construction and corrected conditional accounting. The requested0.001745 target is not reached. Scoped obstructions and failed construction searches are not general impossibility results.',
    }
    (HERE/'CLAIM.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    task = read('TASK.json')
    if 'BIT_gap_to_target' in task:
        task['BIT_previous_gap_to_target'] = task.pop('BIT_gap_to_target')
    task.update(status=result['status'], target_reached=False,
                BIT_achieved_lower_decimal=decimal(lower), BIT_current_gap_to_target_decimal=decimal(target-lower),
                complex_valid_lower_decimal=decimal(complex_lower),
                outcome='Complete finite BIT improvement; previous high complex operator input invalidated; target remains unachieved.')
    (HERE/'TASK.json').write_text(json.dumps(task, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': result['status'], 'BIT_lower': decimal(lower), 'retained_conditional_kappa': decimal(retained_kappa), 'target_reached': False}))


if __name__ == '__main__':
    main()
