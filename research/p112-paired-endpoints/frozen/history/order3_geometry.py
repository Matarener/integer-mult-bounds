#!/usr/bin/env python3
"""Nine-dimensional paired partners and exact individual contact witnesses.

The individual edge words and source-batched scheduling screen do not supply
a complete shared-data scalar word. Substantial OpenAI Codex assistance.
"""
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import paired_endpoint as E

HERE=Path(__file__).resolve().parent
O_COLUMNS=(451,454,453,31,55,47,248,440,376)
C=511


def dot(a,b):
    return (a&b).bit_count()&1


def apply(columns,x):
    y=0
    for i,v in enumerate(columns):
        if (x>>i)&1:y^=v
    return y


def span(values):
    ans={0}
    for x in values:ans|={v^x for v in ans}
    return ans


def basis(values):
    piv={}
    for x in values:
        while x:
            p=x.bit_length()-1
            if p in piv:x^=piv[p]
            else:piv[p]=x;break
    return tuple(piv[p]for p in sorted(piv,reverse=True))


def orthonormal(values,prefix=()):
    space=span(values);out=list(prefix)
    E.need(all(x in space for x in out),'prefix in subspace')
    E.need(all(dot(x,y)==int(i==j) for i,x in enumerate(out)
               for j,y in enumerate(out)),'orthonormal prefix')
    n=len(basis(values))
    while len(out)<n:
        choices=[x for x in sorted(space)if dot(x,x) and all(not dot(x,y)for y in out)]
        found=False
        for x in choices:
            rest=[v for v in space if not dot(v,x)and all(not dot(v,y)for y in out)]
            # Avoid leaving a nonzero alternating space without an orthonormal basis.
            if len(out)+1<n and not any(dot(v,v)for v in rest):continue
            out.append(x);found=True;break
        E.need(found,'nonalternating orthonormal completion')
    E.need(span(out)==space,'orthonormal basis covers whole frame')
    return tuple(out)


def batched_maximum(ports,partners):
    """Complete exact DP over source-batched triangular zero subsets."""
    n=len(ports)
    m=[[dot(p,q)for q in partners]for p in ports]
    zeros=[sum(1<<j for j in range(n)if i!=j and not m[i][j])for i in range(n)]
    compat=[sum(1<<j for j in range(n)if i!=j and not(m[i][j]and m[j][i]))
            for i in range(n)]
    @lru_cache(None)
    def clique_coloring_upper(mask):
        colors=0
        while mask:
            colors+=1;available=mask
            while available:
                bit=available&-available;v=bit.bit_length()-1
                mask^=bit;available^=bit;available&=~compat[v]
        return colors
    @lru_cache(None)
    def solve(mask):
        if not mask:return ()
        choices=[];left=mask
        while left:
            bit=left&-left;left^=bit;v=bit.bit_length()-1;sub=mask&zeros[v]
            choices.append((clique_coloring_upper(sub),sub.bit_count(),v,sub))
        choices.sort(reverse=True);best=()
        for upper,_,v,sub in choices:
            if upper+1<=len(best):continue
            candidate=(v,)+solve(sub)
            if len(candidate)>len(best):best=candidate
        return best
    witness=solve((1<<n)-1)
    E.need(all(not m[a][b]for j,a in enumerate(witness)for b in witness[j+1:]),
           'literal triangular witness')
    return {'maximum':len(witness),'witness':witness,'states':solve.cache_info().misses,
            'all_entries_digest':hashlib.sha256(json.dumps(m).encode()).hexdigest(),
            'scope':'Fixed partner O and source-batched all-edge delivery/restore order. Arbitrary per-edge interleaving, other O and changed correction graph are outside this maximum.'}


