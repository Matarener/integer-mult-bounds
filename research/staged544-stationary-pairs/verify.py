#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only, source-authenticated census and exact dirty-state controls."""
import gzip,hashlib,json,sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
P=Path(__file__).resolve().parent
# Authenticate retained executable bytes before any retained source executes.
for _row in json.loads((P/'SOURCES.json').read_text())['snapshots']:
    _raw=(P/_row['local']).read_bytes()
    if len(_raw)!=_row['bytes'] or hashlib.sha256(_raw).hexdigest()!=_row['sha256'] or hashlib.sha1(b'blob '+str(len(_raw)).encode()+b'\0'+_raw).hexdigest()!=_row['git_blob']:
        raise ValueError('source authentication before import: '+_row['local'])
sys.path.insert(0,str(P))
import pairs as S

def normal(x):return json.loads(json.dumps(x,sort_keys=True))
def authenticate(raw,row):
    S.require(len(raw)==row['bytes'],'source length')
    S.require(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256')
    S.require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob')
def setup():
    for row in json.loads((P/'SOURCES.json').read_text())['snapshots']:authenticate((P/row['local']).read_bytes(),row)
    return S.module('retained_auditor',P/'vendor/audit_core.py'),S.module('retained_semantics',P/'vendor/audit_verify.py')
def load(tag):return json.loads(gzip.decompress((P/'inputs'/f'BORROW-WORD-43{tag}.json.gz').read_bytes()))
def scalar_projection(word):
    # Every semantic field is retained, except frames and derived paid report.
    out=deepcopy(word)
    for section in ('A','B','restore'):
        for g in out[section]:
            if g[0]=='add':g[-1]=None
    out['report'].pop('local_profile',None)
    return out

def validation(word,result,C,A):
    C.hygiene(word);bill,widths,*_=C.frame_bill(word)
    S.require(bill=={int(k):v for k,v in result['baseline_profile'].items()},'baseline invoice')
    S.require(C.derive_cleanup(word)==word['cleanup'],'baseline cleanup')
    baseline=A.semantics(C,word);samples=[]
    for a,b,fa,fb,delta in result['whole_word_samples']:
        final=deepcopy(word);final[a[0]][a[1]][-1]=fa;final[b[0]][b[1]][-1]=fb
        actual,inventory,*_=C.frame_bill(final)
        S.require(tuple(actual.get(k,0)-bill.get(k,0) if k else 0 for k in range(10))==tuple(delta),'sample final invoice')
        S.require(inventory==widths,'helper inventory')
        S.require(C.derive_cleanup(final)==word['cleanup'],'unchanged inverse cleanup')
        final['report']['local_profile']={str(k):v for k,v in actual.items()}
        C.hygiene(final)
        S.require(scalar_projection(word)==scalar_projection(final),'unchanged free-operator program')
        semantic=A.semantics(C,final)
        samples.append({'addresses':[a,b],'frames':[fa,fb],'profile':actual,'semantics':semantic})
    primitives={sec:dict(sorted(Counter(g[0] for g in word[sec]).items())) for sec in ('precondition','compensation','A','cut','B','restore','cleanup')}
    coeff=[g for sec in ('A','B','restore') for g in word[sec] if g[0]=='add']
    return {'baseline_semantics':baseline,'edited_whole_words':samples,
      'ledger':{'recursive_profile':bill,'children':sum(bill.values()),'rank_mass':sum(k*v for k,v in bill.items()),
      'helper_widths':widths,'helper_roles':sum(widths.values()),'dirty_buffers':len(word['helper_final']),
      'live_inputs':C.N-len(word['removed']),'native_warps':len(word['warps']),'initial_corrections':len(word['initial_corrections']),
      'primitive_inventory':primitives,'scalar_numerator_bits':max(abs(g[3]).bit_length() for g in coeff),
      'scalar_denominator_bits':max(g[4].bit_length() for g in coeff),'added_gates_helpers_buffers':0,
      'proved':['All final paired frames and fixed boundaries by exact subspace enumeration; every paired local invoice',
       'Arbitrary-dirty operator and cleanup unchanged for every frame-only edit by identical semantic fields',
       'Complete exact free-operator baseline plus four edited whole-word controls per provider'],
      'unknown':['Fresh native Gaussian/Clifford phase implementation','Physical allocation/hosting and owner chronology',
       'Uniform precision, stock and tape tariffs','All-size compiler and outer/supplier admission','Analytic and BIT assumptions'],
      'unknown_costs_are_zero':False,'new_supplier_or_kappa':False}}

def main():
    C,A=setup()
    for tag in ('base','extra'):
        word=load(tag);result=S.census(word)
        S.require(normal(result)==json.loads((P/f'RESULT-{tag}.json').read_text()),'census receipt '+tag)
        receipt=validation(word,result,C,A)
        S.require(normal(receipt)==json.loads((P/f'CHECKS-{tag}.json').read_text()),'validation receipt '+tag)
        print('PASS_STATIONARY_PAIRS',tag,result['coupled_pairs'],result['pair_frame_assignments'],flush=True)
if __name__=='__main__':main()
