#!/usr/bin/env python3
"""Ten literal rank1-entrance helper contracts from compensation kernels.

The owner must implement each paired residual; arbitrary physical dirt can be interpreted in its declared entrance frame.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from cold_cosets import bits,need,rank2
from helper_tail_retime import WORD,RAW,replay,rankQ

HERE=Path(__file__).resolve().parent

def kernel(V):
    B={};out=[]
    for i,v in enumerate(V):
        c=1<<i
        while v:
            k=v.bit_length()-1
            if k not in B:B[k]=(v,c);break
            w,a=B[k];v^=w;c^=a
        if not v:out.append(c)
    return out

def parity(rows):return[sum((v&1)<<j for j,v in row.items())for row in rows]

def build(base,raw):
    records=base['records'];cols={h:0 for h in range(222,651)};first={}
    for i,r in enumerate(records):
        op,d,s,c,f,ph=r
        if op==1 and ph==10:
            need(c==1 and f==0 and 111<=d<222 and 222<=s<651,'literal zero-frame dirty compensation')
            cols[s]^=1<<(d-111)
        if op==0 and d>=222:first.setdefault(d,(i,r))
    groups=defaultdict(list)
    for h,(i,r)in first.items():
        need(r[2]==0,'old helper first frameZERO')
        need(not any(z[0]==1 and z[-1]!=10 and h in(z[1],z[2])for z in records[:i]),
             'no forward helper incidence before first MOVE')
        groups[r[3]].append(h)
    witnesses=[];selected={};active=set();setup=[];post=[]
    for f,hs in sorted(groups.items()):
        ker=kernel([cols[h]for h in hs])
        if not ker:continue
        need(rankQ(raw['lines'][p]for p in raw['frames'][f])==1 and len(ker)==1,
             'this constructor uses actual one-dimensional first-frame kernels')
        v=ker[0];support=[hs[j]for j in bits(v)];h=support[-1]
        need(not selected.keys()&set(support),'disjoint exact entrance groups')
        selected[h]=f;active.update(support)
        others=[k for k in support if k!=h]
        total=0
        for k in support:total^=cols[k]
        need(total==0,'actual compensation-kernel column')
        setup.extend([1,k,h,1,f,71]for k in others)
        post.extend([1,k,h,-1,1,72]for k in reversed(others))
        witnesses.append({'frame':f,'selected_helper':h,'kernel_helpers':support,
                          'forward_S_ADDs':[[k,h,1]for k in others],
                          'inverse_S_ADDs':[[k,h,-1]for k in reversed(others)],
                          'old_compensation_column_weights':[cols[k].bit_count()for k in support]})
    need(len(selected)==10,'ten exact first-frame kernel directions')
    first_ids={id(first[h][1])for h in active}
    lifted=[first[h][1][:]for h in sorted(active-selected.keys())]
    for r in lifted:r[-1]=70
    start=base['start'][:]
    for h,f in selected.items():start[h]=f
    prefix=[r[:]for r in records if r[-1]==10 and r[2]not in selected]
    tail=[r[:]for r in records if r[-1]!=10 and id(r)not in first_ids]
    lastC=max(i for i,r in enumerate(tail)if r[-1]==5)+1
    tail[lastC:lastC]=post
    new=dict(base);new['start']=start;new['records']=prefix+lifted+setup+tail
    new['format']='R429-ten-paired-nonzero-helper-entrances-v1'
    return new,witnesses,selected,setup,post

def receipt(write=False):
    need(sha256(WORD.read_bytes()).hexdigest()=='0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e','frozen full box')
    need(sha256(RAW.read_bytes()).hexdigest()=='a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','frozen geometry')
    base=json.loads(gzip.decompress(WORD.read_bytes()));raw=json.loads(gzip.decompress(RAW.read_bytes()))
    new,witnesses,selected,setup,post=build(base,raw)
    rows,rec=replay(new,raw);oldrows,oldrec=replay(base,raw)
    need(all(rows[h]=={h:1}for h in list(range(111))+list(range(222,651))),
         'all111 sources and429 arbitrary helpers restored exactly overZ')
    expected=[1<<j for j in range(651)]
    for p in range(111):expected[111+p]^=1<<p
    need(parity(rows)==expected,'all651 binary clean-shear columns with new compensation')
    for p in range(111,222):
        need(rows[p].get(p)==1 and all(j<111 or j==p or j>=222 for j in rows[p]),'target oldy exact self row')
        need(all(not v&1 for j,v in rows[p].items()if j>=222),'new target helper leakage is even')
    closed,invrec=replay(new,raw,rows,True)
    need(closed==[{j:1}for j in range(651)],'literal signed inverse every column')
    H=Counter({int(k):v for k,v in rec['H'].items()});oldH=Counter({int(k):v for k,v in oldrec['H'].items()})
    need(H==oldH-Counter({1:10})and rec['mass']==5087,'exact ten H1 reduction')
    wrapper=[]
    from fractions import Fraction as Q
    from native_seed_binding import eye,mm,rank
    def D(P):
        n=len(P);C=[[Q(i==j)-P[i][j]for j in range(n)]for i in range(n)]
        return[C[i]+P[i]for i in range(n)]+[P[i]+C[i]for i in range(n)]
    I=eye(8)
    for h,f in sorted(selected.items()):
        q=raw['lines'][raw['frames'][f][0]];P=[[Q(x*y,4)for y in q]for x in q]
        K=[[I[i][j]-P[i][j]for j in range(8)]for i in range(8)]
        need(rank(P)==1 and rank(K)==7 and mm(D(I),D(P))==D(K),'actual paired (E,FULL) native residual rank7')
        wrapper.append({'helper':h,'entrance_frame':f,'entrance_root':q,'terminal_frame':1,
                        'residual_rank':7,'native_residual':'D_FULL D_E^-1 =D_(E-perp)'})
    # An old ZERO entrance or compensation column is a typed error.
    bad=dict(new);bad['start']=new['start'][:];bad['start'][next(iter(selected))]=0
    try:replay(bad,raw)
    except ValueError:zero_control=True
    else:raise ValueError('oldZERO entrance mutation escaped')
    bad=dict(new);bad['records']=[r[:]for r in new['records']if r[-1]!=72]
    br,_=replay(bad,raw)
    need(any(br[h]!={h:1}for h in range(222,651)),'omitting inverse basis fails integer helper restoration')
    # Delete one member of a nontrivial kernel from both S directions while
    # retaining the zero compensation column; the target leaks dirty parity.
    chosen=next(w for w in witnesses if len(w['kernel_helpers'])>1);d=chosen['kernel_helpers'][0];s=chosen['selected_helper']
    bad=dict(new);bad['records']=[r[:]for r in new['records']if not(r[-1]in(71,72)and r[1]==d and r[2]==s)]
    br,_=replay(bad,raw)
    need(parity(br)!=expected,'perturbed kernel basis leaks arbitrary helper dirt')
    canonical=json.dumps(new,sort_keys=True,separators=(',',':')).encode()
    out={'status':'PASS_R429_TEN_LITERAL_PAIRED_RANK1_ENTRANCE_FULL_EXIT_HELPERS',
        'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(WORD,RAW)},
        'all651_signed_integer_columns':True,'literal_inverse':invrec,'profile':rec,'old_profile':oldrec,
        'ordinary_helpers':429,'private_fields':0,'helper_inventory_by_residual_width':{7:10,8:419},
        'paired_native_wrappers':wrapper,'compensation_kernel_witnesses':witnesses,
        'new_basis_scalar_ADDs':len(setup)+len(post),'word_canonical_sha256':sha256(canonical).hexdigest(),
        'contract':'Ten explicitly listed arbitrary dirty helpers enter at their rank1 first frame E_h and exitFULL. The other419 helpers enterZERO and exitFULL. Each changed residual is D_FULL D_Eh^-1 of rank7; every scalar source/helper row is restored exactly overZ and target is the same clean shear overF2. Source and target physical native cuts are inherited unchanged.',
        'complete_local_price':'Delete10 first H1 queries. Other first MOVEs are merely advanced to the same frame before S; no new recursive query, COPY, private field or target lift. The helper basis S acts at a genuine common E; S^-1 acts atFULL. Initial compensation D*S mod2 has zero selected columns and therefore never reads a nonZERO entrance atZERO. New histogram is the frozen H minus10H1. Source/target coverage111*15 plus419*8+10*7 equals5087, so the old uncovered deficit is unchanged.',
        'entrance_gate':'The owner must implement the physical paired residual D_FULL D_Eh^-1 with public helper dependence cancelled. An arbitrary physical helper u can be interpreted as logical dirt h=D_Eh^-1u; this requires no executed entrance query merely to name h. If one instead insists on the old ZERO logical-dirt identification, ten explicit entrance queries restore the old5097 mass. Chronological paired owner routing remains open.',
        'controls':{'old_ZERO_entrance_rejected':zero_control,'omitted_inverse_basis_fails_Z_helpers':True,'perturbed_kernel_leaks_F2_dirt':True},
        'limits':['No chronological owner/stock construction for the nonzero entrances.','No changed rounded suffix-error or physical source/tape invoice.','A local residual-width reduction is not an admitted supplier or new exponent.'],
        'attribution':'Underlying R429/E8/signed-word ancestry is pinned in the frozen full compensation source. The helper-boundaries skill compensation-kernel lesson guided the changed entrance. This lane constructs the literal staged S, modified compensation, exact inverse and paired native wrappers.'}
    if write:
        (HERE/'KERNEL-ENTRANCES-WORD.json.gz').write_bytes(gzip.compress(canonical,mtime=0))
    else:need(gzip.decompress((HERE/'KERNEL-ENTRANCES-WORD.json.gz').read_bytes())==canonical,'saved kernel-entrance word differs')
    return json.loads(json.dumps(out))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=receipt(args.write);path=HERE/'KERNEL-ENTRANCES.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_bytes())==out,'saved kernel-entrance receipt differs')
    print(out['status']);print('10 rank7 residuals;419 rank8;0private; all651 signed/F2 columns; local mass5087; owner entrance gate open')

if __name__=='__main__':main()
