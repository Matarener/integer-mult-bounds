#!/usr/bin/env python3
"""Exact current-stock exclusions for the generalized paired-chain family.

p=2 fails raw helper capacity; p=3 and p=5 use exact knapsack duals; all
p>=6 are excluded by an analytic monotonicity argument. Both the original
and receiver-sharing supplier bills are checked, and each p=4 fractional
profile reproduces its own physically priced target. No clock search is
a proof input.
Apache-2.0; substantial OpenAI assistance and retained source attribution.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WIDTHS = (4,5,6,7,8,9)
LOCAL = {1:2440,2:725,3:224,4:102,5:20,8:8}
STOCK = {4:26,5:2,6:18,7:53,8:96,9:213}


def load_module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def linear_solve(matrix,rhs):
    n=len(rhs)
    if len(matrix)!=n or any(len(row)!=n for row in matrix):
        raise ValueError('square nominated basis')
    A=[[Q(v) for v in row]+[Q(rhs[j])] for j,row in enumerate(matrix)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if A[i][j])
        A[j],A[pivot]=A[pivot],A[j]
        d=A[j][j]
        A[j]=[x/d for x in A[j]]
        for i in range(n):
            if i!=j and A[i][j]:
                d=A[i][j]
                A[i]=[x-d*y for x,y in zip(A[i],A[j])]
    return [row[-1] for row in A]


def exact_knapsack(pi,maximum):
    """Max pi·pattern at every exact total width; all patterns are covered."""
    values=[None]*(maximum+1)
    witnesses=[None]*(maximum+1)
    values[0],witnesses[0]=Q(0),(0,)*6
    for total in range(1,maximum+1):
        for j,w in enumerate(WIDTHS):
            if total>=w and values[total-w] is not None:
                value=values[total-w]+pi[j]
                if values[total] is None or value>values[total]:
                    pat=list(witnesses[total-w]);pat[j]+=1
                    values[total],witnesses[total]=value,tuple(pat)
    number=[0]*(maximum+1);number[0]=1
    for w in WIDTHS:
        for total in range(w,maximum+1):
            number[total]+=number[total-w]
    return values,witnesses,number


def primal(I,path,local=LOCAL):
    row=json.loads(path.read_text())
    p=row['pairs'];m=16*p+9;c=2*p+1;W=224*p
    bins={8:224*(p-1)}|{16*q:448 for q in range(1,p)}
    I.need(row['rank_guard_relaxation']=='native','optimistic unsplit native rank relaxation')
    I.need({int(r):n for r,n in row['native_idle_histogram'].items()}==bins,'generalized idle census')
    used,sup,idle=Counter(),Counter(),Counter()
    for s in row['pattern_selection']:
        rank,pattern,n=s['rank'],s['counts'],Q(s['count'])
        I.need(n>=0 and len(pattern)==6 and all(type(x)is int and x>=0 for x in pattern),'nonnegative rational primal')
        left=rank-sum(w*x for w,x in zip(WIDTHS,pattern))
        I.need(left>=0 and s['priced_remainder_children']==([left] if left else []),'unsplit optimistic remainder')
        used[rank]+=n
        for w,x in zip(WIDTHS,pattern):sup[w]+=x*n
        if left:idle[left]+=n
    I.need(used==bins and sup=={w:c*n for w,n in STOCK.items()},'every exact bin and helper equation')
    profile=Counter({r:c*n for r,n in local.items()});profile.update(idle)
    I.need(m*W-sum(r*n for r,n in profile.items())==96*p-64,'generalized raw deficit identity')
    return row,bins,profile


def dual(I,row,bins,endpoint,local=LOCAL):
    p=row['pairs'];m=16*p+9;c=2*p+1;W=224*p;caps=sorted(bins)
    cost={0:Q(0)}|{r:I.cost(r,m,endpoint)[0] for r in range(1,max(caps)+1)}
    matrix,rhs=[],[]
    for s in row['pattern_selection']:
        pattern,rank=s['counts'],s['rank']
        matrix.append(pattern+[int(rank==r) for r in caps])
        rhs.append(cost[rank-sum(w*x for w,x in zip(WIDTHS,pattern))])
    nominated=linear_solve(matrix,rhs)
    pi=nominated[:6]
    values,witnesses,number=exact_knapsack(pi,max(caps))
    mu={}
    worst={}
    for rank in caps:
        # Re-tightening the bin dual makes feasibility exact even if a
        # nominated active basis had a tiny outward-rounding mismatch.
        bound,total=min((cost[rank-t]-values[t],t) for t in range(rank+1) if values[t] is not None)
        mu[rank]=bound
        worst[rank]=dict(used=total,pattern=witnesses[total],remainder=rank-total)
        I.need(all(mu[rank]+values[t]<=cost[rank-t] for t in range(rank+1) if values[t] is not None),
               'every exact used-width knapsack state is dual feasible')
    lower=I.weighted({r:c*n for r,n in local.items()},m,endpoint)[0]
    lower+=sum(mu[r]*bins[r] for r in caps)+sum(pi[j]*c*STOCK[w] for j,w in enumerate(WIDTHS))
    residual=lower-W
    # A wrong bin price is caught by its concrete maximizing knapsack witness.
    rank=caps[-1];control_mu=mu[rank]+1
    t=worst[rank]['used']
    I.need(control_mu+values[t]>cost[rank-t],'perturbed dual rejection control')
    return dict(endpoint=str(endpoint),dual_feasible=True,
                represented_integer_patterns=sum(sum(number[:r+1]) for r in caps),
                width_dual={w:str(v) for w,v in zip(WIDTHS,pi)},
                bin_dual={r:str(v) for r,v in mu.items()},tight_witnesses=worst,
                invoice_minus_productive_lower=str(residual),lower_decimal=I.decimal(residual),
                strictly_excludes_endpoint=residual>0,perturbed_bin_dual_rejected=True)


def analytic_tail(I,endpoint,local=LOCAL):
    # Grant every remaining rank unit the cheapest native rank m-25.
    # exp(x)>=1+x then bounds the invoice using
    # f(m)=a[5134log(m)-A+(112m-6078)log(m/(m-25))]-48+896/(m-1).
    # The raw deficit is (2p+1)*(48-896/(m-1)).
    m=105
    I.need(sum(r*n for r,n in local.items())==5134,'tail raw local mass')
    A_upper=sum(r*n*I.C.ln(r)[1] for r,n in local.items())
    lm,um=I.C.ln(m);lr,ur=I.C.ln(m-25)
    f_lower=endpoint*(5134*lm-A_upper+(112*m-6078)*(lm-ur))-48+Q(896,m-1)
    derivative_gate=endpoint*5134*(m-1)**2-896*m
    I.need(f_lower>0 and derivative_gate>0,'uniform p>=6 analytic base and derivative gates')
    return dict(endpoint=str(endpoint),local_profile=local,first_pairs=6,base_dimension=m,
                f_at_105_lower=str(f_lower),f_at_105_lower_decimal=I.decimal(f_lower),
                derivative_gate=str(derivative_gate),derivative_gate_decimal=I.decimal(derivative_gate),
                identity='D=96p-64; R=(2p+1)(112m-6078); m=16p+9',
                function='f(m)=a[5134 ln(m)-A+(112m-6078)ln(m/(m-25))]-48+896/(m-1)',
                derivative_bound='f prime(m) >= a*5134/m - 896/(m-1)^2, using ln(m/(m-25)) >=25/m; the omitted positive term is a*81950/[m(m-25)].',
                monotonicity='(m-1)^2/m=m-2+1/m is increasing for m>1. The positive rational gate at105 therefore makes the derivative positive for every real m>=105.',
                conclusion='Every integer p>=6 fails this moment endpoint even when all residue is fractionally priced unsplit at native rank m-25, with clock/physical restrictions dropped.')


def main():
    Ipath=REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    I=load_module(Ipath,'architecture_exact_invoice')
    geometry_path=HERE/'evidence/SEVEN57-GEOMETRY.json.gz'
    geometry=I.read(geometry_path)
    I.need(Counter(geometry['helper_widths'])==STOCK and {int(r):n for r,n in geometry['local_profile'].items()}==LOCAL,
           'authenticated source stock and local bill')
    nominations=HERE/'pair-count-nominations'
    paths=[nominations/f'PAIRS-{p}.json' for p in range(3,9)]
    records=[]
    for path in paths:
        row,bins,profile=primal(I,path)
        p=row['pairs']
        rec=dict(pairs=p,dimension=row['dimension'],root=I.root(profile,row['dimension'],row['productive_fields']))
        if p in (3,5,6,7,8):
            rec['dual_at_target']=dual(I,row,bins,I.TARGET)
            I.need(rec['dual_at_target']['strictly_excludes_endpoint'],'all nominated alternatives fail target exactly')
        if p==4:
            I.need(Q(rec['root']['rational'][0])==I.TARGET,'four-pair positive control reproduces retained ideal target')
        records.append(rec)
    p2_idle=8*224+16*448
    p2_required=5*3278
    I.need(p2_idle==8960 and p2_required-p2_idle==7430,'two-pair exact raw capacity control')
    tail=analytic_tail(I,I.TARGET)
    # Price the same width patterns for the actual newly emitted word as well.
    # The independent receiver review binds unchanged entrance/output frames
    # and every helper width, so no new geometry or clock is assumed here.
    review_path=HERE/'evidence/RECEIVER-REVIEW.json'
    review=I.read(review_path)
    I.need(review['status']=='PASS_BOTH_PROVIDER_INDEPENDENT_RECEIVER_REWRITE_REVIEW','receiver stock review')
    new_paths=[HERE.parent/f'native-alternatives/candidate/BORROW-WORD-43{tag}.json.gz' for tag in ('base','extra')]
    new_local={1:2439,2:724,3:225,4:102,5:20,8:8}
    for tag,path in zip(('base','extra'),new_paths):
        word=I.read(path)
        payload=sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        I.need(payload==review['providers'][tag]['candidate_payload_sha256'],'new supplier word bound to independent review')
        I.need({int(r):n for r,n in word['report']['local_profile'].items()}==new_local,'new actual local bill')
        I.need({int(w):n for w,n in review['providers'][tag]['helper_width_inventory'].items()}==STOCK,'new actual helper widths')
    price_path=HERE.parent/'global-budget/receiver-sharing/PRICE.json'
    price=I.read(price_path)
    new_target=Q(price['root_lower'])
    I.need(price['status']=='PASS_EXACT_ACTUAL_CHRONOLOGICAL_PROFILE_PRICE' and new_target>I.TARGET,'new priced four-pair target')
    new_records=[]
    for path in paths:
        row,bins,profile=primal(I,path,new_local)
        p=row['pairs']
        rec=dict(pairs=p,dimension=row['dimension'],root=I.root(profile,row['dimension'],row['productive_fields']))
        if p in (3,5,6,7,8):
            rec['dual_at_target']=dual(I,row,bins,new_target,new_local)
            I.need(rec['dual_at_target']['strictly_excludes_endpoint'],'new supplier alternative excluded exactly')
        if p==4:
            I.need(Q(rec['root']['rational'][0])==new_target,'new four-pair control reproduces actual receiver-sharing target')
            actual={int(r):Q(n,price['replicas']) for r,n in price['profile'].items()}
            I.need(profile==actual,'new four-pair aggregate exactly equals the admitted physical profile')
        new_records.append(rec)
    new_tail=analytic_tail(I,new_target,new_local)
    sources=[Path(__file__),HERE/'seven_geometry.py',geometry_path,HERE/'pair_count_screen.py',Ipath,I.ENGINE_PATH,
             review_path,price_path]+paths+new_paths
    result=dict(status='PASS_EXACT_GENERALIZED_PAIRED_CHAIN_CURRENT_STOCK_SCREEN',
                input_sha256={str(path.relative_to(REPO)):sha256(path.read_bytes()).hexdigest() for path in sources},
                source_helper_inventory=STOCK,source_local_profile=LOCAL,
                two_pair_raw_shortfall=7430,finite_pattern_certificates=records,uniform_tail=tail,
                receiver_sharing_family=dict(local_profile=new_local,target=str(new_target),
                    finite_pattern_certificates=new_records,uniform_tail=new_tail,
                    four_pair_profile_equals_admitted_physical_invoice=True),
                scope='Generalized B_p geometry with112 oldports,2p+1 complete calls,dimension16p+9,exact unchanged408-helper inventory3278,and no added productive bank families. Both the original complete supplier and the authenticated receiver-sharing supplier are priced separately. The proof relaxes clocks, owner injection and the native rank guard. It is not an exclusion for other supplier words, changed coverage laws, more general controllers, or additional banks.',
                conclusion='For each of these two stated supplier bills, p2 is infeasible; p3 and every p>=5 fail its own four-pair target. Each p4 fractional inventory reproduces the corresponding physically priced target. The positive new kappa admission belongs to the native/global/outer integration, not this family exclusion.')
    (HERE/'evidence/PAIR-COUNT-CERTIFICATE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])
    print('uniform p>=6 f105 lower',tail['f_at_105_lower_decimal'])
    print('receiver supplier uniform p>=6 f105 lower',new_tail['f_at_105_lower_decimal'])


if __name__=='__main__':
    main()
