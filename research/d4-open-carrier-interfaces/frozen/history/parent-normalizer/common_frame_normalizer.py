#!/usr/bin/env python3
"""Construct OPEN-C normalizers preserving both zero and full native cuts.

Apache-2.0; substantial OpenAI Codex assistance. No global caller claimed.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CP = Path('/Users/ross/git/math/integer-mult-bounds/research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py')


def need(b, m):
    if not b:
        raise ValueError(m)


def main():
    sha = hashlib.sha256(CP.read_bytes()).hexdigest()
    need(sha == '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962', 'compiler pin')
    sp = importlib.util.spec_from_file_location('common_frame_ce', CP)
    ce = importlib.util.module_from_spec(sp)
    sys.modules[sp.name] = ce
    sp.loader.exec_module(ce)
    buspath = HERE.parent/'complex-boundary/paired-pivot/D4-BUS-INPUT.json'
    bus = json.loads(buspath.read_text())
    n = 7
    core = [g[0] for g in bus['groups7']]
    chart = ce.perm(n, ce.inv(ce.transpose(core+[5,53,30,96], n), n))
    D = chart.then(ce.hadamard(n, [3,4])).then(chart.adjoint()).then(ce.Op(n, ce.identity(n), [('phase',3)]))
    VC = D.then(ce.cgate(n, core[0])).then(ce.cgate(n, core[1]))
    F = ce.fourier(n).then(ce.xgate(n,33))
    def same(a,b,m):
        need(a.tab == b.tab and a.zero_state() == b.zero_state(), m)
    def lower(a):
        rec, lit = ce.lower_child(a)
        same(a,lit,'full phase native lowering')
        return rec
    def matmul(a,b):
        cols = ce.transpose(b,n)
        return ce.transpose([ce.mv(a,v) for v in cols],n)
    rows = []
    for j,p in enumerate(bus['groups7'][2]):
        q = bus['groups7'][0][j]
        Cp,Cq = ce.cgate(n,p),ce.cgate(n,q)
        S = Cp.adjoint().then(VC)
        T = Cp.adjoint().then(Cq.adjoint()).then(F)
        # W_A = {v : A(v,v) has zero X component}; it represents
        # A^-1 Z intersect F^-1 Z, ignoring irrelevant Pauli phases.
        def W(A):
            return ce.nullspace(ce.transpose([A.tab[i][0]^A.tab[n+i][0] for i in range(n)],n),n)
        wt,ws = W(T),W(S)
        need(len(wt)==len(ws)==5,'both full-frame intersections have dimension5')
        bt,bs = ce.basis_extend(wt,n),ce.basis_extend(ws,n)
        G = matmul(ce.transpose(bs,n),ce.inv(ce.transpose(bt,n),n))
        Gi = ce.inv(G,n)
        metric = matmul(ce.transpose(Gi,n),Gi)
        Q = tuple((1<<i)^metric[i] for i in range(n))
        pre = ce.perm(n,G).then(ce.diag(n,Q))
        post = S.adjoint().then(pre.adjoint()).then(T)
        fullcut = F.adjoint().then(pre).then(F)
        need(lower(pre)['rank']==lower(post)['rank']==lower(fullcut)['rank']==0,'two endpoint cuts and source normalization are all monomial')
        same(pre.then(S).then(post),T,'source normalization exact on all inputs')
        J = ce.xgate(n,p).then(F)
        K = pre.then(J).then(T.adjoint())
        A = Cp.then(K).then(Cq.adjoint())
        same(A,Cp.then(pre).then(Cp.adjoint()),'actual logical A')
        DX = Cp
        DY = Cp.adjoint().then(F)
        entry = DX.adjoint().then(A.adjoint()).then(DX)
        exitop = DY.adjoint().then(A.adjoint()).then(DY)
        need(lower(entry)['rank']==lower(exitop)['rank']==0,'canonical forward pre-X and post-Y are both free native cuts')
        AB = K.adjoint().then(T.adjoint()).then(K.adjoint()).then(T)
        BB = T.adjoint().then(AB.adjoint()).then(T)
        same(AB.then(T.adjoint()).then(K).then(T.then(T)),K.adjoint().then(T),'corrected inverseB cross')
        rows.append(dict(p=p,q=q,W_T=wt,W_S=ws,G=G,Q=Q,pre_events=pre.circuit,post_events=post.circuit,
                         pre_native=lower(pre),post_native=lower(post),fullcut_native=lower(fullcut),
                         physical_K_events=K.circuit,logical_A_events=A.circuit,
                         forward_entry=lower(entry),forward_exit=lower(exitop),
                         inverse_B_input=lower(AB),inverse_B_output=lower(BB)))
    out = dict(status='PASS_OPEN_C_NORMALIZATION_WITH_BOTH_FORWARD_CUTS_NATIVE_ZERO',no_new_kappa=True,
               compiler_sha256=sha,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               input_sha256=hashlib.sha256(buspath.read_bytes()).hexdigest(),rows=rows,
               construction='W_A={v:A(v,v) has zero X component}. Choose invertible G mapping W_T to W_S. Set Q=I+G^-T G^-1, pre=D_Q P_G. Both pre and F pre F^-1 are monomial. post=T pre^-1 S^-1 is monomial because pre sends T^-1 Z to S^-1 Z. All phases are retained in the literal operators.',
               limits=['The previous finite search attainers do not give a global lower bound on forward correction costs.',
                       'This supplies a new OPEN local forward normalizer; a full chronological caller and terminal completion remain open.',
                       'Inverse-B corrections are emitted and must be paid unless an actual revised backward construction removes them.',
                       'Columnwise tensor products of these exact operator-product identities preserve native monomiality, but scalar work, all-size controller, precision and physical tape remain separate obligations.'])
    (HERE/'COMMON-FRAME-NORMALIZER.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])
    for z in rows:
        print(z['p'],'forward',z['forward_entry']['rank'],z['forward_exit']['rank'],'inverse',z['inverse_B_input']['rank'],z['inverse_B_output']['rank'])


if __name__ == '__main__':
    main()
