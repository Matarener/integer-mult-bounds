#!/usr/bin/env python3
"""Recheck the saved width8 dual and reprice the achieved BIT local words.

Pure standard-library rational arithmetic, with no LP or orbit search rerun.
This transfers only the unchanged width8/controller premises; it does not
transfer the old fixed-scalar-graph entrance obstruction.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENGINE = HERE/'geometry_budget.py'
spec = importlib.util.spec_from_file_location('independent_geometry_tariff',ENGINE)
engine = importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)


def main():
    saved_path = HERE/'GEOMETRY-BUDGET.json'
    saved = json.loads(saved_path.read_bytes())['arbitrary_nine_segment_target']
    a = Q(saved['parameter']); assert a == Q('.001745')
    lam = Q(saved['dual_multiplier'])
    dual = {int(d):Q(p) for d,p in saved['dual_segment_lower_prices'].items()}
    constraints = []
    for delta in range(1,7):
        for count in range(7*delta//8+1):
            residual = 7*delta-8*count
            slack = engine.tariff(residual,a)[0]+lam*count-dual[delta]
            assert slack >= 0
            constraints.append({'delta':delta,'width8_helpers':count,'residual_rank':residual,'rational_slack':str(slack)})
    partitions = [ds for ds in combinations_with_replacement(range(1,7),9) if sum(ds) == 27]
    assert len(partitions) == 88
    base = {1:1322,2:1342,3:74,4:46,5:103,6:10,7:18}
    cases = [
      ('checkpoint','14cd9ec8f8deb6e16364e550878a5cb4e3da3550d6969a39e94fe786957a1a48',
       {1:1322,2:1340,3:75,4:46,5:102,6:11,7:18}),
      ('retimed444','ddc4f70ef7e0721f25bc5a2027ec09671457384aeb22b45f1a7dae33dae6482a',
       {1:1323,2:1338,3:76,4:46,5:102,6:11,7:18}),
      ('early-birth-prefixes','f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908',
       {1:1330,2:1327,3:79,4:49,5:90,6:20,7:18})]
    old_path = REPO/'research/kappa-next-regime/word-search/candidate/WORD.json.gz'
    oldword = json.loads(gzip.decompress(old_path.read_bytes()))
    orbit_path = HERE/'controller-orbits/K4.json'
    orbit_script = HERE/'controller_clock_orbits.py'
    orbit = json.loads(orbit_path.read_bytes())
    assert orbit['script_sha256'] == sha256(orbit_script.read_bytes()).hexdigest()
    assert orbit['status'] == 'EXACT_FINITE_CLOCK_ORBIT_SEARCH_COMPLETE'
    assert (orbit['K'],orbit['stages'],orbit['budget_before_final'],orbit['minimum_final_idle_segments_found']) == (4,9,6,9)
    assert orbit['maximum_idle_jump'] is None
    rows = []; sources = [Path(__file__),saved_path,ENGINE,engine.PRICE,old_path,
                          orbit_path,orbit_script,HERE/'CLOCK-MODEL-PROOF.md',
                          HERE/'verify_clock_reductions.py',HERE/'CLOCK-REDUCTIONS-CHECK.json']
    for name,digest,profile in cases:
        path = HERE.parent/'bit-word'/name/'WORD.json.gz'; sources.append(path)
        word = json.loads(gzip.decompress(path.read_bytes()))
        assert sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest() == digest
        assert all(word[k] == oldword[k] for k in ('h','v','R','start','final','ret','scatter'))
        assert word['R'] == 437 and word['start'][222:] == [0]*437 and word['final'][222:] == [1]*437
        # The independent complete local audit binds this asserted histogram
        # to every literal move; pin it instead of rerunning scalar emission.
        receipt_path = HERE/{'checkpoint':'BIT-CHECKPOINT-INDEPENDENT-REVIEW.json',
                           'retimed444':'BIT-RETIMED444-INDEPENDENT-REVIEW.json',
                           'early-birth-prefixes':'BIT-FINAL-INDEPENDENT-REVIEW.json'}[name]
        receipt = json.loads(receipt_path.read_bytes()); sources.append(receipt_path)
        assert receipt['word_canonical_sha256'] == digest
        observed = receipt.get('local_profile',receipt.get('profile'))
        assert {int(r):n for r,n in observed.items()} == profile
        assert sum(r*n for r,n in profile.items()) == 5113
        changes = Counter(profile); changes.subtract(base)
        local = engine.combine(profile,a)[0]
        candidates = [((9*local+222*sum(dual[d] for d in ds)-lam*9*437)/(64*888),ds) for ds in partitions]
        candidates.sort(); minimum,ds = candidates[0]
        assert minimum > 1
        rows.append({'word':name,'word_canonical_sha256':digest,'profile':profile,
                     'delta_from_previous_permanent_carrier_word':{r:n for r,n in changes.items() if n},
                     'all_88_partitions_reject_target':True,'best_relaxed_partition':list(ds),
                     'minimum_normalized_moment_lower':str(minimum),
                     'minimum_normalized_moment_minus_one_lower':str(minimum-1),
                     'decimal_margin':engine.decimal(minimum-1)})
    result = {'status':'EXACT_SAVED_DUAL_RECHECK_REJECTS_TARGET_FOR_ALL_ACHIEVED_BIT_WORDS',
              'target':str(a),'partition_count':len(partitions),'packing_dual_constraints':constraints,
              'fallback_charged':0,'rows':rows,
              'scope':'Integral dual-bridge four-pair controller, nine local calls, ordinary signed exchange, common monotone pair clocks, unchanged complete width8 helper inventory. The source-bound orbit proof gives at least nine idle segments and the dormant-span lemma gives maximum six. Full pooling, unrestricted chronological owner eligibility, and omitted fallback all favor the construction. Arbitrary nonintegral bridges or changed width/flag laws remain outside.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'ACHIEVED-BIT-CLOCK-REPRICE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],[(r['word'],r['decimal_margin']) for r in rows],flush=True)


if __name__ == '__main__':
    main()
