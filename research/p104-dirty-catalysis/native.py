#!/usr/bin/env python3
"""Exact native recipes for104 retimed Y lifts; independent Pauli+phase check."""
import argparse,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];NATIVE=ROOT/'research/p104-native-channel'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--generate',action='store_true');args=ap.parse_args()
    V=module('late_delivery_verify',P/'verify.py');word,_=V.sources()
    cert=json.loads(gzip.decompress((NATIVE/'NATIVE-RECIPES.json.gz').read_bytes()))
    N=module('late_independent_native',NATIVE/'vendor/native_verify.py')
    iso=cert['label_isometry'];dual=iso['compressed_dual_gram'];orth=iso['orthonormal_basis_compressed']
    mv=lambda rows,x:sum(((r&x).bit_count()&1)<<i for i,r in enumerate(rows))
    dot=lambda a,b:(a&mv(dual,b)).bit_count()&1
    need(all(dot(a,b)==int(i==j) for i,a in enumerate(orth) for j,b in enumerate(orth)),'physical isometry')
    convert=lambda x:sum(dot(x,v)<<j for j,v in enumerate(orth))
    def basis(vs):
        # compiler canonical_frame expects any independent basis, not RREF.
        return tuple(map(convert,vs))
    full=tuple(1<<i for i in range(9))
    def physical_old(i):
        terminal=max(k for k,e in enumerate(word['program']) if e[0]=='transport' and e[1]==f'Y{i}')
        retained=next(t for t in cert['transports'] if terminal in t['events'])
        need(V.span(retained['new'])==V.span(basis(word['final_frames'][f'Y{i}'])),'physical terminal frame span')
        return tuple(retained['new'])
    if args.generate:
        C=module('late_native_compiler',NATIVE/'vendor/clifford_exact.py');records=[]
        for i in range(104):
            old=physical_old(i);op=C.canonical_frame(9,old).adjoint().then(C.canonical_frame(9,full));recipe,_=C.lower_child(op)
            records.append({'role':f'Y{i}','old':list(old),'new':list(full),'recipe':recipe})
        (P/'LIFT-RECIPES.json').write_text(json.dumps(records,sort_keys=True,indent=2)+'\n')
    records=V.load(P/'LIFT-RECIPES.json');need(len(records)==104,'104 lifts')
    for i,r in enumerate(records):
        old=physical_old(i);need(r['role']==f'Y{i}' and r['old']==list(old) and r['new']==list(full),'literal Y endpoint binding')
        need(r['recipe']['rank']==1,'one positive rank1 child')
        terminal=max(k for k,e in enumerate(word['program']) if e[0]=='transport' and e[1]==f'Y{i}')
        retained=next(t for t in cert['transports'] if terminal in t['events'])
        N.equal(N.frame(old,9),N.frame(retained['new'],9),'same retained canonical Y frame')
        N.equal(N.recipe(r['recipe']),N.adjoint(N.frame(old,9))+N.frame(full,9),'native lift'+str(i))
    # A representative exhaustive512-column comparison complements the complete
    # signed-Pauli and exact-phase criterion used on every one of104 operators.
    r=records[0];actual=N.recipe(r['recipe']);expected=N.adjoint(N.frame(r['old'],9))+N.frame(r['new'],9)
    for col in range(512):need(N.state(actual,col)==N.state(expected,col),'representative Gaussian column')
    bad=json.loads(json.dumps(r['recipe']));bad['left']['phase']=(bad['left']['phase']+1)%4
    try:N.equal(N.recipe(bad),actual,'phase mutation')
    except (ValueError,AssertionError):pass
    else:raise ValueError('phase control accepted')
    print('PASS_P104_LATE_LIFTS exact_native_operators=104 rank1=104 exhaustive_representative_columns=512 phase_control=1')
if __name__=='__main__':main()
