#!/usr/bin/env python3
"""Independent literal review of the source-resynthesis BIT checkpoint.

Reuses only the previous independent review's standard-library algebra and
rational price primitives. No current constructor, optimizer, xcheck,
native emitter, integrator, or production price engine is imported.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
REPO = HERE.parents[2]
OLD = REPO/'research/kappa-next-regime'
WORD = TASK/'bit-word/checkpoint/WORD.json.gz'
PARENT_WORD = OLD/'word-search/candidate/WORD.json.gz'
REVIEW = OLD/'width-search/review_composed_word.py'
PRICE = OLD/'width-search/review_invoice_outer.py'
INTEGRATED = TASK/'bit-integration/checkpoint'
EXPECTED_WORD = '14cd9ec8f8deb6e16364e550878a5cb4e3da3550d6969a39e94fe786957a1a48'


def load(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


review = load(REVIEW,'previous_independent_local_review')
price = load(PRICE,'previous_independent_invoice_review')


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(',',':')).encode()


def geometry(parent,word):
    for key in ('h','v','R','form','lines','start','final','ret','scatter','ports_geom','punctured'):
        assert word[key] == parent[key], 'unchanged boundary '+key
    assert word['frames'][:len(parent['frames'])] == parent['frames']
    assert len(parent['frames']) == 636 and len(word['frames']) == 758
    dims,masks = [],[]
    for frame in word['frames']:
        assert len(frame) == len(set(frame)) and all(0 <= t < 111 for t in frame)
        basis = review.basis([word['lines'][t] for t in frame])
        actual = {t for t,line in enumerate(word['lines']) if not any(review.remainder(line,basis))}
        assert actual == set(frame), 'exact rational frame closure'
        dims.append(len(basis)); masks.append(sum(1 << t for t in frame))
    assert dims[0] == 0 and dims[1] == 8
    assert word['start'][111:] == [0]*548 and word['final'][222:] == [1]*437
    for t,line in enumerate(word['lines']):
        assert len(line) == 8 and sum(x*x for x in line) == 4
        assert dims[word['start'][t]] == 1 and t in word['frames'][word['start'][t]]
        assert word['final'][t] == 1
        expected = {s for s,other in enumerate(word['lines']) if sum(a*b for a,b in zip(line,other)) == 0}
        assert set(word['frames'][word['final'][111+t]]) == expected
        assert dims[word['final'][111+t]] == 7
    return dims,masks


def full_profile_and_price(word,details,programs):
    invoice = read(INTEGRATED/'RESULT.json')
    assert invoice['word_content_sha256'] == EXPECTED_WORD
    for name,digest in invoice['source_sha256'].items():
        assert sha256((REPO/name).read_bytes()).hexdigest() == digest
    template = read(INTEGRATED/'GLOBAL-TEMPLATE.json.gz')
    original = read(OLD/'geometry-search/pool35-word/GLOBAL-TEMPLATE.json.gz')
    assert sha256(canonical(template)).hexdigest() == invoice['template_content_sha256']
    for key in original:
        if key not in ('version','local_programs','source_record_sha256','calls','local_word_override'):
            assert template[key] == original[key], 'unchanged physical template '+key
    override = template['local_word_override']
    assert override['word_content_sha256'] == EXPECTED_WORD
    assert override['parent_template_content_sha256'] == sha256(canonical(original)).hexdigest()
    assert override['local_programs'] == invoice['local_programs']
    assert template['source_record_sha256'] == invoice['source_record_sha256']
    assert all(p['source_record_sha256'] == template['source_record_sha256'] for p in override['local_programs'].values())
    assert template['local_programs'] == programs
    profile = Counter()
    for before,after in zip(original['calls'],template['calls']):
        assert all(before[k] == after[k] for k in before if k != 'local_hash')
        orientation = after['orientation']
        digest = sha256(json.dumps(programs[orientation],separators=(',',':')).encode()).hexdigest()
        assert digest == after['local_hash'] == invoice['local_programs'][orientation]['sha256']
        profile.update(details[orientation]['profile'])
    assert len(template['calls']) == len(original['calls']) == 315
    ids = read(INTEGRATED/'IDLE-INVENTORY.json.gz')
    assert ids == read(OLD/'geometry-search/pool35-word/IDLE-INVENTORY.json.gz')
    assert read(INTEGRATED/'OWNER-INVENTORY.json.gz') == read(OLD/'geometry-search/pool35-word/OWNER-INVENTORY.json.gz')
    assert len(ids) == 69930
    profile.update(row[-1] for row in ids)
    assert dict(sorted(profile.items())) == {int(r):n for r,n in invoice['profile'].items()}
    assert sum(profile.values()) == invoice['paid_requests'] == 987840
    assert sum(r*n for r,n in profile.items()) == 1977885
    T,W,m,R,V,L,N = 35,31080,64,437,111,9,128
    E = sum(profile.values())
    assert m*W-sum(r*n for r,n in profile.items()) == 11235
    pf,pb = details['forward']['prefix_l1'],details['reverse']['prefix_l1']
    assert (pf,pb) == (53147,1197292)
    prefix = (2**18*pf**5*pb**4)**5
    episodes = 9*L*T
    J = 8*T*L*(2*V+R)+8*(8*V*T)+2*L*T*R+2*episodes
    geometry_path = OLD/'sources/PR3647/research/bit-p111-r437-gl464-470-20261018/data/GEOMETRY.json'
    source_geometry = read(geometry_path)
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
    assert prefix.bit_length() == bill['prefix_bits'] == 887
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
            'profile':dict(sorted(profile.items())),'paid_requests':E,'rank_mass':1977885,
            'independent_third_engine_signs':signs,'coefficient_components_recomputed':True,
            'five_replica_prefix_bits':887,'charged_prefix_bits':896,'charged_two_level_bits':1856,
            'ROW':18355,'scope':'Complete finite BIT invoice and retained owner binding; no independent all-size or combined-complex claim.'}


def main():
    parent,word = read(PARENT_WORD),read(WORD)
    assert sha256(canonical(word)).hexdigest() == EXPECTED_WORD
    # First validate the already reviewed immutable boundary, then every new
    # rational frame rather than accepting its integer dimension annotation.
    review.geometry(parent)
    dims,masks = geometry(parent,word)
    expected_cleanup = [[1,d,ss] for _,d,ss in reversed(word['A']+word['B']) if not 111 <= d < 222]
    assert word['C'] == expected_cleanup
    assert all(not 111 <= d < 222 for _,d,_ in word['A']+word['C'])
    assert all(f == 0 and 111 <= d < 222 and all(s >= 222 for s in ss) for f,d,ss in word['D'])
    review.raw_compensation(word)
    old,new = review.replay(parent,dims,masks),review.replay(word,dims,masks)
    assert new['profile'] == {1:1322,2:1340,3:75,4:46,5:102,6:11,7:18}
    assert new['rank_mass'] == old['rank_mass'] == 5113
    delta = Counter(new['profile']); delta.subtract(old['profile'])
    assert {r:n for r,n in delta.items() if n} == {2:-2,3:1,5:-1,6:1}
    source_mask = (1 << 111)-1
    captures = []
    for before,after in zip(old['captures'],new['captures']):
        assert all(before[k] == after[k] for k in before if k != 'full_row_hex')
        old_row,new_row = int(before['full_row_hex'],16),int(after['full_row_hex'],16)
        assert old_row & source_mask == new_row & source_mask
        captures.append({'role':after['role'],'frame':after['frame'],'rank':after['rank'],
                         'SOURCE_row_unchanged':True,'full_dirty_row_unchanged':old_row == new_row,
                         'dirty_difference_hex':hex(old_row^new_row)})
    changed = [r for r in range(659) if old['paths'][r] != new['paths'][r]]
    assert [r for r in changed if r < 111] == [92]
    assert old['paths'][92] == [94,184,509,381,544,1]
    assert new['paths'][92] == [94,509,381,544,1]
    assert changed == [92,128,463,469]
    assert old['paths'][128] == [0,184,542] and new['paths'][128] == [0,94,542]
    gauges = review.exact_changed_gauges(word,old['paths'],new['paths'],changed,dims)
    columns = review.column_check(word)
    programs,details = price.record_programs(word)
    assert all(d['profile'] == new['profile'] and d['adds'] == 23795 and d['events'] == 26718 for d in details.values())
    controls = []
    expected = review.whole_rows(word)
    for key,replacement in [('D',[]),('D',parent['D']),('C',parent['C'])]:
        changed_word = deepcopy(word); changed_word[key] = replacement
        assert review.whole_rows(changed_word) != expected
        controls.append({'mutated_section':key,'kind':'deleted' if not replacement else 'stale incumbent','rejected':True})
    # Force SOURCE92's first new contact to the uncharged zero frame. The
    # endpoint algebra survives the frame edit, but exact frame legality fails.
    underpriced = deepcopy(word)
    section_index = next(i for i,(f,d,ss) in enumerate(underpriced['A']) if 92 in [d]+ss)
    underpriced['A'][section_index][0] = 0
    try:
        review.replay(underpriced,dims,masks)
    except AssertionError:
        controls.append({'mutated_section':'A','kind':'underpaid SOURCE92 first contact','rejected':True})
    else:
        raise AssertionError('underpaid SOURCE92 frame escaped')
    invoice = full_profile_and_price(word,details,programs)
    source_paths = [WORD,PARENT_WORD,REVIEW,PRICE,Path(__file__),INTEGRATED/'RESULT.json',
                    INTEGRATED/'GLOBAL-TEMPLATE.json.gz',INTEGRATED/'OWNER-INVENTORY.json.gz',
                    INTEGRATED/'IDLE-INVENTORY.json.gz']
    result = {'status':'PASS_INDEPENDENT_SOURCE_RESYNTHESIS_DIRTY_FRAME_CAPTURE_AND_FULL_INVOICE_REVIEW',
              'word_canonical_sha256':EXPECTED_WORD,'exact_frames_checked':758,
              'old_catalogue_retained':636,'new_exact_rational_frames':122,
              'local_profile':new['profile'],'local_delta':{r:n for r,n in delta.items() if n},
              'scalar_ADDs':new['scalar_ADDs'],'D_equals_complete_raw_dirty_response':True,
              'C_is_literal_full_inverse':True,'columns':columns,'captures':captures,
              'changed_frame_paths':[{'role':r,'old':old['paths'][r],'new':new['paths'][r]} for r in changed],
              'all_changed_path_gauges':gauges,'native_program_details':details,
              'rejecting_controls':controls,'complete_invoice':invoice,
              'scope':'Independent local/interface and finite full-invoice review using preceding independent standard-library tools. No current optimizer/emitter/integrator is imported. Native five-stage881-column replay is upstream evidence, not rerun independently here; full physical and all-size interfaces remain conditional.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in source_paths}}
    (HERE/'BIT-CHECKPOINT-INDEPENDENT-REVIEW.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'frames',len(dims),'changed paths',len(changed),
          'capture dirty changes',sum(not row['full_dirty_row_unchanged'] for row in captures),
          'bit',invoice['independent_third_engine_signs'][0]['endpoint'],flush=True)


if __name__ == '__main__':
    main()
