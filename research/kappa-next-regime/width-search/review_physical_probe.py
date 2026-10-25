#!/usr/bin/env python3
"""Source-bound static review of the updated controlled nested physical probe.

This does not rerun the costly caller. The script pins the exact source diff
reviewed independently, verifies its runtime receipt and recalculates grants.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
REPO = TASK.parents[1]
ORIGINAL = TASK/'sources/PR3967/research/r437-oq4-caller-binding/physical_probe.py'
CURRENT = TASK/'word-search/physical_probe.py'
RUNTIME = TASK/'word-search/PHYSICAL-PROBE.json'


def need(ok,message):
    if not ok:
        raise AssertionError(message)


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=HERE/'PHYSICAL-PROBE-STATIC-REVIEW.json')
    args = ap.parse_args()
    expected = {ORIGINAL:'4fb0958485d7bd3d77435d882c91f4a9462ac877b0bd99cbd55d0db505a35460',
                CURRENT:'1e69a2992323d2724ff686f91769cc1510d1e94107308f2897945fb2c109b145',
                RUNTIME:'06ddcf4bb17415dadefeb36481e37551b9b01256b14238931017d3a3357b0ea9'}
    for path,pin in expected.items():
        need(sha256(path.read_bytes()).hexdigest() == pin,'exact independently reviewed source/receipt '+path.name)
    runtime = json.loads(RUNTIME.read_text())
    for name,pin in runtime['source_sha256'].items():
        need(sha256((REPO/name).read_bytes()).hexdigest() == pin,'runtime source binding '+name)
    need(runtime['status'] == 'PASS_ACTUAL_T35_AC_WORD_NESTED_PHYSICAL_PROTOCOL','successful actual runtime receipt')
    first,second = 2048*42//64,2048*42*7//(64*64)
    need(2048*42 % 64 == 0 and first*7 % 64 == 0 and [2048,first,second] == runtime['widths'] == [2048,1344,147],
         'both nested grants are exact integers with correct ranks')
    gaps = [2*(2048-first),2*(2048-second)]
    need(gaps == runtime['gap_exponents'] == [1408,3802], 'root and nested unused-stock gap exponents')
    need(runtime['coefficient_coordinates'] == [0,second-1] and runtime['coefficients'] == [2,2], 'both controlled child endpoint coefficients')
    need(runtime['rejected_gates'] == ['wrong_parent','foreign_program','wrong_source'], 'all three original rejecting physical gates retained')
    need(runtime['semantic_rejections'] == ['obsolete_rank26','obsolete_rank34','foreign_COPY_prefix','foreign_replica_COPY_prefix'],
         'obsolete-rank and both foreign-source semantic controls reject')
    need(runtime['counts']['calls'] == runtime['counts']['returns'] == 2, 'two completed nested CALL/RETURN pairs')
    need(runtime['ancestor_request'] == 965276 and runtime['copy_request'] == 4518 and
         runtime['ancestor_replica'] == runtime['copy_replica'] == 1 and runtime['foreign_copy_replica'] == 2,
         'actual new owner and distinct global replica bindings')
    need(runtime['controlled_payload_bits'] == 46 and runtime['controlled_fibre_bits'] == 23 and
         runtime['complete_GL64_payload_executed'] is False and runtime['stock_is_controlled_fixture'] is True,
         'finite controlled scope retained without universal GL64 execution claim')
    result = {'status':'PASS_SOURCE_BOUND_STATIC_REVIEW_OF_CONTROLLED_T35_PHYSICAL_PROBE',
              'source_sha256':{p.relative_to(REPO).as_posix():sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__),ORIGINAL,CURRENT,RUNTIME)},
              'review_method':'Independent line diff against exact PR3967 predecessor; runtime receipt inspection; direct integer grant/capsule arithmetic. The expensive physical caller was executed by the word track, not independently rerun by this review.',
              'review_findings':[
                  'All nested tape, lease, rollback, SOURCE/ADDRESS/PC immutability, evaluator-state and final borrowed caller restoration checks remain.',
                  'The old rank34 semantic control is retained; obsolete rank26 and foreign replica2 COPY-prefix controls are added.',
                  'The ancestor binds the actual newly freed rank42 stage6 replica1 family1097 idle owner. The COPY binds actual frame515 stage0 replica1 and the updated literal IR window.',
                  'The two exact grant ratios are42/64 and7/64; both descendants remain nonterminal.',
                  'The46bit controlled payload scope is explicit. This review and probe do not execute a universal GL64 packet or prove inherited all-size interfaces.'
              ],
              'widths':[2048,first,second],'gap_exponents':gaps,
              'retained_physical_rejection_controls':runtime['rejected_gates'],
              'semantic_rejection_controls':runtime['semantic_rejections'],
              'scope':'Static source review and arithmetic/receipt verification of the controlled finite physical protocol; no independent rerun or human review is asserted.'}
    with args.out.open('x') as handle:
        json.dump(result,handle,sort_keys=True,indent=2); handle.write('\n')
    print(result['status'])


if __name__ == '__main__':
    main()
