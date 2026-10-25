#!/usr/bin/env python3
"""Independent final BIT source, dirty interface, native and invoice review.

No current constructor, optimizer, emitter, integrator or production price
engine is imported. Only the preceding independent standard-library audit
algebra and rational tails are reused. Apache-2.0; substantial OpenAI
assistance. The explicit complete word is the independently replayed input.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_source_review',HERE/'review_bit_checkpoint.py')
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
review,price,read,canonical = audit.review,audit.price,audit.read,audit.canonical
WORD = HERE.parent/'bit-word/early-birth-prefixes/WORD.json.gz'
PARENT = HERE.parent/'bit-word/retimed444/WORD.json.gz'
INTEGRATED = HERE.parent/'bit-integration/early-birth-prefixes'
EXPECTED = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'
EXPECTED_PROFILE = {1:1330,2:1327,3:79,4:49,5:90,6:20,7:18}


def complete_invoice(details,programs):
    invoice = read(INTEGRATED/'RESULT.json')
    assert invoice['word_content_sha256'] == EXPECTED
    for name,digest in invoice['source_sha256'].items():
        assert sha256((audit.REPO/name).read_bytes()).hexdigest() == digest
    template = read(INTEGRATED/'GLOBAL-TEMPLATE.json.gz')
    previous = read(audit.OLD/'geometry-search/pool35-word/GLOBAL-TEMPLATE.json.gz')
    assert sha256(canonical(template)).hexdigest() == invoice['template_content_sha256']
    assert set(template) == set(previous)
    for key in previous:
        if key not in ('version','local_programs','source_record_sha256','calls','local_word_override'):
            assert template[key] == previous[key], 'unchanged physical field '+key
    override = template['local_word_override']
    assert override['word_content_sha256'] == EXPECTED
    assert override['parent_template_content_sha256'] == sha256(canonical(previous)).hexdigest()
    assert override['local_programs'] == invoice['local_programs']
    assert template['source_record_sha256'] == invoice['source_record_sha256']
    assert all(p['source_record_sha256'] == template['source_record_sha256'] for p in override['local_programs'].values())
    assert template['local_programs'] == programs
    assert len(template['calls']) == len(previous['calls']) == 315
    profile = Counter()
    for before,after in zip(previous['calls'],template['calls']):
        assert set(before) == set(after)
        assert all(before[k] == after[k] for k in before if k != 'local_hash')
        orientation = after['orientation']
        digest = sha256(json.dumps(programs[orientation],separators=(',',':')).encode()).hexdigest()
        assert digest == after['local_hash'] == invoice['local_programs'][orientation]['sha256']
        profile.update(details[orientation]['profile'])
    idles = read(INTEGRATED/'IDLE-INVENTORY.json.gz')
    assert idles == read(audit.OLD/'geometry-search/pool35-word/IDLE-INVENTORY.json.gz')
    assert read(INTEGRATED/'OWNER-INVENTORY.json.gz') == read(audit.OLD/'geometry-search/pool35-word/OWNER-INVENTORY.json.gz')
    assert len(idles) == 69930
    profile.update(row[-1] for row in idles)
    assert dict(sorted(profile.items())) == {int(r):n for r,n in invoice['profile'].items()}
    E = sum(profile.values()); mass = sum(r*n for r,n in profile.items())
    assert E == invoice['paid_requests'] == 987525
    assert mass == 1977885
    T,W,m,R,V,L,N = 35,31080,64,437,111,9,128
    assert m*W-mass == 11235
    pf,pb = details['forward']['prefix_l1'],details['reverse']['prefix_l1']
    assert (pf,pb) == (49281,1052208)
    prefix = (2**18*pf**5*pb**4)**5
    episodes = 9*L*T
    J = 8*T*L*(2*V+R)+8*(8*V*T)+2*L*T*R+2*episodes
    source_geometry = read(audit.OLD/'sources/PR3647/research/bit-p111-r437-gl464-470-20261018/data/GEOMETRY.json')
    common = {'unit':L*T*details['forward']['adds']+18*V*T,
              'J_times_high':J*16*(m*m+1)**2,'J_times_physical':J*(W+9),
              'E_times_good':E*(8*m*m+8),'E_times_compiler':E*128*N**3,
              'matrix_test':16*m**3,'copy_erase_episodes':episodes,
              'selectors':2*L*T*((W-1)+R*m*(source_geometry['max_route_factors']+144+2+(m-1)+m)),
              'one':1}
    bill = invoice['coefficient_invoice']
    assert {k:str(v) for k,v in common.items()} == bill['components_without_prefix']
    coefficient = prefix+sum(common.values()); two = (coefficient+1)**2*(E+1)**2
    assert (prefix,coefficient,two) == tuple(int(bill[k]) for k in ('five_replica_prefix','coefficient','two_level_coefficient'))
    assert prefix.bit_length() == bill['prefix_bits']
    assert prefix < 2**bill['charged_prefix_bits'] == 2**896
    assert two < 2**bill['charged_two_level_bits'] == 2**1856
    assert bill['ROW'] == 2*(m*m+1)+9909+252 == 18355 < bill['ROW_cap'] == 20161
    assert 2*max(profile)**2 < m*m
    endpoints = Q(invoice['bit_endpoint_lower']),Q(invoice['bit_endpoint_upper'])
    assert endpoints[1]-endpoints[0] == Q(1,10**24)
    signs = []
    for label,a in zip(('lower','upper'),endpoints):
        lo,hi = price.moment(profile,m,W,a,32*m*m*E)
        assert hi < 1 if label == 'lower' else lo > 1
        signs.append({'endpoint':str(a),'moment_lower':str(lo),'moment_upper':str(hi)})
    return {'all_315_native_programs_bound':True,'all_physical_owners_and_idles_unchanged':True,
            'profile':dict(sorted(profile.items())),'paid_requests':E,'rank_mass':mass,
            'independent_third_engine_signs':signs,'coefficient_components_recomputed':True,
            'five_replica_prefix_bits':prefix.bit_length(),'two_level_coefficient_bits':two.bit_length(),
            'charged_prefix_bits':896,'charged_two_level_bits':1856,'ROW':18355,
            'source_record_sha256':invoice['source_record_sha256'],
            'template_content_sha256':invoice['template_content_sha256'],
            'scope':'Complete finite BIT invoice and retained owner binding; no independent all-size or combined-complex claim.'}


def main():
    parent,word = read(PARENT),read(WORD)
    assert sha256(canonical(word)).hexdigest() == EXPECTED
    old = read(audit.PARENT_WORD)
    review.geometry(old)
    dims,masks = audit.geometry(old,word)
    assert all(parent[k] == word[k] for k in parent if k not in ('A','B','C','D'))
    assert word['C'] == [[1,d,ss] for f,d,ss in reversed(word['A']+word['B']) if not 111 <= d < 222]
    assert all(not 111 <= d < 222 for f,d,ss in word['A']+word['C'])
    assert all(f == 0 and 111 <= d < 222 and all(s >= 222 for s in ss) for f,d,ss in word['D'])
    review.raw_compensation(word)
    before,after = review.replay(parent,dims,masks),review.replay(word,dims,masks)
    assert after['profile'] == EXPECTED_PROFILE
    assert after['rank_mass'] == before['rank_mass'] == 5113
    assert after['scalar_ADDs'] == {'A':2130,'B':932,'C':2627,'D':17573,'SCATTER':527}
    delta = Counter(after['profile']); delta.subtract(before['profile'])
    source_mask = (1 << 111)-1
    captures = []
    assert len(before['captures']) == len(after['captures']) == 9
    for a,b in zip(before['captures'],after['captures']):
        assert all(a[k] == b[k] for k in a if k != 'full_row_hex')
        old_row,new_row = int(a['full_row_hex'],16),int(b['full_row_hex'],16)
        assert old_row & source_mask == new_row & source_mask
        captures.append({'role':b['role'],'frame':b['frame'],'rank':b['rank'],
                         'SOURCE_row_unchanged':True,'full_dirty_row_unchanged':old_row == new_row,
                         'dirty_difference_hex':hex(old_row^new_row)})
    changed = [r for r in range(659) if before['paths'][r] != after['paths'][r]]
    gauges = review.exact_changed_gauges(word,before['paths'],after['paths'],changed,dims)
    columns = review.column_check(word)
    programs,details = price.record_programs(word)
    assert all(d['profile'] == EXPECTED_PROFILE and d['adds'] == 23789 and d['events'] == 26711 for d in details.values())
    assert (details['forward']['prefix_l1'],details['reverse']['prefix_l1']) == (49281,1052208)
    wanted = review.whole_rows(word); controls = []
    for name,replacement in [('D',[]),('D',parent['D']),('C',parent['C'])]:
        bad = deepcopy(word); bad[name] = replacement
        assert review.whole_rows(bad) != wanted
        controls.append({'mutated_section':name,'kind':'deleted' if not replacement else 'stale retimed444 section','rejected':True})
    underpriced = deepcopy(word); underpriced['A'][0][0] = 0
    try:
        review.replay(underpriced,dims,masks)
    except AssertionError:
        controls.append({'kind':'underpaid first SOURCE birth at zero frame','rejected':True})
    else:
        raise AssertionError('underpaid first birth escaped')
    invoice = complete_invoice(details,programs)
    sources = [Path(__file__),HERE/'review_bit_checkpoint.py',audit.REVIEW,audit.PRICE,WORD,PARENT,
               audit.PARENT_WORD,INTEGRATED/'RESULT.json',INTEGRATED/'GLOBAL-TEMPLATE.json.gz',
               INTEGRATED/'OWNER-INVENTORY.json.gz',INTEGRATED/'IDLE-INVENTORY.json.gz']
    result = {'status':'PASS_INDEPENDENT_FINAL_BIT_DIRTY_INTERFACE_NATIVE_PROGRAM_AND_COMPLETE_INVOICE_REVIEW',
              'word_canonical_sha256':EXPECTED,'exact_frames_checked':len(dims),'local_profile':EXPECTED_PROFILE,
              'delta_from_retimed444':{r:n for r,n in delta.items() if n},'scalar_ADDs':after['scalar_ADDs'],
              'D_equals_complete_raw_dirty_response':True,'C_is_literal_full_inverse':True,
              'columns':columns,'captures':captures,
              'changed_frame_paths':[{'role':r,'old':before['paths'][r],'new':after['paths'][r]} for r in changed],
              'all_changed_path_gauges':gauges,'native_program_details':details,
              'rejecting_controls':controls,'complete_invoice':invoice,
              'scope':'Independent local/interface and finite full-invoice review using preceding independent standard-library tools. No current constructor, optimizer, emitter, integrator or production price engine is imported. Native five-stage881-column and full global replay are separate evidence. Full physical and all-size interfaces remain conditional; this is not a combined-complex claim.',
              'source_sha256':{str(p.relative_to(audit.REPO)):sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'BIT-FINAL-INDEPENDENT-REVIEW.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'frames',len(dims),'changed paths',len(changed),'gauge identities',gauges['distinct_transitions_checked'],flush=True)


if __name__ == '__main__':
    main()
