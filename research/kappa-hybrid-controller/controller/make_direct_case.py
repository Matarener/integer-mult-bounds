#!/usr/bin/env python3
"""Regenerate and compare the exact p17 rational Laurent specialization.

The original complex controller, rational algebra, and binary discovery source
are authenticated at --source-root. Sparse multiplication omits zero summands
but uses exact rational arithmetic. Every acceptance guard survives python -O.
Native source/geometry and interval transfer are independently audited elsewhere.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PINS={
    'research/kappa-rebuild/bit/complex_controller_factor.py':'1de9aaf918e6a4f2f5448754c1f3c3da3b85e6257849ebd097af09859c4e5497',
    'research/kappa-rebuild/bit/mixed_productive_bit.py':'b32291b0db7fc0d332ec444c70746ab0fb03351d2e50546f8bcb64060e3ff95e',
    'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/bit-compression/carrier-reuse/reference/joint_pair_dag.py':'8a0de761642d21919e969475c3f13e5d01a4bae7343c1e1f37c586d94b676a85',
}
PAIRS=17
CUT=8
KEEP=280378328416255
NATIVE=28633115307
HELPERS={4:26,5:2,7:29,8:42,9:309}
LOCAL_PAID={1:2253,2:515,3:445,4:102,5:40,8:8}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def authenticated(source_root):
    root=Path(source_root).resolve()
    for relative,expected in PINS.items():
        need(sha256((root/relative).read_bytes()).hexdigest()==expected,'Pinned original source: '+relative)
    paths=list(PINS)
    load(root/paths[2],'joint_pair_dag')
    algebra=load(root/paths[1],'mixed_productive_bit')
    controller=load(root/paths[0],'p17_original_complex_controller')
    return controller,algebra


def sparse_multiply(a,b):
    need(bool(a) and bool(b) and len(a[0])==len(b),'Matrix dimensions')
    result=[[Q(0) for _ in b[0]] for row in a]
    sparse_b=[[(j,x) for j,x in enumerate(row) if x] for row in b]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in sparse_b[k]:
                    result[i][j]+=x*y
    return result


def specialize(term):
    return (term[0],)+tuple(x if NATIVE>>s&1 else 0 for s,x in enumerate(term[1:]))


def collapse(coefficients):
    result={}
    for term,matrix in coefficients.items():
        key=specialize(term)
        if key not in result:
            result[key]=[row[:] for row in matrix]
        else:
            result[key]=[[x+y for x,y in zip(a,b)] for a,b in zip(result[key],matrix)]
    return {key:matrix for key,matrix in result.items() if any(any(row) for row in matrix)}


def encode(value):
    return (json.dumps(value,indent=2)+'\n').encode()


def generate(source_root):
    C,B=authenticated(source_root)
    B.matrix_multiply=sparse_multiply
    need(NATIVE==sum(1<<s for s in range(35) if s in (0,34) or s%2),
         'Exactly the sixteen internal even stages are direct')
    coefficients,events,idles=C.controller(PAIRS,KEEP)
    factored=C.factor(coefficients)
    need(factored is not None,'Full rational Laurent factorization')
    original=C.serialize_case(PAIRS,KEEP,coefficients,events,idles,factored)
    full_sha=sha256(encode(original)).hexdigest()
    specialized=collapse(coefficients)
    diagonal=[specialize(term) for term in factored['diagonal']]
    transformed={key:sparse_multiply(sparse_multiply(factored['left'],matrix),factored['right'])
                 for key,matrix in specialized.items()}
    expected={term:[[Q(i==j and diagonal[i]==term) for j in range(34)] for i in range(34)]
              for term in set(diagonal)}
    need(transformed==expected,'Every specialized Laurent coefficient equals the claimed diagonal')
    wrong,_,_=C.controller(PAIRS,KEEP,wrong_reverse_sign=True)
    wrong_transformed={key:sparse_multiply(sparse_multiply(factored['left'],matrix),factored['right'])
                       for key,matrix in collapse(wrong).items()}
    need(wrong_transformed!=expected,'Wrong backward sign rejected after specialization')
    binary,_,_=B.physical_controller(PAIRS,KEEP)
    binary_factor=B.simultaneous_monomial_factor(binary)
    need(binary_factor is not None,'Separate binary profile cross-check')
    main=Counter()
    for term in diagonal:
        need(term[0] in (-1,1) and all(x in (0,1) for x in term[1:]),'Only explicit Q signs and active stage factors')
        main[1+8*sum(term[1:])]+=112
    binary_main=Counter()
    for monomial in binary_factor['diagonal_monomials']:
        binary_main[1+8*((monomial>>1)&NATIVE).bit_count()]+=112
    need(main==binary_main,'Exact complex and binary job widths agree')
    native_count=NATIVE.bit_count()
    direct_count=35-native_count
    need(native_count==19 and direct_count==16,'Native/direct stage inventory')
    paid=Counter({k:native_count*v for k,v in LOCAL_PAID.items()})
    paid[1]+=112*direct_count
    productive=Counter({k:native_count*v for k,v in HELPERS.items()})+main
    windows=[]
    for idle in idles:
        if not idle['retained']:
            continue
        active=[s for s in idle['stages'] if NATIVE>>s&1]
        rank=8*len(active)
        if rank:
            paid[rank]+=224
        windows.append(dict(**idle,active_stages=active,specialized_rank=rank))
    need(main==Counter({**{k:448 for k in range(17,74,8)},153:224}),'Exact main productive profile')
    need(sum(main.values())==34*112,'Every main input field contributes one productive output')
    need(sum(k*v for k,v in productive.items())-sum(k*v for k,v in paid.items())==800,'Exact raw rank-mass margin')
    result=dict(schema='exact-p17-direct-stage-Laurent-specialization/1',
                source_sha256=PINS,source_full_case_sha256=full_sha,
                pairs=PAIRS,cut=CUT,keep_idle_mask=KEEP,native_stage_mask=NATIVE,
                native_stages=[s for s in range(35) if NATIVE>>s&1],
                direct_stages=[s for s in range(35) if not(NATIVE>>s&1)],
                coefficient_variables=original['coefficient_variables'],
                specialized_coefficient_matrices=[dict(exponents=list(key),matrix=C.serialize_matrix(matrix))
                                                   for key,matrix in sorted(specialized.items())],
                left=original['left'],right=original['right'],
                left_program=original['left_program'],right_program=original['right_program'],
                exact_diagonal_monomials=[list(term) for term in diagonal],
                every_specialized_Laurent_coefficient_checked=True,
                incorrect_backward_sign_rejected=True,
                main_productive_profile=dict(sorted(main.items())),
                native_helper_profile=HELPERS,native_paid_profile=LOCAL_PAID,
                native_invocations=native_count,direct_Q_shears=direct_count,
                direct_rank1_children=112*direct_count,
                complete_paid_profile=dict(sorted(paid.items())),
                complete_productive_profile=dict(sorted(productive.items())),
                retained_idle_windows=windows,
                ambient_dimension_with_all_original_stage_coordinates=9+16*PAIRS,
                full_Laurent_identity=True,
                physical_direct_shear_and_native_source_bindings_are_separate=True,
                no_interval_or_rounded_transfer_claim=True)
    return {'P17-FULL-LAURENT-CASE.json':original,'P17-DIRECT-CASE.json':result}


def run(source_root,out=HERE,write=False):
    generated=generate(source_root)
    hashes={}
    out=Path(out)
    if write:
        out.mkdir(parents=True,exist_ok=True)
    for name,value in generated.items():
        data=encode(value)
        path=out/name
        if write:
            path.write_bytes(data)
        else:
            need(path.read_bytes()==data,'Exact regenerated receipt bytes: '+name)
        hashes[name]=sha256(data).hexdigest()
    return dict(status='PASS_EXACT_P17_LAURENT_SPECIALIZATION',source_sha256=PINS,
                artifacts=hashes,native_invocations=19,direct_rank1_children=1792,
                incorrect_backward_sign_rejected=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=HERE.parents[2])
    parser.add_argument('--out',type=Path,default=HERE)
    parser.add_argument('--write',action='store_true',help='Write regenerated receipts instead of comparing them')
    args=parser.parse_args()
    print(json.dumps(run(args.source_root,args.out,args.write),sort_keys=True))
