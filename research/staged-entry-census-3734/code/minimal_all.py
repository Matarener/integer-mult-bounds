"""Minimal frame assignment of the whole word outside the prelude: each gate = join of its registers;
the last A gate of a target equals its cut level and that of a centre its centre frame (equalities
required by frame_bill). Pointwise minimal among assignments keeping the prelude, entrances and
terminals, so its failure proves infeasibility of that word."""
from timeline import *
from construct import basis, span_masks
from repair import repair

class Infeasible(Exception): pass

def minimal_all(x,mark):
    ids={id(g) for g in mark}
    npre=x['prelude_events']
    levels={C.V+int(t):C.span(U) for t,U in x['target_levels'].items()}
    cframe={q:C.span(U) for q,U in zip(x['centers'],x['center_frames'])}
    last={}
    for i,g in enumerate(x['A']):
        if g[0]=='warp': continue
        for r in C.touched(g):
            if (112<=r<224) or r in cframe: last[r]=i
    ports=x['ports']; removed=set(x['removed'])
    cur={}
    for r in range(704):
        if r in removed: continue
        cur[r]=C.span((ports[r],)) if r<112 else C.ZERO
    for q,U in x['start_extra'].items(): cur[int(q)]=C.span(U)
    for i,g in enumerate(x['A']):
        if g[0]=='warp':
            cur[g[1]]=C.span(g[4]); continue
        regs=C.touched(g)
        if i<npre and id(g) not in ids:
            F=C.span(g[-1])
        else:
            J=C.ZERO
            for r in regs: J=span_masks(J,cur[r]) if J!=C.ZERO else cur[r]
            forced=[levels.get(r,C.ZERO) if 112<=r<224 else cframe[r] for r in regs if last.get(r)==i]
            if forced:
                F=forced[0]
                if any(f!=F for f in forced) or (J & F)!=J:
                    raise Infeasible(('cut equality',i,regs))
            else:
                F=J
        fb=basis(F) if F!=C.ZERO else []
        if id(g) in ids and len(g)==5: g.append(fb)
        else: g[-1]=fb
        for r in regs: cur[r]=F
    return repair(x,[g for g in mark if not any(g is h for h in x['A'])],minimal_B=True,cleanup=False)
