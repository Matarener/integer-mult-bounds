#!/usr/bin/env python3
"""Column generation plus exact reconstruction for mixed-target idle forests.

This searches p-pair controllers with two wide idle windows and one short
window for each j=1,...,p-1.  A fresh productive job completes every unhosted
helper.  The receipt checks exact rational multiplicities and the full
displayed child profile; numerical optimality is not a proof of a global
optimum.  Native frame/emission and outer supplier obligations remain open.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse
import json
import sys

import mixed_target_probe as E
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
IDENTITY=Counter({1:2487,2:713,3:224,4:102,5:20,8:8})
WIDTHS=(0,5,6,7,8,9)

def windows(p,prefix_cut=False):
    """Literal pair-controller idle chronology, 224 fields per window."""
    out=[]
    for j in range(1,p):
        if not prefix_cut:
            out.append({'name':f'early{j}','capacity':16*j,'stages':list(range(2*j))})
        out.append({'name':f'middle{j}','capacity':8,'stages':[2*j]})
        out.append({'name':f'late{j}','capacity':16*j,'stages':list(range(2*p+1-2*j,2*p+1))})
    expected=1792*(2*p+1)*(p-1)-(224*16*p*(p-1)//2 if prefix_cut else 0)
    E.need(sum(224*w['capacity'] for w in out)==expected,'General idle rank identity')
    return out

def numerical_split(r,maximum,c):
    return sum(n*k**(1-c) for k,n in E.split_rank(r,maximum).items())

def reconstruct_exact(numbers,columns,families,resource,inventory):
    """Recover an exact feasible basic solution, not rounded inventories.

    Small denominators suffice for most screens.  Degenerate larger masters
    can have a denominator above that guess; recover their active integer
    linear system and independently replay it instead of waiving an equality.
    """
    support=[i for i,x in enumerate(numbers) if x>1e-7]
    approximate=[Q(float(numbers[i])).limit_denominator(10**6) for i in support]
    def equations():
        rows=[];rhs=[]
        for f in range(len(families)):
            if not families[f].get('unbounded'):
                rows.append([int(columns[i][0]==f) for i in support]);rhs.append(families[f].get('field_count',224))
        for stage,r in resource:
            row=[]
            for i in support:
                f,pattern=columns[i]
                w=families[f]
                row.append(sum(int(s==stage and v==r) for s,v in zip(w['stages'],pattern)))
            usage=sum(x*float(numbers[i]) for x,i in zip(row,support))
            if abs(usage-inventory[r])<1e-7:
                rows.append(row);rhs.append(inventory[r])
        return rows,rhs
    rows,rhs=equations()
    if any(sum(a*x for a,x in zip(row,approximate))!=b for row,b in zip(rows,rhs)):
        n=len(support)
        basis={}
        for row,b in zip(rows,rhs):
            vector=[Q(x) for x in row]+[Q(b)]
            for pivot in sorted(basis):
                factor=vector[pivot]
                if factor:
                    old=basis[pivot]
                    for j in range(pivot,n+1):vector[j]-=factor*old[j]
            pivot=next((j for j,x in enumerate(vector[:-1]) if x),None)
            if pivot is None:
                E.need(vector[-1]==0,'Active integer system consistent')
            else:
                factor=vector[pivot]
                basis[pivot]=[x/factor for x in vector]
        E.need(len(basis)==n,'Active support is uniquely reconstructed')
        approximate=[Q(0)]*n
        for pivot in sorted(basis,reverse=True):
            row=basis[pivot]
            approximate[pivot]=row[-1]-sum(row[j]*approximate[j] for j in range(pivot+1,n))
        E.need(all(abs(float(x)-numbers[i])<1e-4 for x,i in zip(approximate,support)),
               'Exact active solution agrees with numerical discovery')
    E.need(all(x>=0 for x in approximate),'Reconstructed multiplicities nonnegative')
    return [{'family':columns[i][0],'pattern':list(columns[i][1]),'count':str(x)}
            for i,x in zip(support,approximate) if x]

def discover(p,minimum,c,max_rounds=300,fresh_groups=False,prefix_cut=False,
             custom_windows=None,custom_targets=None):
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    families=windows(p,prefix_cut) if custom_windows is None else [dict(w) for w in custom_windows]
    calls=2*p+1
    if fresh_groups:
        families.append({'name':'fresh_group','capacity':2*minimum+8,
                         'stages':list(range(calls)),'unbounded':True})
    maximum=minimum-1
    sp=lambda r:numerical_split(r,maximum,c)
    h=lambda r:r**(1-c) if r else 0
    v={r:h(max(r,minimum))-sp(max(0,minimum-r)) for r in WIDTHS[1:]}
    v[0]=0
    def gain(f,pattern):
        if families[f].get('unbounded'):
            used=sum(pattern)
            return (h(max(used,minimum))-sp(max(0,minimum-used)) if used else 0)-sum(v[r] for r in pattern)
        return sp(families[f]['capacity'])-sp(families[f]['capacity']-sum(pattern))-sum(v[r] for r in pattern)
    columns=[]
    keys=set()
    def add(f,pattern):
        key=(f,tuple(pattern))
        if key not in keys:
            keys.add(key)
            columns.append(key)
            return True
        return False
    for f,w in enumerate(families):
        add(f,[0]*len(w['stages']))
        for r in WIDTHS[1:]:
            # Seed every constant-width prefix and suffix that fits.
            n=min(len(w['stages']),w['capacity']//r)
            if n:
                add(f,[r]*n+[0]*(len(w['stages'])-n))
                add(f,[0]*(len(w['stages'])-n)+[r]*n)
    if not families:
        return [],{'columns':0,'rounds':0,'discovery_converged':True}
    resource=[(s,r) for s in range(calls) for r in WIDTHS[1:]]
    rid={key:i for i,key in enumerate(resource)}
    bounded=[f for f,w in enumerate(families) if not w.get('unbounded')]
    bid={f:i for i,f in enumerate(bounded)}
    done=False
    largest_reduced=None
    for iteration in range(max_rounds):
        ar=[];ac=[];av=[]
        er=[];ec=[];ev=[]
        objectives=[]
        for index,(f,pattern) in enumerate(columns):
            if f in bid:
                er.append(bid[f]);ec.append(index);ev.append(1)
            for stage,r in zip(families[f]['stages'],pattern):
                if r:
                    ar.append(rid[stage,r]);ac.append(index);av.append(1)
            objectives.append(-gain(f,pattern))
        A=coo_matrix((av,(ar,ac)),shape=(len(resource),len(columns))).tocsr()
        B=coo_matrix((ev,(er,ec)),shape=(len(bounded),len(columns))).tocsr()
        result=linprog(objectives,A_ub=A,b_ub=[E.HELPERS[r] for s,r in resource],
                       A_eq=B if bounded else None,b_eq=[families[f].get('field_count',224) for f in bounded] if bounded else None,bounds=(0,None),method='highs',
                       options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
        E.need(result.success,'Restricted master feasible')
        pi=result.ineqlin.marginals
        lam=result.eqlin.marginals
        new=0
        largest_reduced=0.0
        for f,w in enumerate(families):
            dp={0:(0.0,())}
            for stage in w['stages']:
                nxt={}
                for used,(score,pattern) in dp.items():
                    for r in WIDTHS:
                        if used+r>w['capacity']:
                            continue
                        score2=score-v[r]+(pi[rid[stage,r]] if r else 0)
                        if used+r not in nxt or score2>nxt[used+r][0]+1e-13:
                            nxt[used+r]=(score2,pattern+(r,))
                dp=nxt
            def terminal(used):
                if w.get('unbounded'):
                    return h(max(used,minimum))-sp(max(0,minimum-used)) if used else 0
                return sp(w['capacity'])-sp(w['capacity']-used)+lam[bid[f]]
            ranked=sorted(((score+terminal(used),pattern)
                           for used,(score,pattern) in dp.items()),reverse=True)
            largest_reduced=max(largest_reduced,ranked[0][0])
            # Several best used-capacity patterns reduce degeneracy.
            for improvement,pattern in ranked[:4]:
                if improvement>1e-8:
                    new+=add(f,pattern)
        if not new:
            done=True
            break
    # Rational reconstruction checks feasibility independently of floating duals.
    solution=reconstruct_exact(result.x,columns,families,resource,E.HELPERS)
    verify(p,minimum,solution,'H',fresh_groups=fresh_groups,prefix_cut=prefix_cut,
           custom_windows=custom_windows,custom_targets=custom_targets)
    return solution,{'columns':len(columns),'rounds':iteration+1,
                     'discovery_converged':done,'last_max_reduced_cost_float':largest_reduced,
                     'optimality_scope':'Floating column-generation screen only; rational receipt certifies displayed construction, not global optimum.'}

def verify(p,minimum,solution,kernel,fresh_groups=False,prefix_cut=False,
           custom_windows=None,custom_targets=None):
    E.need(kernel in ('H','identity'),'Known exact local invoice')
    calls=2*p+1
    maximum=minimum-1
    families=windows(p,prefix_cut) if custom_windows is None else [dict(w) for w in custom_windows]
    if fresh_groups:
        families.append({'name':'fresh_group','capacity':2*minimum+8,
                         'stages':list(range(calls)),'unbounded':True})
    counts=[Q(0) for _ in families]
    inventory=[Counter({r:Q(n) for r,n in E.HELPERS.items()}) for _ in range(calls)]
    source=E.NATIVE if kernel=='H' else IDENTITY
    paid=E.split_profile(source,maximum)
    paid=Counter({r:Q(calls*n) for r,n in paid.items()})
    if kernel=='H':
        paid[1]+=8*calls
    targets=(Counter({16*p+9-16*j:Q(224) for j in range(p)}) if prefix_cut
             else Counter({16*p+9:Q(224*p)}))
    if custom_targets is not None:
        targets=Counter({int(r):Q(n) for r,n in custom_targets.items()})
        E.need(sum(targets.values())==224*p,'Changed main targets have the original data field count')
        expected_total=sum(r*n for r,n in targets.items())-sum(w.get('field_count',224)*w['capacity'] for w in families if not w.get('unbounded'))
        old_total=224*p*(16*p+9)-sum(224*w['capacity'] for w in windows(p))
        E.need(expected_total==old_total,'Literal removed windows match the changed main rank credit')
    for row in solution:
        f=row['family'];pattern=row['pattern'];count=Q(row['count'])
        E.need(0<=f<len(families) and count>=0,'Pattern count')
        w=families[f]
        E.need(len(pattern)==len(w['stages']) and set(pattern)<=set(WIDTHS),'Window chronology')
        E.need(sum(pattern)<=w['capacity'],'Window capacity')
        counts[f]+=count
        for stage,r in zip(w['stages'],pattern):
            if r:
                inventory[stage][r]-=count
        if w.get('unbounded'):
            E.need(sum(pattern)>0,'A fresh productive group consumes some actual helper')
            targets[max(sum(pattern),minimum)]+=count
            E.add_scaled(paid,E.split_rank(max(0,minimum-sum(pattern)),maximum),count)
        else:
            E.add_scaled(paid,E.split_rank(w['capacity']-sum(pattern),maximum),count)
    E.need(all(n==w.get('field_count',224) for n,w in zip(counts,families) if not w.get('unbounded')),
           'Every idle window accounted')
    global_roles=Counter()
    for stage,stock in enumerate(inventory):
        E.need(all(n>=0 for n in stock.values()),'Stage inventory '+str(stage))
        global_roles.update(stock)
    for r,n in global_roles.items():
        if n:
            targets[max(r,minimum)]+=n
            E.add_scaled(paid,E.split_rank(max(0,minimum-r),maximum),n)
    paid=+paid;targets=+targets
    E.need(max(paid)<min(targets),'Strict children')
    signed=Counter(targets);signed.subtract(paid)
    margin=sum(r*n for r,n in signed.items())
    want=224*p-(8 if kernel=='H' else 64)*calls
    E.need(margin==want,'Whole recursive rank credit minus all displayed costs')
    lift=lcm(*(Q(row['count']).denominator for row in solution)) if solution else 1
    return {'p':p,'kernel':kernel,'minimum_target_parameter':minimum,
            'fresh_groups':fresh_groups,
            'prefix_cut':prefix_cut,
            'custom_main_targets':{str(r):str(n) for r,n in sorted(custom_targets.items())} if custom_targets is not None else None,
            'replica_lift':lift,'targets':{str(r):str(n) for r,n in sorted(targets.items())},
            'paid':{str(r):str(n) for r,n in sorted(paid.items())},
            'signed':signed,'rank_margin':str(margin),
            'global_helper_roles':{str(r):str(n) for r,n in sorted(global_roles.items())},
            'strict_separation':{'max_child':max(paid),'min_target':min(targets)},
            'patterns':solution,'windows':families}

def serialize(case,targets=('0.001745','0.004')):
    out={k:v for k,v in case.items() if k!='signed'}
    out['invoices']={c:E.show(E.moment(case['signed'],Q(c))) for c in targets}
    return out

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--min-p',type=int,default=1)
    parser.add_argument('--max-p',type=int,default=8)
    parser.add_argument('--min-k',type=int,default=5)
    parser.add_argument('--max-k',type=int,default=12)
    parser.add_argument('--C',default='0.001745')
    parser.add_argument('--fresh-groups',action='store_true')
    parser.add_argument('--prefix-cut',action='store_true')
    parser.add_argument('--output',type=Path,default=HERE/'MIXED-FOREST-SEARCH.json')
    args=parser.parse_args()
    candidates=[]
    for p in range(args.min_p,args.max_p+1):
        for minimum in range(args.min_k,args.max_k+1):
            solution,discovery=discover(p,minimum,float(args.C),fresh_groups=args.fresh_groups,
                                        prefix_cut=args.prefix_cut)
            for kernel in ('H','identity'):
                case=verify(p,minimum,solution,kernel,fresh_groups=args.fresh_groups,
                            prefix_cut=args.prefix_cut)
                case['discovery']=discovery
                candidates.append(case)
        current=[case for case in candidates if case['p']==p and case['kernel']=='identity']
        best=max(current,key=lambda x:E.numerical_value(x['signed'],float(args.C)))
        print(json.dumps({'p':p,'identity_best_minimum':best['minimum_target_parameter'],
                          'margin_float':E.numerical_value(best['signed'],float(args.C)),
                          'replica_lift':best['replica_lift']}),flush=True)
        # Preserve a useful receipt after each complete p, not only at the end.
        winners={}
        for kernel in ('H','identity'):
            for count in range(args.min_p,p+1):
                rows=[case for case in candidates if case['p']==count and case['kernel']==kernel]
                win=max(rows,key=lambda x:E.numerical_value(x['signed'],float(args.C)))
                winners[f'{kernel}_p{count}']=serialize(win)
        receipt={'schema':'mixed-target-productive-forest/1','status':'PASS_EXACT_DISPLAYED_INVOICES',
                 'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
                 'enclosure_source_sha256':sha256((HERE/'mixed_target_probe.py').read_bytes()).hexdigest(),
                 'discovery_C':args.C,'completed_p':p,'minimum_target_menu':[args.min_k,args.max_k],
                 'best_in_finite_search':winners,
                 'not_proved':['native variable-target owner emission and helper block adapters',
                               'H caller closure; identity entries assume the source full-identity invoice really supplies the required helper contract',
                               'all-size mixed recursion, fixed-tape router, finite precision and outer multiplication transfer'],
                 'new_kappa':False}
        args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    main()
