#!/usr/bin/env python3
"""Exact legal common-cut insertions; no endpoint rank improvement claim."""
from pathlib import Path
import hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CP=Path('/Users/ross/git/math/integer-mult-bounds/research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py')
def need(b,m):
    if not b:raise ValueError(m)
def main():
    need(hashlib.sha256(CP.read_bytes()).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','compiler pin')
    sp=importlib.util.spec_from_file_location('insertion_supplement_ce',CP);ce=importlib.util.module_from_spec(sp);sys.modules[sp.name]=ce;sp.loader.exec_module(ce)
    n=4;p,q,past,future=1,2,4,8
    def same(a,b,m):need(a.tab==b.tab and a.zero_state()==b.zero_state(),m)
    def lower(a):
        r,l=ce.lower_child(a);same(a,l,'literal native phase lowering');return r
    Cp,Cq=ce.cgate(n,p),ce.cgate(n,q);Gpast=ce.cgate(n,past)
    DX=Gpast.then(Cp);DY=Gpast.then(Cq);K=Cp.adjoint().then(Cq)
    # A nonorthogonal order-three address map on common (p,q), with the
    # common-pair quadratic chirp required for simultaneous admission.
    M=ce.perm(n,[2,3,4,8]).then(ce.diag(n,[3,1,0,0]))
    need(lower(M)['rank']==lower(K.adjoint().then(M).then(K))['rank']==0,'common-axis order3 map admitted at both physical banks')
    H=DX.then(M).then(DX.adjoint())
    same(DX.adjoint().then(H).then(DX),M,'actual X dressing')
    need(lower(DY.adjoint().then(H).then(DY))['rank']==0,'actual Y dressing also monomial')
    missing_chirp=ce.perm(n,[2,3,4,8])
    need(lower(K.adjoint().then(missing_chirp).then(K))['rank']>0,'omitting chirp is a real hidden-cut defect')
    # A physical past/future ADDRESS swap preserves the current pair's
    # intersection, but its logical dressing transfers a completed-past
    # Lagrangian direction into an uncompleted-future direction.
    swap=ce.perm(n,[1,2,8,4]);Hs=DX.then(swap).then(DX.adjoint())
    need(lower(DX.adjoint().then(Hs).then(DX))['rank']==lower(DY.adjoint().then(Hs).then(DY))['rank']==0,'dressed fresh swap is admitted at both banks')
    def image(op,x,z):
        xx=zz=0
        for j in range(n):
            if x>>j&1:xx^=op.tab[j][0];zz^=op.tab[j][1]
            if z>>j&1:xx^=op.tab[n+j][0];zz^=op.tab[n+j][1]
        return xx,zz
    need(image(Hs,past,past)==(0,future),'past F^-1Z can move to future Z within the admitted intersection')
    hidden=lower(DX.adjoint().then(swap).then(DX))['rank']
    need(hidden==2,'undressed logical swap would cost native rank2')
    out=dict(status='PASS_LEGAL_COMMON_AXIS_AND_PAST_FUTURE_INSERTIONS_NO_ENDPOINT_CLAIM',
             compiler_sha256=hashlib.sha256(CP.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             common_axis_physical=lower(M),common_axis_logical_events=H.circuit,
             common_axis_X_cut=lower(DX.adjoint().then(H).then(DX)),common_axis_Y_cut=lower(DY.adjoint().then(H).then(DY)),
             fresh_swap_X_cut=lower(DX.adjoint().then(Hs).then(DX)),fresh_swap_Y_cut=lower(DY.adjoint().then(Hs).then(DY)),
             completed_past_input=[past,past],uncompleted_future_output=[0,future],undressed_swap_cut_rank=hidden,
             limits=['No actual D4 B1 endpoint improvement is proved.','Preservation of the full common-cut intersection does not imply preservation of its past and future pieces.','The physical dressing is essential; counting the undressed logical swap as native-zero is wrong.','All statements tensor-lift, but field permutation/phase scans remain paid.'])
    (HERE/'INSERTION-SUPPLEMENT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])
if __name__=='__main__':main()
