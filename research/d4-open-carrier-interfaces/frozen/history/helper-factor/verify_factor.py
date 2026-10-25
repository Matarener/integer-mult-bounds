#!/usr/bin/env python3
"""Exact invariant-gauge four-helper OPEN bus factorization.

Local identity only. Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1]/'kappa-major-20261018T1330Z'
BUS = OLD/'complex-boundary/paired-pivot/D4-BUS-INPUT.json'
COMP = Path('/Users/ross/git/math/integer-mult-bounds/research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py')

def need(v,m):
    if not v:
        raise ValueError(m)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    need(hashlib.sha256(BUS.read_bytes()).hexdigest()=='93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd','geometry pin')
    need(hashlib.sha256(COMP.read_bytes()).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','compiler pin')
    spec=importlib.util.spec_from_file_location('helper_factor_clifford',COMP)
    ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    G=json.loads(BUS.read_text())['groups7'];n=7;core=[g[0]for g in G]
    chart=ce.perm(n,ce.inv(ce.transpose(core+[5,53,30,96],n),n))
    D=chart.then(ce.hadamard(n,[3,4])).then(chart.adjoint()).then(ce.Op(n,ce.identity(n),[('phase',3)]))
    E=[D.then(ce.cgate(n,p))for p in core]
    VB=E[0].then(ce.cgate(n,core[2]));VC=E[0].then(ce.cgate(n,core[1]))
    F=ce.fourier(n).then(ce.xgate(n,33))
    def same(a,b,m):
        need(a.tab==b.tab and a.zero_state()==b.zero_state(),m)
    def lower(a):
        r,l=ce.lower_child(a);same(a,l,'exact lowering including phase');return r
    source_in=[ce.cgate(n,p)for group in G for p in group]
    target_in=[ce.cgate(n,G[(g+1)%3][j])for g in range(3)for j in range(4)]
    source_out=[ce.cgate(n,G[(g+1)%3][j]).adjoint().then(F)for g in range(3)for j in range(4)]
    target_out=[ce.cgate(n,p).adjoint().then(F)for group in G for p in group]
    # Logical arrays at their declared native frames. Every input column,
    # including all four independent helper values, is represented.
    rows=[[int(i==j)for j in range(28)]for i in range(28)]
    def swap(a,b):rows[a],rows[b]=rows[b],rows[a]
    for g in range(3):
        for j in range(4):swap(4*g+j,24+j)
        for j in range(4):rows[12+4*g+j]=[a+b for a,b in zip(rows[12+4*g+j],rows[24+j])]
    before=[r[:]for r in rows]
    destinations=list(range(4,12))+list(range(24,28))+list(range(12,24))+list(range(4))
    physical_ends=source_out+target_out+[VC]*4
    # Raw field swaps restore IDs and carry the actual native operators.
    for g in reversed(range(3)):
        for j in range(4):
            swap(4*g+j,24+j)
            physical_ends[4*g+j],physical_ends[24+j]=physical_ends[24+j],physical_ends[4*g+j]
    expected=[[int(i==j)for j in range(28)]for i in range(28)]
    for p in range(12):expected[12+p][p]=1
    need(rows==expected,'all28 input columns, exact scalar identity and dirty isolation')
    need(before!=expected,'omitting raw ID cleanup is detected')
    channels=[];helper_ranks=[]
    for g in range(3):
        for j,p in enumerate(G[g]):
            i=4*g+j;q=G[(g+1)%3][j];r=G[(g+2)%3][j]
            S=source_in[i].adjoint().then(physical_ends[i])
            wanted_S=source_in[i].adjoint().then(ce.cgate(n,r).adjoint().then(F)if g<2 else VC)
            same(S,wanted_S,'source channel equals frozen zero-helper OPEN boundary')
            T=target_in[i].adjoint().then(physical_ends[12+i])
            J=source_in[i].adjoint().then(physical_ends[12+i])
            same(J,ce.xgate(n,p).then(F),'cross channel equals actual full J')
            need(lower(S)['rank']==lower(T)['rank']==5,'source and target rank5')
            channels.append({'port':p,'source_rank':5,'target_rank':5,'cross_rank':lower(J)['rank']})
    for j in range(4):
        H=E[0].adjoint().then(physical_ends[24+j])
        same(H,E[0].adjoint().then(source_out[j]),'helper line has moved A endpoint')
        rec=lower(H);need(rec['rank']==3,'independent helper native rank3')
        helper_ranks.append(rec)
    hist=Counter()
    for g in range(3):
        for j in range(4):
            i=4*g+j
            sp=[source_in[i],E[g],source_out[i]]
            tp=[target_in[i],E[(g+1)%3]]+([VC]if g==2 else[])+[target_out[i]]
            for path in(sp,tp):
                for a,b in zip(path,path[1:]):hist[lower(a.adjoint().then(b))['rank']]+=1
    for a,b in zip([E[0],E[1],E[2],VB],[E[1],E[2],VB,VC]):
        hist[lower(a.adjoint().then(b))['rank']]+=4
    need(hist==Counter({1:8,2:40,3:20}),'complete actual four-helper histogram')
    carrier=Counter({1:8,2:40,3:16})
    need(hist-carrier==Counter({3:4}),'exact marginal histogram equals four standalone H3')
    bad=[r[:]for r in rows];bad[12][24]+=1
    need(bad!=expected,'helper contamination detected')
    out={'status':'PASS_OPEN_BUS_EQUALS_OPEN_CARRIER_PLUS_FOUR_INDEPENDENT_RANK3_CHANNELS',
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
         'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(BUS,COMP)},
         'all_independent_input_columns':28,'actual_gauge':'F=X33 F7; D and E_g as frozen source-carrier construction',
         'scalar_endpoint':rows,'public_native_channels':channels,'helper_lowerings':helper_ranks,
         'four_helper_histogram':dict(hist),'zero_helper_histogram':dict(carrier),'marginal_histogram':{'3':4},
         'identity':'After paid raw ID cleanup, the operator is OPEN on the24 public fields direct-sum H0,H1,H2,H3 on four independent arbitrary helper inputs. Each Hj=F C_(q_j)^-1 E_A^-1 has native rank3 with exact phase lowering.',
         'scope':'All input columns and exact native operators for the declared invariant-gauge local bus. Tensor products preserve the identity at every chunk size. This is not an admission of a nonlocal helper exchange, global owner schedule, rounding or tape bill.',
         'consequence':'Keeping helpers separated cannot repair the public endpoint deficit. A proposed saving using them must change the global coupled word, not credit the same four rank3 channels to both helper completion and public completion.',
         'controls':['omit ID cleanup','introduce a helper-to-target coefficient'],
         'no_new_kappa':True}
    out=json.loads(json.dumps(out));target=HERE/'FACTOR.json'
    if args.write:target.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(target.read_text())==out,'stored receipt mismatch')
    print(out['status'])
    print('28 columns;12 public native blocks;4 exact rank3 helpers;2 controls PASS')

if __name__=='__main__':main()
