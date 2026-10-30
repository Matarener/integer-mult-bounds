"""Exact full-cost comparison for the inherited ideal whole-K p19 inventory.
This arithmetic does not assert that the controller has been emitted.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def engine():
    src=ROOT/'source/moments.py';pin=json.loads((ROOT/'source/MOMENT-SOURCE.json').read_text())
    need(sha256(src.read_bytes()).hexdigest()==pin['sha256'],'Interval-engine source')
    ns={'__name__':'credited_interval_engine','__file__':str(src)}
    exec(compile(src.read_bytes(),str(src),'exec',dont_inherit=True,optimize=0),ns)
    return ns

def invoice():
    # 19 FULLs on odd positions and 20 QUERYs on even positions.
    # One full main pair, nine initial pairs, nine terminal pairs.
    sizes=[19]+[j for j in range(1,10)for _ in range(2)]
    T=Counter();P=Counter({1:20,8:19,9:19,15:19,16:19})
    for m in sizes:T[24*m+1]+=2
    for j in range(1,10):P[24*j]+=4
    full=P.copy();full[1]+=2*len(sizes)
    dropped=P.copy();dropped[1]+=len(sizes)
    Td=T.copy()
    for m in sizes:Td[24*m+1]-=1;Td[24*m]+=1
    return sizes,T,P,full,Td,dropped

def e_completion(E):
    pin=json.loads((ROOT/'source/E-PINS.json').read_text())
    for name,digest in pin['files'].items():need(sha256((ROOT/'source'/name).read_bytes()).hexdigest()==digest,'Changed E source')
    src=json.loads((ROOT/'source/E-MODES.json').read_text())
    V=src['global_dimension'];modes=src['nonzero_global_modes']
    eigenvalues=sorted({sector['F_C_eigenvalue']for sector in src['sectors']})
    need(eigenvalues==[-1078,0,98],'Actual E spectrum')
    D=97*1079
    need(D==104663 and D+981==105644,'Exact inverse-polynomial coefficients')
    for x in eigenvalues:
        need(x**3+980*x*x-105644*x==0,'Spectral annihilator')
        need((1-x)*(1-Q(981*x+x*x,D))==1,'Exact inverse polynomial')
    need(max(abs(Q(1,1-x))for x in eigenvalues)==1,'E operator norm')
    need(max(abs(1-x)for x in eigenvalues)==1079,'E inverse operator norm')
    need(V==112**3 and modes==20480 and Q(modes,V)==Q(5,343),'Actual mode ratio')
    T={73:2*V};paid={r:3*V for r in (8,9,15,16)};paid[25]=3*modes;paid[1]=2*V
    t=1-Q('0.003027288235');tm=E['moment'](T,t);pm=E['moment'](paid,t)
    margin=(tm[0]-pm[1],tm[1]-pm[0]);need(margin[1]<0,'Completed N3 cost must not be granted as profitable')
    rank_margin=sum(r*n for r,n in T.items())-sum(r*n for r,n in paid.items())
    need(Q(rank_margin,V)==-Q(375,343),'Complete E rank mass')
    ordinary=Counter()
    # Three local modules, each with two recodings, plus three positive and
    # three negative output recodings: twelve E/E^-1 evaluations in total.
    for name,factor in [('ordinary_E_code_per_evaluation',12),('ordinary_query_both_orientations_upper',3),('ordinary_native_inverse_transpose_and_boundaries_upper',3)]:
        for op,n in src[name].items():
            if op!='reusable_owned_fields':ordinary[op]+=factor*n
    return {'status':'PASS_RETAINED_E_N3_COMPOSITION_AND_COMPLETE_FIELD_BILL',
            'endpoint':'diag(R73,R73) under the pinned E local contracts',
            'negative_decoder_chronology':['Q','E3_inverse','E2','E1_inverse','Q'],
            'paid':paid,'targets':T,'ordinary_upper':dict(ordinary),
            'owned_peak_field_upper':max(src['global_inverse_owned_peak_upper'],src['reusable_scalar_K_scratch_fields']),
            'rank_mass_per_owner':str(Q(rank_margin,V)),
            'moment_margin_per_owner':[str(v/V)for v in margin],
            'spectrum_norm_E':'1','spectrum_norm_E_inverse':'1079',
            'negative_decoder_operator_norm_upper':1079**2,
            'scope':'Source-bound algebraic composition and field-level upper bill. The upstream E physical proof is retained; its full 41-file replay, ordinary TM tariff and odd-denominator precision implementation are not newly supplied.',
            'k_specific_unitary_precision_applies':False,'new_kappa':False}

def run():
    E=engine();sizes,T,P,F,Td,Pd=invoice()
    mass=lambda h:sum(r*n for r,n in h.items())
    need(mass(T)-mass(P)==18,'Inherited ideal rank mass')
    need(mass(T)-mass(F)==mass(Td)-mass(Pd)==-20,'Full repair rank accounting')
    tests=[]
    for k in [Q('0.003027288235'),Q('0.0030272882489783'),Q('0.00344412')]:
        t=1-k;ideal=E['moment'](T,t);paid=E['moment'](P,t)
        fm=E['moment'](F,t);dt=E['moment'](Td,t);dp=E['moment'](Pd,t)
        original=(ideal[0]-paid[1],ideal[1]-paid[0]);full=(ideal[0]-fm[1],ideal[1]-fm[0]);drop=(dt[0]-dp[1],dt[1]-dp[0])
        need(original[0]>0 and full[1]<0 and drop[1]<0,'Changed full-cost conclusion')
        need(drop[0]>full[1],'One-pass lower-rank option has better concave moment')
        tests.append({'tested_kappa':str(k),'ideal_unrepaired_margin':[str(x)for x in original],
                      'full_repair_margin':[str(x)for x in full],'drop_central_margin':[str(x)for x in drop]})
    return {'status':'PASS_EXACT_REPAIR_INVOICE','per_owner':True,'owners':112**3,
            'negative_cohorts':len(sizes),'inverse_code_evaluations':sum(sizes),
            'naive_per_stage_Q_jobs':2*sum(sizes),'whole_word_Q_jobs':2*len(sizes),
            'saved_Q_jobs_against_naive_stagewise_repair':2*(sum(sizes)-len(sizes)),
            'full_targets':dict(sorted(T.items())),'full_paid':dict(sorted(F.items())),
            'drop_central_targets':dict(sorted(Td.items())),'drop_central_paid':dict(sorted(Pd.items())),
            'repaired_rank_mass_surplus':-20,'tests':tests,'newest_E_completion':e_completion(E),'new_kappa':False,
            'scope':'Decoder bills are constructive. The p19 inventory is inherited planning arithmetic; no complete p19 native/controller emission or multiplier admission is claimed.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
