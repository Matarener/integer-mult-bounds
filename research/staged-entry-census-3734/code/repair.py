"""Frame repair: each gate gets span(its frame, current frames of its registers); with minimal_B,
B/restore gates get exactly the join (pointwise minimal assignment of B given A). Marked releases get
the minimal join. Warps follow: U = current lender frame, E = image. Equalities (target levels,
centres) and terminals are left to frame_bill."""
from timeline import *
from construct import basis, span_masks

def repair(x,mark,minimal_B=False,cleanup=True):
    ids={id(g) for g in mark}
    ports=x['ports']; removed=set(x['removed'])
    cur={}
    for r in range(704):
        if r in removed: continue
        cur[r]=C.span((ports[r],)) if r<112 else C.ZERO
    for q,U in x['start_extra'].items(): cur[int(q)]=C.span(U)
    changed=0
    inB=[False]
    def gate(g):
        nonlocal changed
        regs=C.touched(g)
        J=0
        for r in regs: J=span_masks(J,cur[r]) if J else cur[r]
        if id(g) in ids:
            F=J if J else C.ZERO
            g.append(basis(F) if F!=C.ZERO else [])
        elif minimal_B and inB[0]:
            F=J if J else C.ZERO
            if F!=C.span(g[-1]): changed+=1
            g[-1]=basis(F) if F!=C.ZERO else []
        else:
            F=C.span(g[-1])
            if (F & J)!=J:
                F=span_masks(F,J); g[-1]=basis(F); changed+=1
        for r in regs: cur[r]=F
    def warp(lender,cols,U,E):
        nonlocal changed
        if cur[lender]!=C.span(U):
            im=C.warp_images(cols); U2=cur[lender]; E2=C.image_mask(im,U2)
            changed+=1
            cur[lender]=E2; return basis(U2),basis(E2)
        cur[lender]=C.span(E); return U,E
    for i,g in enumerate(x['A']):
        if g[0]=='warp':
            _,r,op,fr,to=g
            cols=x['warps'][abs(op)-1][2]
            im=C.warp_images(cols)
            if op<0:
                inv=[0]*512
                for a,b in enumerate(im): inv[b]=a
                im=inv
            if cur[r]!=C.span(fr):
                U2=cur[r]; E2=C.image_mask(im,U2); g[3]=basis(U2); g[4]=basis(E2); changed+=1
            cur[r]=C.span(g[4]); continue
        gate(g)
    levels={C.V+int(t):C.span(U) for t,U in x['target_levels'].items()}
    for q,U in zip(x['centers'],x['center_frames']):
        served={levels.get(gg[1],C.ZERO) for gg in x['cut'] if gg[2]==q}
        T=C.span(U)
        for S in sorted(served,key=lambda m:-C.dim(m)): T=S
        cur[q]=T
    at={}
    inB[0]=True
    for k,rec in enumerate(x['warps'],1): at.setdefault(rec[0],[]).append(k)
    for p in range(len(x['B'])+1):
        for k in at.get(p,()):
            rec=x['warps'][k-1]
            U,E=warp(rec[1],rec[2],rec[3],rec[4]); rec[3]=U; rec[4]=E
        if p<len(x['B']): gate(x['B'][p])
    for g in x['restore']: gate(g)
    if cleanup: x['cleanup']=C.derive_cleanup(x)
    return x,changed
