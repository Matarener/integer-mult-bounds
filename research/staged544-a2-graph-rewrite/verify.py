#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only source-authenticated A2 rewrite certificate replay."""
import argparse,gzip,hashlib,json,time,types
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def module(name,path):
    m=types.ModuleType(name);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def authenticate(raw,row):
    need(len(raw)==row['bytes'],'source length '+row['local'])
    need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256 '+row['local'])
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob '+row['local'])

def setup():
    for row in json.loads((P/'SOURCES.json').read_text())['snapshots']:authenticate((P/row['local']).read_bytes(),row)
    return module('graph_search',P/'search.py'),module('retained_core',P/'vendor/audit_core.py'),module('retained_semantics',P/'vendor/audit_verify.py')

def load(tag):return json.loads(gzip.decompress((P/f'inputs/BORROW-WORD-43{tag}.json.gz').read_bytes()))

def normal(x):return json.loads(json.dumps(x,sort_keys=True))

def coefficient_heights(word,records):
    from fractions import Fraction
    replacement=[Fraction(g[3],g[4]) for row in records for g in row['gates']]
    complete=list(replacement)
    for section in ('precondition','compensation','A','cut','B','restore','cleanup'):
        for g in word[section]:
            if g[0]=='add':complete.append(Fraction(g[3],g[4]))
            elif g[0]=='scale':complete.append(Fraction(g[2],g[3]))
    complete.extend(Fraction(c['coefficient']) for c in word['initial_corrections'])
    result={}
    for name,values in [('replacement_gates',replacement),('complete_words',complete)]:
        result['maximum_'+name+'_numerator_bits']=max(abs(x.numerator).bit_length() for x in values)
        result['maximum_'+name+'_denominator_bits']=max(x.denominator.bit_length() for x in values)
    return result

def current_producer(tag,S,C,A):
    word=json.loads(gzip.decompress((P/f'inputs/PR3945-WORD-{tag}.json.gz').read_bytes()))
    C.hygiene(word);profile,widths,*_=C.frame_bill(word)
    need(profile=={int(r):n for r,n in word['report']['local_profile'].items()},'PR3945 source invoice')
    need(C.derive_cleanup(word)==word['cleanup'],'PR3945 source cleanup')
    block=word['A'][1858:1861]
    expected=[['add',457,475,-1,1,[82,42]],['add',456,457,1,1,[82,42]],['add',456,475,1,1,[82,42]]]
    need(block==expected,'PR3945 literal motif changed')
    nodes,where,bill=S.R.tracing(word);need(bill==profile,'PR3945 trace invoice')
    contracted=S.contract(word,C,[['A',1858,2]],nodes,where,bill)
    need(len(contracted['records'])==1,'PR3945 contraction frame count')
    row=contracted['records'][0];need(not any(row['delta']),'PR3945 moment changed')
    after=S.apply(word,'A',1858,row['gates'],C,3)
    need(all(word[k]==after[k] for k in word if k not in ('A','cleanup')),'PR3945 frozen boundary/native fields')
    return {'source_canonical_sha256':S.digest(word),'source_head':'91f81d131252db704f945891da1ea54e29d46b8b',
            'scope':'Only the literal A1858 inverse contraction; no PR3945 expansion census.',
            'source_profile':profile,'recursive_children':sum(profile.values()),'rank_mass':sum(k*v for k,v in profile.items()),
            'coefficient_heights':coefficient_heights(word,[row]),'width_inventory':widths,'before_gates':block,'contraction':row,
            'source_semantics':A.semantics(C,word),'contracted_semantics':A.semantics(C,after),
            'forward_ADD_delta':-1,'cleanup_ADD_delta':len(after['cleanup'])-len(word['cleanup']),
            'fixed_all_other_top_level_fields':True,'fresh_native_phase_or_supplier_admission':False}

