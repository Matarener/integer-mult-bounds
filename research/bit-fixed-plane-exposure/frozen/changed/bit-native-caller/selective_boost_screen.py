#!/usr/bin/env python3
"""Exact temporal common-E propagation screen for old R438 dirty kernels.

Nomination only: successful entries still need a literal joined-frame word.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter,defaultdict
from itertools import combinations
from hashlib import sha256
import argparse
import gzip
import json
from old_kernel_boost import old_word,dirty_factor
from global_kernel_boost import HERE,RAW,basis,contains,eye
from cold_cosets import need
from kernel_entrances import kernel

def dirty_cols(base):
    cols={h:0 for h in range(222,660)}
    for op,d,s,c,f,ph in base['records']:
        if op==1 and ph==10:cols[s]^=1<<(d-111)
    return cols

def propagation(base,raw,E,Bs=None):
    if Bs is None:Bs=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    upper=[all(contains(B,q)for q in E)for B in Bs]
    labels=[0]*661
    for p in range(111):
        if not upper[base['final'][111+p]]:labels[111+p]=1<<p
    copy_index=9
    for op,d,s,c,f,ph in reversed(base['records']):
        if ph==10:continue
        if op==0:
            if upper[c]:labels[d]=0
        elif op==1:
            if s==660:continue  # the copied field staysZERO, even for a boosted source
            if upper[f]:labels[d]=labels[s]=0
            else:labels[d]=labels[s]=labels[d]|labels[s]
        elif op==2:
            copy_index-=1
            if not upper[c]:labels[d]|=1<<(111+copy_index)
    need(copy_index==0,'all nine COPY exposure marks')
    return labels,upper

def receipt(write=False,native=False):
    raw=json.loads(gzip.decompress(RAW.read_bytes()));base=old_word(raw)
    dirty_factor(base,raw)  # independent semantic dirty-map comparison
    Bs=[basis(raw['lines'][p]for p in f)for f in raw['frames']]
    cols=dirty_cols(base);rows=[];todo=[]
    if native:
        from pathlib import Path
        FULL=Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz')
        full=json.loads(gzip.decompress(FULL.read_bytes()))
        todo=[('root'+str(i),basis([q]))for i,q in enumerate(full['lines'])]
        todo += [('frame'+str(i),B)for i,B in enumerate(Bs)if len(B)==2]
    else:
        for d in range(1,5):
            todo += [(axes,[eye(8)[i]for i in axes])for axes in combinations(range(8),d)]
    for axes,E in todo:
            d=len(E);labels,upper=propagation(base,raw,E,Bs)
            groups=defaultdict(list)
            for h in range(222,660):groups[labels[h]].append(h)
            zero=groups[0];K=kernel([cols[h]for h in zero])
            cold_safe=[p for p in range(111)if upper[base['final'][111+p]]and not labels[111+p]]
            forbidden=((1<<111)-1)^sum(1<<p for p in cold_safe)
            quotient_kernel=kernel([cols[h]&forbidden for h in zero])
            candidates=[]
            for mask in sorted(groups,key=lambda m:(m.bit_count(),m)):
                hs=[h for h in range(222,660)if not labels[h]&~mask]
                if len(hs)<=111 and len(hs)<2:continue
                allowed=[p for p in range(111)if upper[base['final'][111+p]]and not labels[111+p]&~mask]
                forbidden=((1<<111)-1)^sum(1<<p for p in allowed)
                ker=kernel([cols[h]&forbidden for h in hs]);k=len(ker)
                if not k:continue
                t=(mask&((1<<111)-1)).bit_count();c=(mask>>111).bit_count()
                candidates.append({'target_exposure':t,'COPY_exposure':c,'kernel_dimension':k,'allowed_cold_targets':allowed,
                                   'helper_group':hs,'mask':str(mask),'rank_mass_saving':d*k-t-c})
            candidates.sort(key=lambda z:(-z['rank_mass_saving'],z['target_exposure'],z['COPY_exposure']))
            rows.append({'axes':axes,'rank':d,'zero_exposure_helpers':zero,'zero_exposure_kernel':len(K),
                         'safe_cold_targets':cold_safe,'zero_exposure_quotient_kernel':len(quotient_kernel),
                         'zero_exposure_quotient_kernel_supports':[[zero[i]for i in range(len(zero))if v>>i&1]for v in quotient_kernel],
                         'distinct_exposure_classes':len(groups),'best':candidates[:3]})
    rows.sort(key=lambda z:(-z['zero_exposure_quotient_kernel']*z['rank'],-max([a['rank_mass_saving']for a in z['best']]+[0]),z['rank'],str(z['axes'])))
    out={'status':'PASS_EXACT_TEMPORAL_PROPAGATION_NOMINATION_ONLY','no_new_kappa':True,
         'source':{str(RAW):sha256(RAW.read_bytes()).hexdigest()},'planes_tested':len(rows),'plane_mode':'all120 roots plus153 actual rank2 frames'if native else'coordinate ranks1-4',
         'model':'A selected helper seed begins at commonE. Across an old ADD atf not containingE, either boosted actor forces both to span(f,E). Once an old frame containsE, no extra boost remains and its chronological propagation stops. Sources may climb early and use changed later joins. Total source terminal cuts areFULL. Copied fields remainZERO; a copied source not yet aboveE incurs at most one extra rank because its original total frame has dimension7. Targets acquire a paidFULL lift exactly when their final cap does not containE and they are reached.',
         'scope':'Backward OR propagation computes exact endpoint/COPY exposure for this prescribed temporal join algorithm. Allowed cold targets containE in their final cap and their own E promotion has exposure contained in the current mask. The quotient kernel restricts D to all forbidden target rows, permitting residual compensation at actual commonE only on the allowed cold targets. Kernel groups and rank-mass savings nominate literal words only; no scalar or ADDRESS replay is claimed by this screen.',
         'candidates':rows}
    out=json.loads(json.dumps(out));p=HERE/('SELECTIVE-BOOST-NATIVE-SCREEN.json'if native else'SELECTIVE-BOOST-SCREEN.json')
    if write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved selective boost screen differs')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--native',action='store_true');a=ap.parse_args();o=receipt(a.write,a.native)
    print(o['status'])
    for z in o['candidates'][:12]:print(z['axes'],'zeroK',z['zero_exposure_kernel'],'quotK',z['zero_exposure_quotient_kernel'],'safeT',len(z['safe_cold_targets']),'zerohelpers',len(z['zero_exposure_helpers']),'best',[(a['rank_mass_saving'],a['kernel_dimension'],a['target_exposure'],a['COPY_exposure'])for a in z['best']])

if __name__=='__main__':main()
