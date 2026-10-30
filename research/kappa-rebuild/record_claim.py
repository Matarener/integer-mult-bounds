#!/usr/bin/env python3
"""Bind the proposed conditional claim to its written proofs and exact receipts.

This is a provenance gate, not a theorem prover. The mathematical boundary is
recorded explicitly. Apache-2.0; substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def read(name):
    return json.loads((HERE/name).read_text())


def main():
    outer = read('transfer-audit/OUTER-TRANSFER-AUDIT.json')
    replay = read('verification/CRITICAL-REPLAY.json')
    explicit = read('controller/EXPLICIT-TEMPLATE-BOUNDS.json')
    ledger = read('controller/OUTER-PARAMETERS.json')
    bridge = read('transfer-audit/BIT-BRIDGE-AUDIT.json')
    need(outer['status'] == 'PASS_EXPLICIT_RANKS_NEW_NATIVE_INTERFACES_AND_CONDITIONAL_OUTER_POINT', 'Independent transfer audit')
    need(bridge['status'] == 'PASS_NATIVE_ROLES_COMPLETE_DAG_ALL_COLUMN_PAIRING_COMMON_WEIGHT_AND_PAID_COVER', 'Independent BIT bridge')
    need(replay['status'] == 'PASS_FRESH_NATIVE_AND_CONDITIONAL_INTERFACE_REPLAY', 'Fresh critical replay')
    need(replay['reconstructed_primitive_stages_replayed'] and len(replay['stages']) == 23, 'All primitive and interface stages replayed')
    need(len(replay['artifact_comparisons']) == 59, 'All declared native/proof artifacts compared')
    need(all(row['returncode'] == 0 for row in replay['stages']), 'No failed scientific stage')
    kappa = Q(outer['conditional_assembly']['kappa'])
    need(kappa == Q(23,10000), 'Declared target')
    savings = {k:Q(v) for k,v in outer['conditional_assembly']['nine_outer_savings'].items()}
    need(len(savings) == 9 and min(savings.values())-kappa == Q(98849,50000000000), 'Complete strict outer bill')
    need(all(Q(v) > 0 for v in outer['conditional_assembly']['functional_interface_gaps'].values()), 'Every changed interface gap')
    need(not replay['winning_uniform_words_materialized'], 'Materialization limitation retained')
    ranks = {row['family']:row['N']['H1'] for row in explicit['cases']}
    need(ranks == {'complex':276540184361,'BIT':6552928412}, 'Exact finite template specification')
    sources = [
        'README.md', 'LITERATURE-AND-PROBES.md', 'TASK.json', 'record_claim.py',
        'architecture/FINITE-PRECOMPILATION.md',
        'controller/P3-NATIVE-COVER.json.gz', 'controller/OUTER-PARAMETERS.json',
        'controller/EXPLICIT-TEMPLATE-BOUNDS.json', 'controller/EXPLICIT-TEMPLATE-BOUNDS.md',
        'bit/BIT-P3-NATIVE-BINDING.json', 'bit/DELAYED-COVER-BRIDGE.md',
        'bit/BIT-ALLSIZE-PARAMETERS.json',
        'transfer-audit/AUDIT.md', 'transfer-audit/FINITE-DAG-AUDIT.json',
        'transfer-audit/P3-NATIVE-AUDIT.json.gz', 'transfer-audit/P3-COVER-AUDIT.json',
        'transfer-audit/BIT-BRIDGE-AUDIT.json', 'transfer-audit/FINITE-TEMPLATE-CLOSURE.md',
        'transfer-audit/PRECISION-CLOSURE.json', 'transfer-audit/OUTER-TRANSFER-AUDIT.md',
        'transfer-audit/OUTER-TRANSFER-AUDIT.json',
        'verification/CRITICAL-REPLAY.json', 'verification/BASE-MATERIALIZED.json',
        'verification/PRIOR-APPLIED.json', 'provenance/public-final/REFRESH.json',
        'replay_critical.py',
    ]
    bindings = {str((HERE/name).relative_to(ROOT)):sha256((HERE/name).read_bytes()).hexdigest() for name in sources}
    # Every regenerated canonical artifact must still be the one compared by
    # the fresh replay. Later H-branch additions do not alter these inputs.
    for row in replay['artifact_comparisons']:
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['reference_sha256'], 'Canonical replay artifact still frozen: '+row['path'])
    for row in replay['stages']:
        source = ROOT/row['command'][2]
        need(sha256(source.read_bytes()).hexdigest() == row['source_sha256'], 'Scientific replay source still frozen')
    baseline = Q('0.001730970419199163702738')
    claim = {
        'schema':'proposed-conditional-integer-multiplication-claim/1',
        'status':'COMPLETE_PROPOSED_CONDITIONAL_CONSTRUCTION_WITH_FRESH_FINITE_REPLAY',
        'date_utc':'2026-10-21',
        'claim':'T(n) = O(n (log n)^(1-kappa)) under the retained analytic/native hypotheses and the supplied written construction.',
        'kappa':str(kappa), 'kappa_decimal':'0.0023',
        'user_comparison_baseline':str(baseline),
        'relative_exponent_saving_increase':str(kappa/baseline-1),
        'limiting_outer_saving':str(min(savings.values())),
        'strict_limiting_slack':str(min(savings.values())-kappa),
        'nine_outer_savings':{k:str(v) for k,v in savings.items()},
        'uniform_templates':[
            {'family':'complex','rank_encoding':'2^276540184361','saving':'0.002304'},
            {'family':'BIT before cover','rank_encoding':'2^6552928412','saving':'0.002760'},
        ],
        'ordinary_BIT_saving':'0.0027418653797',
        'admitted_BIT_saving':'0.0027',
        'source_sha256':bindings,
        'fresh_replay':{'stages':23,'artifacts':59,'all_passed':True},
        'written_proof_entry':'research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md',
        'remaining_hypotheses':[
            'The inherited analytic decomposition and exact integer recovery.',
            'The retained native ordered-movement and fixed-tape execution framework.',
            'The inherited fine-prime padding, gauge-free interior and outer analytic estimates.',
        ],
        'verification_limits':[
            'Universal finite-precompilation, native closure and outer transfer are written mathematical arguments, not formally machine-checked theorems.',
            'Winning fixed uniform words, complete GL covers, B_N, P_N and U_N are algorithm-defined but not materialized.',
            'No practical runtime, usable numerical threshold, unconditional theorem, upstream admission or novelty claim is made.',
        ],
        'larger_H_branch':'Separate local improvements and priced negative boundary probes; no kappa above 0.0023 is claimed.',
        'official_selected_frontier_modified':False,
        'public_posted_or_merged':False,
        'preserve_all_unmerged_changes_until_user_reports_merge':True,
        'attribution':'Apache-2.0; substantial OpenAI assistance; immutable predecessor authors and source licenses retained.',
    }
    (HERE/'CLAIM.json').write_text(json.dumps(claim,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':claim['status'],'kappa':claim['kappa'],'source_bindings':len(bindings),'fresh_stages':23,'fresh_artifacts':59}))


if __name__ == '__main__':
    main()
