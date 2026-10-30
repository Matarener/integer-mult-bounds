#!/usr/bin/env python3
"""Admit a headline only from full operator AND native/owner/outer evidence.

Arithmetic-only or geometry-only receipts cannot pass this conjunction.
All inherited infinite-size interfaces remain explicit hypotheses.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
LOWER=Q('.001730824595303184580890')
UPPER=Q('.001730824595303184580891')
OUTER_LOSS=Q(1,10**46)+Q(1,10**70)
BIT=Q('.001738137188329345368427')
PRIOR=Q('.001730739780298357321619')
TARGET=Q('.001745')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def need(ok,why):
    if not ok:
        raise ValueError(why)

def dec(x):
    with localcontext() as c:
        c.prec=100
        return str(Decimal(x.numerator)/Decimal(x.denominator))

def validate(records):
    inv,operator,runner,admit,release,prior,full=map(records.get,
        ['invoice','operator','runner','admission','release','prior','operator_self_test'])
    need(operator is not None,'Missing required full operator gate')
    need(operator['status']=='PASS_ACTUAL_T360_ALL_CHARACTER_OPERATOR_ADMISSION', 'Actual T360 operator gate')
    need(operator['all_Fourier_characters'] is True and operator['all_positive_tensor_multiplicities'] is True,
         'Positive operator admission must cover all characters and tensor multiplicities')
    need(operator['no_axis_transfer_overlay'] is True,'Current supplier cannot silently retain MOVES')
    need(operator['actual_calls']==3240 and operator['actual_hosted_rows']==1321920 and operator['symbolic_ports']==112,
         'Complete actual operator/hosting coverage')
    need(inv['status']=='PASS_FRESH_NATIVE_LITERAL_OWNERS_AND_THREE_ENGINE_COMPLEX_INVOICE','Complete current invoice')
    need(list(map(Q,inv['root']['rational']))==[LOWER,UPPER],'Exact current root bracket')
    need(inv['profile']==runner['profile']==admit['profile'],'Same global paid profile in all gates')
    need(operator['actual_residual_profile']==inv['idle_profile'],'Independent chronological residual agreement')
    need(runner['status']=='PASS_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE','Complete new release execution')
    need(admit['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE',
         'Complete inherited admission and release')
    expected=min(LOWER,BIT)-OUTER_LOSS
    need(Q(runner['kappa_rational'])==Q(admit['kappa'])==Q(release['kappa_decimal'])==expected,'Exact final outer deduction')
    need(Q(admit['complex_lower'])==LOWER,'Actual admitted complex supplier')
    need([s['name'] for s in runner['stages']]==[
        'install-outer-dependencies','dependencies','independent-terminal-word',
        'independent-receiver-word','complete-admission'], 'All five full-mode runner stages in order')
    need([s['name'] for s in admit['stages']]==[
        'owners','parent-lift','rebind','discovery','outer-check_ledger.py',
        'outer-independent_check.py','release'], 'All seven inherited full admission stages in order')
    need(all(stage['exit_code']==0 for stage in runner['stages']+admit['stages']),'Every declared stage completed')
    need(full['status']=='PASS_FAIL_CLOSED_FULL_OPERATOR_SELF_TEST' and full['baseline_admitted'] is True
         and full['candidate_admitted'] is False,'Regression rejects the actual inherited faulty MOVES')
    need(Q(prior['bit_supplier']['lower'])==BIT and prior['finite_bit_gain_certified'] is True,'Retained sufficient BIT supplier')
    need(prior['prior_complex_claim']['supported'] is False,'Prior invalid complex claim remains withdrawn')
    release_native=records['release_native']
    need(release_native['manifest_sha256']==runner['source_manifest_sha256'],
         'Native cache belongs to the actual admitted scientific source')
    for tag,pid in [('base','gauge44'),('extra','extra')]:
        actual=operator['actual_provider_bindings'][tag]
        native=inv['native_receipts'][pid]
        need(actual['candidate_sha256']==native['word_sha256']
             and actual['canonical_native_sha256']==native['native_word_sha256'], 'Same exact candidate in operator and invoice')
        bound=records['native_sources'][tag]
        current=records['native_current'][tag]
        need(release_native['providers'][tag]['word_sha256']==bound['word_sha256']
             ==current['word_sha256']==actual['candidate_sha256'],
             'Same literal word across operator, invoice, native execution and full release')
        need(bound['result_sha256']==actual['native_receipt_sha256']==records['native_current_sha256'][tag],
             'Same executed native receipt admitted everywhere')
        need(bound['native_files']==release_native['providers'][tag]['complete_native_files'],
             'Byte-identical complete native outputs in admitted cache')
        need(current['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY'
             and [s['step'] for s in current['steps']]==['native','ledgers','local-replay','wrappers','phases']
             and all(s['exit_code']==0 for s in current['steps']), 'Fresh complete five-stage native execution')
    return expected

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--release',type=Path,default=HERE/'evidence/full-release')
    ap.add_argument('--out',type=Path,default=HERE/'CLAIM.json')
    a=ap.parse_args()
    need(__debug__,'Assertions enabled')
    paths={
        'invoice':HERE/'composed-supplier/invoice/RESULT.json',
        'operator':HERE/'operator-correction/T360-OPERATOR-ADMISSION.json',
        'operator_self_test':HERE/'operator-correction/FULL-OPERATOR.json',
        'runner':a.release/'RESULT.json','admission':a.release/'admission/RESULT.json',
        'release':a.release/'admission/release/RELEASE-RECEIPT.json',
        'inventory':a.release/'FILE-INVENTORY.json',
        'release_native':a.release/'NATIVE-RECEIPT.json',
        'native_sources':a.release/'ACTUAL-NATIVE-SOURCES.json',
        'prior':REPO/'research/kappa-1745-continuation/CLAIM.json',
        'static_review':HERE/'operator-correction/RELEASE-STATIC-REVIEW.json',
    }
    records={key:read(p) for key,p in paths.items()}
    native_paths={tag:HERE/'composed-supplier'/('native-'+tag)/'RESULT.json' for tag in ['base','extra']}
    records['native_current']={tag:read(p) for tag,p in native_paths.items()}
    records['native_current_sha256']={tag:sha(p) for tag,p in native_paths.items()}
    expected=validate(records)
    pins={}
    def pin(p,expected_sha=None):
        checksum=sha(p)
        need(expected_sha is None or checksum==expected_sha,'Source-bound evidence '+str(p))
        pins[p.resolve().relative_to(REPO).as_posix()]=checksum
    for p in paths.values():
        pin(p)
    for p in native_paths.values():
        pin(p)
    for group,field in [('invoice','source_pins'),('operator','input_files'),('operator_self_test','input_files')]:
        for rel,digest in records[group][field].items():
            pin(REPO/rel,digest)
    operator=records['operator'];runner=records['runner'];inv=records['invoice']
    need(operator['complete_owner_invoice_sha256']==sha(paths['invoice']),'Operator proof references actual current invoice')
    pin(paths['admission'],runner['release_result_sha256'])
    pin(paths['release'],runner['release_receipt_sha256'])
    pin(HERE/'composed-supplier/run_release.py',runner['runner_sha256'])
    pin(a.release/'NATIVE-RECEIPT.json',runner['native_receipt_sha256'])
    need(records['inventory']['status']=='PASS_CURRENT_RELEASE_EVIDENCE_COLLECTION','Collected completed release')
    pin(HERE/'collect_release.py',records['inventory']['collector_sha256'])
    pin(HERE/'composed-supplier/run_release.py',records['inventory']['executed_runner_sha256'])
    pin(a.release/'RUNNER-EXECUTED.py',records['inventory']['executed_runner_sha256'])
    for tag,binding in records['native_sources'].items():
        root=HERE/'composed-supplier'/('native-'+tag)
        for rel,digest in binding['native_files'].items():
            pin(root/'native'/rel,digest)
        for rel,digest in binding['scientific_sources'].items():
            pin(root/'source'/rel,digest)
    for rel,record in records['inventory']['retained_files'].items():
        p=a.release/rel
        need(p.stat().st_size==record['bytes'],'Retained byte count')
        pin(p,record['sha256'])
    review=records['static_review']
    need(review['status']=='PASS_SCOPED_READ_ONLY_RELEASE_AND_INVOICE_REVIEW' and not review['acceptance_defects_found'],
         'Independent static acceptance review')
    for rel,digest in review['reviewed_files'].items():
        original=REPO/rel
        runtime=HERE/'composed-supplier/release-work'
        collected=a.release/original.relative_to(runtime) if original.is_relative_to(runtime) else original
        pin(collected,digest)
    prior=records['prior']
    for rel,digest in prior['source_sha256'].items():
        pin(REPO/rel,digest)
    for rel,digest in prior['evidence_sha256'].items():
        if rel.startswith(('bit-integration/','bit-word/')):
            pin(REPO/'research/kappa-1745-continuation'/rel,digest)
    controls=[]
    changes=[
        ('missing_operator_gate',lambda r:r.update(operator=None)),
        ('geometry_only_operator_status',lambda r:r['operator'].update(status='PASS_GEOMETRY')),
        ('finite_only_operator_check',lambda r:r['operator'].update(all_positive_tensor_multiplicities=False)),
        ('retained_axis_transfer_overlay',lambda r:r['operator'].update(no_axis_transfer_overlay=False)),
        ('different_operator_word',lambda r:r['operator']['actual_provider_bindings']['base'].update(candidate_sha256='0'*64)),
        ('different_release_word',lambda r:r['release_native']['providers']['base'].update(word_sha256='0'*64)),
        ('different_native_source_manifest',lambda r:r['release_native'].update(manifest_sha256='0'*64)),
        ('uncompleted_release',lambda r:r['runner'].update(status='PREPARED_NOT_ADMITTED')),
        ('empty_runner_stages',lambda r:r['runner'].update(stages=[])),
        ('missing_complete_admission_stage',lambda r:r['runner']['stages'].pop()),
        ('supplier_root_without_outer_loss',lambda r:r['runner'].update(kappa_rational=str(LOWER))),
        ('wrong_complete_profile',lambda r:r['invoice']['profile'].update({'1':r['invoice']['profile']['1']-1})),
        ('regression_admits_bad_moves',lambda r:r['operator_self_test'].update(candidate_admitted=True)),
    ]
    for name,change in changes:
        mutant=deepcopy(records);change(mutant)
        try:
            validate(mutant)
        except (ValueError,KeyError,TypeError):
            controls.append(name)
        else:
            raise ValueError('Claim gate accepted mutation '+name)
    pin(Path(__file__))
    result=dict(schema_version=1,status='PASS_NEW_OPERATOR_GUARDED_CONDITIONAL_KAPPA_INCREASE',
                conditional_kappa=dict(value=str(expected),decimal=dec(expected),
                    formula='min(valid_BIT_lower,valid_complex_lower)-10^-46-10^-70',binding_supplier='complex',
                    outer_loss=str(OUTER_LOSS),gain_over_previous_valid=str(LOWER-PRIOR),gain_decimal=dec(LOWER-PRIOR)),
                complex_supplier=dict(lower=str(LOWER),upper=str(UPPER),lower_decimal=dec(LOWER),upper_decimal=dec(UPPER),
                    previous_valid_lower=str(PRIOR),profile=inv['profile'],local_profile=inv['local_profile'],
                    productive_families=322560,physical_families=323069,replicas=360,local_calls=3240,
                    helpers_per_call=408,hosted_rows=1321920,global_operator_admitted=True,
                    all_characters_and_positive_tensor_multiplicities=True,native_and_full_release_reexecuted_this_turn=True),
                bit_supplier=dict(lower=str(BIT),lower_decimal=dec(BIT),upper=prior['bit_supplier']['upper'],
                    word_path=prior['bit_supplier']['word_path'],word_sha256=prior['bit_supplier']['word_gzip_sha256'],
                    status='RETAINED_SOURCE_BOUND_FINITE_BIT_SUPPLIER',reexecuted_this_turn=False,
                    complete_GL64_physical_execution=False,
                    inherited_outer_replay_uses_sufficient_bit_lower='0.001733427039589844234749'),
                target=str(TARGET),target_decimal=dec(TARGET),strictly_exceed_required=True,target_reached=expected>TARGET,
                remaining_complex_gap=str(TARGET-LOWER),remaining_bit_gap=str(TARGET-BIT),
                prior_complex_claim=dict(supported=False,invalid_arithmetic_endpoint_decimal='.0017411725885452521674224',
                    reason='Actual MOVES changes the full exact operator; new fail-closed gate reproduces rejection. The current construction uses no such transfers.'),
                full_operator_regression=True,claim_gate_rejecting_controls=controls,new_combined_kappa=True,
                formal_kernel_acceptance=False,independent_human_review=False,maintainer_admitted=False,
                unconditional_multiplication_theorem=False,
                inherited_hypotheses=[
                    'Uniform native local realization, chart embeddings, recursive-D and physical primitive implementation of the source-bound complex and BIT words.',
                    'Common-cover/owner embeddings and complete finite hosting interfaces extend through the recursive construction.',
                    'Tape/compiler tariffs, precision, recovery, bad-event and stopped-supplier hypotheses remain valid for these exact providers.',
                    'Fine-prime padding, gauge-free interiors and outer transfer hypotheses of the retained conditional release.',
                ],
                scope='New complete finite operator/native/owner certificate and reexecuted conditional resource/outer release. The .001745 target is not reached. Research exclusions apply only to their explicitly checked architectures.',
                source_pins=dict(sorted(pins.items())))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],result['conditional_kappa']['decimal'],'controls',len(controls))

if __name__=='__main__':
    main()
