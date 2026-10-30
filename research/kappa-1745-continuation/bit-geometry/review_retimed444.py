#!/usr/bin/env python3
"""Independent literal reconstruction and invoice review of helper444 retiming.

No current word constructor, optimizer, emitter or integrator is imported.
The only imported audit uses the previous independent standard-library
algebra and price primitives. Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_checkpoint_review',HERE/'review_bit_checkpoint.py')
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
review = audit.review
WORD = HERE.parent/'bit-word/retimed444/WORD.json.gz'
EXPECTED = 'ddc4f70ef7e0721f25bc5a2027ec09671457384aeb22b45f1a7dae33dae6482a'


def main():
    before,word = audit.read(audit.WORD),audit.read(WORD)
    assert sha256(audit.canonical(before)).hexdigest() == audit.EXPECTED_WORD
    assert sha256(audit.canonical(word)).hexdigest() == EXPECTED
    assert set(before) == set(word)
    assert all(before[k] == word[k] for k in before if k not in ('A','C'))
    birth = [186,444,[77]]
    assert before['A'].count(birth) == 1 and before['A'][2029] == birth
    assert before['start'][77] == 79
    assert not any(444 in [d]+ss for f,d,ss in before['A'][:2029])
    assert all(d >= 111 for f,d,ss in before['A']), 'A does not write any SOURCE'
    expected = deepcopy(before)
    expected['A'] = [[79,444,[77]]]+before['A'][:2029]+before['A'][2030:]
    expected['C'] = [[1,d,ss] for f,d,ss in reversed(expected['A']+expected['B']) if not 111 <= d < 222]
    assert word == expected, 'sole literal birth move and inverse cleanup reconstruction'
    a = [1 << r for r in range(659)]; b = a[:]
    for rows,gates in ((a,before['A']),(b,word['A'])):
        for f,d,s in review.flatten(gates):
            rows[d] ^= rows[s]
    assert a == b, 'all 659 full arbitrary-column A output rows equal'
    old_boundary = audit.read(audit.PARENT_WORD)
    dims,masks = audit.geometry(old_boundary,word)
    old,new = review.replay(before,dims,masks),review.replay(word,dims,masks)
    assert old['captures'] == new['captures'], 'all nine complete dirty captures identical to checkpoint'
    assert review.whole_rows(before) == review.whole_rows(word)
    review.raw_compensation(word)
    delta = Counter(new['profile']); delta.subtract(old['profile'])
    delta = {r:n for r,n in delta.items() if n}
    assert delta == {1:1,2:-2,3:1}
    assert new['profile'] == {1:1323,2:1338,3:76,4:46,5:102,6:11,7:18}
    changed = [r for r in range(659) if old['paths'][r] != new['paths'][r]]
    gauges = review.exact_changed_gauges(word,old['paths'],new['paths'],changed,dims)
    columns = review.column_check(word)
    programs,details = audit.price.record_programs(word)
    assert all(d['profile'] == new['profile'] and d['adds'] == 23795 and d['events'] == 26718 for d in details.values())
    assert (details['forward']['prefix_l1'],details['reverse']['prefix_l1']) == (53147,1197292)
    bad = deepcopy(word); bad['A'][0][0] = 0
    try:
        review.replay(bad,dims,masks)
    except AssertionError:
        rejected = True
    else:
        raise AssertionError('underpaid first birth contact escaped')
    audit.INTEGRATED = HERE.parent/'bit-integration/retimed444'
    audit.EXPECTED_WORD = EXPECTED
    invoice = audit.full_profile_and_price(word,details,programs)
    paths = [Path(__file__),HERE/'review_bit_checkpoint.py',audit.REVIEW,audit.PRICE,
             audit.WORD,WORD,audit.INTEGRATED/'RESULT.json',audit.INTEGRATED/'GLOBAL-TEMPLATE.json.gz',
             audit.INTEGRATED/'OWNER-INVENTORY.json.gz',audit.INTEGRATED/'IDLE-INVENTORY.json.gz']
    result = {'status':'PASS_INDEPENDENT_LITERAL_BIRTH_RETIMING_AND_COMPLETE_INVOICE_REVIEW',
              'word_canonical_sha256':EXPECTED,'literal_reconstruction':True,
              'A_659_full_rows_unchanged':True,'nine_complete_dirty_captures_unchanged_from_checkpoint':True,
              'D_and_B_unchanged':True,'C_literal_regenerated':True,'exact_rational_frames':len(dims),
              'profile':new['profile'],'delta_from_checkpoint':delta,'columns':columns,
              'changed_paths':[{'role':r,'old':old['paths'][r],'new':new['paths'][r]} for r in changed],
              'exact_changed_gauges':gauges,'native_program_details':details,
              'underpaid_birth_control_rejected':rejected,'complete_invoice':invoice,
              'scope':'Independent finite BIT supplier review. Full dirty capture identity is relative to the resynthesized checkpoint, not the older permanent-carrier word. No all-size or combined-complex assertion.',
              'source_sha256':{str(p.relative_to(audit.REPO)):sha256(p.read_bytes()).hexdigest() for p in paths}}
    (HERE/'BIT-RETIMED444-INDEPENDENT-REVIEW.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'profile',new['profile'],'changed paths',changed,flush=True)


if __name__ == '__main__':
    main()