def calculate(tag):
    S,C,A=setup();w=load(tag);C.hygiene(w);baseline,widths,_,start,end=C.frame_bill(w)
    need(C.derive_cleanup(w)==w['cleanup'],'source cleanup');need(baseline=={int(k):v for k,v in w['report']['local_profile'].items()},'source invoice')
    need(S.R.tracing(w)[2]==baseline,'trace invoice')
    result=S.compute(w,C);records=result['records'];samples=set()
    for section in ('A','B','restore'):
        group=[i for i,r in enumerate(records) if r['section']==section]
        if group:samples.update((group[0],group[-1]))
    replay=[]
    contraction_replay=[]
    for row in result['contractions']['records']:
        m=S.apply(w,row['section'],row['index'],row['gates'],C,3)
        contraction_replay.append({'record':row,'semantics':A.semantics(C,m)})
    for i in sorted(samples):
        row=records[i];m=S.apply(w,row['section'],row['index'],row['gates'],C)
        replay.append({'record':i,'semantics':A.semantics(C,m)})
    coeffs=[(abs(g[3]).bit_length(),abs(g[4]).bit_length()) for r in records for g in r['gates']]
    ledger={'baseline_profile':baseline,'recursive_children':sum(baseline.values()),'rank_mass':sum(k*v for k,v in baseline.items()),
       'helper_widths':widths,'helper_roles':sum(widths.values()),'live_inputs':C.N-len(w['removed']),'dirty_buffers':len(w['helper_final']),
       'native_warps':len(w['warps']),'initial_operator_corrections':len(w['initial_corrections']),
       'baseline_primitives':{s:dict(Counter(g[0] for g in w[s])) for s in ('precondition','compensation','A','cut','B','restore','cleanup')},
       'replacement_ADD_count':3,'replaced_ADD_count':2,'added_forward_ADDs_per_candidate':1,
       'cleanup_added_ADDs':sorted({r['cleanup_length']-len(w['cleanup']) for r in records}),
       'candidate_recursive_children_range':[min(sum(r['profile'].values()) for r in records),max(sum(r['profile'].values()) for r in records)],
       'candidate_rank_masses':sorted({sum(k*v for k,v in r['profile'].items()) for r in records}),
       **coefficient_heights(w,records),
       'contraction_forward_ADD_delta':-1,'contraction_cleanup_ADD_deltas':sorted({r['cleanup_length']-len(w['cleanup']) for r in result['contractions']['records']}),
       'contraction_profiles':[r['profile'] for r in result['contractions']['records']],
       'additional_helpers_buffers_native_maps':0,'changed_B_warp_positions':'Only numerical indices shift after insertion; same ordered warp with same neighbouring scalar events.',
       'boundary_start_sha256':S.digest({str(k):str(v) for k,v in start.items()}),'boundary_end_sha256':S.digest({str(k):str(v) for k,v in end.items()}),
       'proved':['Exact rational arbitrary-dirty three-register matrix equality for every orientation and coefficient motif',
                 'All compatible frame flags and complete chronological recursive invoice for every legal flag',
                 'Projected non-target matrix equality and literal inverse cleanup for every flag',
                 'All source free-operator symbols plus deterministic full-word sample replay',
                 'Finite primitive and scalar coefficient bounds; fixed roles, entrance/exit frames and native maps'],
       'unknown':['Physical allocation/hosting and complete owner schedule after extra ADD',
                  'Fresh Gaussian/Clifford realization and phase admission',
                  'Uniform precision/stock/tape tariff and implementation cost of additional scalar primitives',
                  'All-size compiler, outer/supplier admission, analytic transfer and BIT H1-H5'],
       'unknown_costs_are_zero':False,'new_supplier_or_kappa':False}
    return normal({'schema_version':1,'provider':tag,'source_canonical_sha256':S.digest(w),'source_semantics':A.semantics(C,w),
                   'current_producer_applicability':current_producer(tag,S,C,A),
                   'census':result,'whole_word_samples':replay,'contraction_whole_word_replays':contraction_replay,'ledger':ledger})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--provider',choices=('base','extra'),required=True);ap.add_argument('--emit',type=Path);ap.add_argument('--emit-contracted-word',type=Path);args=ap.parse_args()
    outputs=[]
    for path in (args.emit,args.emit_contracted_word):
        if path is None:continue
        target=path.resolve();need(target!=P and P not in target.parents,'output must be outside package')
        need(not target.exists(),'output already exists');need(target.parent.is_dir(),'output parent missing')
        need(target not in outputs,'output paths must differ');outputs.append(target)
    start=time.monotonic();result=calculate(args.provider)
    if args.emit:
        path=args.emit.resolve()
        with path.open('x') as stream:stream.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads((P/f'RESULT-{args.provider}.json').read_text()),'retained result mismatch')
    if args.emit_contracted_word:
        target=args.emit_contracted_word.resolve();need(P not in target.parents,'word export must be outside package')
        S,C,A=setup();rows=result['census']['contractions']['records'];need(len(rows)==1,'expected unique contraction')
        row=rows[0];word=S.apply(load(args.provider),row['section'],row['index'],row['gates'],C,3)
        need(S.digest(word)==row['canonical_word_sha256'],'exported word digest')
        with target.open('x') as stream:stream.write(json.dumps(word,sort_keys=True,separators=(',',':'))+'\n')
    print('PASS_A2_GRAPH',args.provider,len(result['census']['motifs']),result['census']['legal_flags'],f'{time.monotonic()-start:.3f}s')
if __name__=='__main__':main()