def main():
    path=E.SOURCE/'split-centres/CANONICAL-WORD.json.gz'
    ports=json.loads(gzip.decompress(path.read_bytes()))['ports']
    partners=[apply(O_COLUMNS,p)for p in ports]
    E.need(all(dot(x,y)==int(i==j)for i,x in enumerate(O_COLUMNS)
               for j,y in enumerate(O_COLUMNS)),'O orthogonal')
    E.need(all(apply(O_COLUMNS,apply(O_COLUMNS,apply(O_COLUMNS,x)))==x
               for x in range(512)),'O order three')
    E.need(all(dot(p,q)==0 for p,q in zip(ports,partners)),
           'all paired ports perpendicular')
    E.need(all(apply(O_COLUMNS,x)^apply(O_COLUMNS,apply(O_COLUMNS,x))
               == x^(C if dot(C,x)else 0) for x in range(512)),
           'O+O^transpose=I+cc^transpose')
    E.need(all(dot(p,r)==dot(q,s)for p,q in zip(ports,partners)
               for r,s in zip(ports,partners)),'whole Q Gram pattern')
    contracts=[]
    for p,q in zip(ports,partners):
        b=orthonormal([1<<i for i in range(9)],(p,q));r=b[2:]
        cp,cq,cr=[E.phase_kernel(9,u)for u in ((p,),(q,),r)]
        full=E.phase_kernel(9,[1<<i for i in range(9)])
        E.need(E.product(E.product(cp,cq),cr)==full,'actual paired product phase')
        E.need(E.product(E.phase_kernel(9,(p,)+r),E.conj(cp))==cr,
               'actual source residual with O partner')
        off=E.product(E.phase_kernel(9,(q,)+r),E.conj(cp))
        E.need(off==E.trans(full,p),'actual O-partner off-diagonal')
        contracts.append({'P':p,'Q':q,'R':r})
    edges=[];rank_counts=Counter();width_counts=Counter()
    for s,p in enumerate(ports):
        for t,pt in enumerate(ports):
            if dot(p,pt):continue
            q,qt=partners[s],partners[t]
            a,b=dot(p,qt),dot(q,pt)
            E.need(a^b==1,'opposite cross pairings at an old correction edge')
            if p==qt:frame=(p,)
            elif not a:frame=(p,qt)
            else:
                radical=p^qt
                w=next(x for x in range(1,512)
                       if not dot(x,q)and not dot(x,pt)and dot(x,radical)
                       and dot(x,qt^C))
                frame=orthonormal((p,qt,w),(qt,))
            E.need(p in span(frame)and qt in span(frame),'complete required contact span')
            E.need(all(not dot(x,q)and not dot(x,pt)for x in frame),
                   'source and target upper caps')
            E.need(all(dot(x,y)==int(i==j)for i,x in enumerate(frame)
                       for j,y in enumerate(frame)),'nondegenerate actual common frame')
            # One isolated arbitrary-dirty edge word:
            # y_t-=a*d_h at Qt; h+=x_s, y_t+=a*h, h-=x_s at F.
            # Its helper entrance Qt and terminal F isolate its dirt exactly.
            f=len(frame);rank_counts[f]+=1;width_counts[f-1]+=1
            edges.append({'source':s,'target':t,'frame':frame,'rank':f,
                          'helper_entrance':[qt],'helper_terminal':frame,
                          'helper_width':f-1,
                          'source_jumps':[f-1,8-f],
                          'target_jumps':[f-1,8-f]})
    E.need(len(edges)==5824,'all actual P112 orthogonal correction pairs')
    E.need(rank_counts=={1:104,2:2912,3:2808},'complete independent-edge ranks')
    # Two meaningful geometry controls.
    bad=list(O_COLUMNS);bad[0]^=1
    E.need(not all(dot(x,y)==int(i==j)for i,x in enumerate(bad)
                   for j,y in enumerate(bad)),'perturbed O rejected')
    E.need(not all(not dot(p,p)for p in ports),'Q=P is not a perpendicular partner')
    first_rank3=next(z for z in edges if z['rank']==3)
    a,b=ports[first_rank3['source']],partners[first_rank3['target']]
    E.need(dot(a,b)==1 and dot(a^b,a)==dot(a^b,b)==0,
           'omitting the rank-three extension leaves a real radical')
    scheduling=batched_maximum(ports,partners)
    E.need(scheduling['maximum']==8,'fixed-O batched order maximum')
    out={'status':'PASS_ORIGINAL_9D_PAIRED_GEOMETRY_NO_WHOLE_LOCAL_WORD',
         'source_sha256':E.hash_file(path),'O_columns':O_COLUMNS,'O_order':3,
         'ports':len(ports),'actual_native_paired_contracts':len(contracts),
         'local_dimension':9,'paired_common_dimension':2,'global_core_dimension':65,
         'contracts':contracts,'edge_rank_counts':dict(rank_counts),
         'isolated_edge_helper_widths':dict(width_counts),'edge_witnesses':edges,
         'literal_edge_family_paid_gate':{
             'direct_free_contacts':104,'remaining_helpers':5720,'helper_width':7,
             'helper_rank_mass':40040,'data_rank_mass':1568,
             'local_rank_mass_lower_bound':41608,
             'global_capacity_per_call':'58240/9',
             'decision':'FAIL_AT_ZERO_RATE_BEFORE_COPY_OR_REMAINDERS',
             'contract':'helper E=Q_t -> U=I-Q_s, actual residual C_(Q_s+Q_t)^perp; no old408-helper inventory inherited'},
         'batched_source_screen':scheduling,
         'negative_controls':['one-bit perturbation of O','Q=P','omit rank3 radical completion'],
         'limits':['Individual all-input edge words cannot be concatenated without repricing shared source/target frame histories.',
                   'Initial helper dirt is precompensated at Qt, so these helpers do not retain the old zero entrances.',
                   'No old408-helper inventory, chronological owner map, COPY decoder or complete histogram is inherited.',
                   'The paired endpoint proof and local contact geometry do not constitute an all-size supplier.']}
    (HERE/'ORDER3-GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])
    print(json.dumps({'edge_rank_counts':dict(rank_counts),'batched_source_screen':scheduling}))


if __name__=='__main__':main()
