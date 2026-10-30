#!/usr/bin/env python3
"""Bounded exact corroboration and literal checks for PROOF.md.
SHIN09-git, substantial OpenAI Codex assistance. Apache-2.0.
Finite checks corroborate; the all-field assertion is the written proof.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time
from types import ModuleType

HERE=Path(__file__).resolve().parent
BOUND_FILES=("linear.py","construct.py","oracle.py","check_witnesses.py","verify.py",
             "PROOF.md","README.md","TASK.json","SOURCES.json","VERIFY.json",
             "OVERLAP.json","reference6031.py","reference6031.md","reference5128.md","LICENSE",
             "ternary_orbits.py","test_mutations.py","reference6053.md","AUDIT.md")

def load(name):
    path=HERE/(name+".py")
    mod=ModuleType(name)
    mod.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),"exec"),mod.__dict__)
    return mod

c=load("construct")
o=load("oracle")
ind=load("check_witnesses")
ref=load("reference6031")
need=c.need

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()

def reviewed_closed_rank(A,B,H):
    # apoursh PR6053, equation (1), independently evaluated here.
    F,J=A-H,B-H
    return (J@A.inverse()@F).rank()+(F@B.inverse()@J).rank()+2*H.rank()-2*A.r

def all_matrices(d,p):
    for flat in product(range(p),repeat=d*d):
        yield tuple(tuple(flat[i*d:(i+1)*d]) for i in range(d))

def domains(quick=False,ternary_representatives=None):
    m2=list(all_matrices(2,2))
    gl2=[a for a in m2 if o.rank_vectors(a,2)==2]
    binary=list(product(gl2,gl2,m2))
    for A,B,H in (binary[::71] if quick else binary):
        yield "binary_quick" if quick else "binary_complete",2,A,B,H,True
    m3=list(all_matrices(2,3))
    gl3=[a for a in m3 if o.rank_vectors(a,3)==2]
    pairs=[(a,b) for a in gl3 for b in gl3 if o.mm(a,b,3)!=o.mm(b,a,3)]
    pairs=[pairs[i*len(pairs)//8] for i in range(8)]
    if quick:
        for A,B in pairs:
            for H in m3[::20]:
                yield "ternary_eight_pairs",3,A,B,H,True
    else:
        need(ternary_representatives is not None,"complete ternary partition required")
        for A,B,H in ternary_representatives:
            yield "ternary_complete_up_to_conjugacy",3,A,B,H,True
    A=((0,1,0),(0,0,1),(1,0,0))
    B=((1,1,0),(0,1,1),(0,0,1))
    m32=list(all_matrices(3,2))
    for H in (m32[::127] if quick else m32):
        yield "binary_d3_all_H",2,A,B,H,True
    for p in (0,2,3,5,7,11):
        for d in range(1,5):
            A=[list(row) for row in c.eye(d,p).a]
            B=[list(row) for row in c.eye(d,p).a]
            if d>1:
                A[0][1]=Fraction(1,2) if not p else 1
                B[1][0]=Fraction(1,3) if not p else 1
            A,B=c.Mat(A,p),c.Mat(B,p)
            candidates=[c.zeros(d,d,p),c.eye(d,p),A,B,A+B-c.eye(d,p),A@B,B@A,
                        c.Mat([[i+2 if i==j else 0 for j in range(d)] for i in range(d)],p)]
            if p==0:
                candidates.append(c.Mat([[Fraction(i+1,i+2) if i==j else 0 for j in range(d)] for i in range(d)],0))
            for H in {H.a:H for H in candidates}.values():
                yield "structured_Q_and_prime_fields",p,A.a,B.a,H.a,False

def fixture(A,B,H,rho,state):
    P,Q=c.build(A,B,H,state)
    need(c.literal_rank(A,B,H,P,Q)==rho,"primary literal rank")
    rec={"field":A.p,"d":A.r,"n":P.r,"rho":rho,
         "A":A.json(),"B":B.json(),"H":H.json(),"P":P.json(),"Q":Q.json()}
    ind.check(rec)
    return rec

def core_minor_census(quick=False):
    total=0
    digest=sha256()
    for p,d in ((2,2),(3,2),(2,3)):
        matrices=list(all_matrices(d,p))
        if quick:
            matrices=matrices[::max(1,len(matrices)//8)]
        subsets=[s for n in range(d+1) for s in combinations(range(d),n)]
        for raw in matrices:
            C=c.Mat(raw,p)
            r=o.rank_vectors(raw,p)
            best={}
            for ii in subsets:
                for jj in subsets:
                    entries=tuple(tuple(raw[i][j] for j in jj) for i in ii)
                    rr=o.rank_vectors(entries,p)
                    rho=2*d-len(ii)-len(jj)+rr
                    cost=2*d-len(ii)-len(jj)
                    best[rho]=min(best.get(rho,10**9),cost)
            actual={}
            for ii,jj,kind in c.minor_chain(C):
                rr=o.rank_vectors(tuple(tuple(raw[i][j] for j in jj) for i in ii),p)
                rho=2*d-len(ii)-len(jj)+rr
                actual[rho]=2*d-len(ii)-len(jj)
            need(actual==best,"minor-chain vs complete independent subset census")
            need(actual=={rho:max(rho-r,2*rho-2*d) for rho in range(r,2*d+1)},"pure minor cost law")
            digest.update(canonical([p,raw,sorted(actual.items())])+b"\n")
            total+=1
    return {"matrices":total,"sha256":digest.hexdigest()}

def controls(examples):
    rejected=[]
    def rejects(name,rec):
        try:
            ind.check(rec)
        except (ValueError,ZeroDivisionError):
            rejected.append(name)
        else:
            raise ValueError("independent checker accepted "+name)
    ordinary=next(x for x in examples if x["field"]==3 and x["rho"]>0)
    bad=deepcopy(ordinary); bad["rho"]-=1; rejects("wrong_rank",bad)
    bad=deepcopy(ordinary); bad["n"]+=1; rejects("wrong_dimension",bad)
    bad=deepcopy(ordinary); bad["H"][0][0]=(bad["H"][0][0]+1)%3; rejects("wrong_product_block",bad)
    bad=deepcopy(ordinary); bad["P"][0][0]=(bad["P"][0][0]+1)%3; rejects("changed_P_entry",bad)
    bad=deepcopy(ordinary); bad["A"]=[[0]*bad["d"] for _ in range(bad["d"])]; rejects("singular_pivot",bad)
    bad=deepcopy(ordinary); bad["d"]=True; rejects("boolean_dimension",bad)
    bad=deepcopy(ordinary); bad["P"][0][0]+=3; rejects("noncanonical_field_value",bad)
    bad=deepcopy(ordinary); bad["field"]=4; rejects("unsupported_composite_modulus",bad)
    A=c.eye(2,3)
    states=c.plan(A,A,A)["states"]
    need(states[1]["n"]==4 and states[1]["n"]!=3,"slope-one-only control")
    rejected.append("slope_one_only_formula")
    need(states[0]["n"]!=states[4]["n"],"maximal-only control")
    rejected.append("maximal_dimension_at_every_rank")
    return rejected

def run(quick=False,all_fixtures=False):
    start=time.perf_counter()
    sources=json.loads((HERE/"SOURCES.json").read_bytes())
    for row in sources["files"]:
        if "vendored_as" in row:
            need(sha256((HERE/row["vendored_as"]).read_bytes()).hexdigest()==row["sha256"],
                 "frozen reference changed")
    summaries={}
    digest=sha256()
    profile_digest=sha256()
    examples=[]
    kept=set()
    all_records=[]
    binary_ref_comparisons=0
    unique=set()
    ternary,coverage=(None,None) if quick else load("ternary_orbits").partition()
    for group,p,a,b,h,enumerate_spaces in domains(quick,ternary):
        A,B,H=(c.Mat(x,p) for x in (a,b,h))
        unique.add(canonical([p,A.json(),B.json(),H.json()]))
        plan=c.plan(A,B,H)
        need(reviewed_closed_rank(A,B,H)==plan["rho0"],"PR6053 ordered closed rho0")
        actual={rho:state["n"] for rho,state in plan["states"].items()}
        if enumerate_spaces:
            exact,count=o.profile(a,b,h,p)
            need(actual==exact,"complete subspace oracle disagrees")
        else:
            count=0
        if p==2 and len(a)==2 and group.startswith("binary"):
            _,original,_,r0=ref.profile(*[[list(row) for row in X] for X in (a,b,h)])
            need(actual==original and plan["rho0"]==r0,"frozen PR6031 comparison")
            binary_ref_comparisons+=1
        d=A.r
        G,Gp=c.ordered_maps(A,B,H)
        active=plan["sectors"][1:]
        T=c.block([[active[i] if i==j else c.zeros(d,d,p) for j in range(3)] for i in range(3)])
        need((T@G@Gp@T).rank()==plan["rho0"],"baseline T G G' T identity")
        row=summaries.setdefault(group,{"triples":0,"literal_witnesses":0,"subspace_pairs":0,
                                      "noncommuting_pivot_triples":0,"rho0_counts":{},
                                      "two_phase_triples":0})
        row["triples"]+=1
        row["subspace_pairs"]+=count
        row["noncommuting_pivot_triples"]+=int(A@B!=B@A)
        row["rho0_counts"][str(plan["rho0"])]=row["rho0_counts"].get(str(plan["rho0"]),0)+1
        row["two_phase_triples"]+=int(0<plan["pairing_rank"]<plan["nu"])
        profile_digest.update(canonical([group,p,A.json(),B.json(),H.json(),sorted(actual.items())])+b"\n")
        for rho,state in plan["states"].items():
            rec=fixture(A,B,H,rho,state)
            digest.update(canonical(rec)+b"\n")
            row["literal_witnesses"]+=1
            tag=(p,d,rho,plan["nu"],plan["pairing_rank"])
            if tag not in kept and (len(examples)<18 or p not in {x["field"] for x in examples}):
                kept.add(tag)
                examples.append(rec)
            if p==3 and rho>0 and not any(x["field"]==3 and x["rho"]>0 for x in examples):
                examples.append(rec)
            if all_fixtures:
                all_records.append(rec)
    minor=core_minor_census(quick)
    summary={"schema_version":1,"scope":"finite corroboration of all-field proof; no kappa or supplier",
             "mode":"quick" if quick else "complete declared domains",
             "domains":summaries,"unique_triples":len(unique),
             "binary_reference_comparisons":binary_ref_comparisons,
             "PR6053_closed_formula_comparisons":sum(x["triples"] for x in summaries.values()),
             "complete_ternary_coverage":coverage,
             "literal_witnesses":sum(x["literal_witnesses"] for x in summaries.values()),
             "subspace_pairs":sum(x["subspace_pairs"] for x in summaries.values()),
             "profile_sha256":profile_digest.hexdigest(),"literal_witness_sha256":digest.hexdigest(),
             "independent_minor_subset_census":minor,"controls_rejected":controls(examples),
             "source_sha256":{name:sha256((HERE/name).read_bytes()).hexdigest() for name in BOUND_FILES}}
    print("computed",summary["unique_triples"],"unique triples;",summary["literal_witnesses"],
          "literal witnesses; seconds",round(time.perf_counter()-start,3),file=sys.stderr,flush=True)
    return summary,examples,all_records

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--quick",action="store_true")
    ap.add_argument("--emit-receipt",action="store_true")
    ap.add_argument("--emit-examples",action="store_true")
    ap.add_argument("--emit-fixtures",action="store_true")
    args=ap.parse_args()
    summary,examples,fixtures=run(args.quick,args.emit_fixtures)
    if args.emit_receipt:
        print(json.dumps(summary,indent=2,sort_keys=True))
    elif args.emit_examples:
        print(json.dumps(examples,indent=2))
    elif args.emit_fixtures:
        print(json.dumps(fixtures,separators=(",",":")))
    elif args.quick:
        print("PASS_SCHUR_RANK_ATTAINMENT_QUICK")
    else:
        expected=json.loads((HERE/"RESULT.json").read_bytes())
        need(canonical(summary)==canonical(expected),"source-bound exact receipt mismatch")
        print("PASS_SCHUR_RANK_ATTAINMENT",summary["unique_triples"],summary["literal_witnesses"])

if __name__=="__main__":
    main()
