"""Local optimisation of B and restore frames (A, entrances, terminals and native warp maps fixed).

Each B/restore gate g carries F_g. For each of its registers F_g must contain the current frame
(after warps, image by G) and lie inside the next constraint (next gate pulled back through warps
by G^-1, or the terminal). Warps keep dimensions, so a register's bill depends only on the
dimensions of its successive gates. Coordinate descent: replace F_g by a subspace between L (join)
and U (meet) lowering sum n_r r^(1-a); iterate to a fixed point. Not an exact solver.
"""
import itertools
from timeline import *
from construct import basis, span_masks
A_EXP=0.00173
def cost(d): return 0.0 if d<=0 else d**(1-A_EXP)
def meet(a,b): return a & b
def inv_images(cols):
    im=C.warp_images(cols); inv=[0]*512
    for x,y in enumerate(im): inv[y]=x
    return im,inv
def img(table,mask): return sum(1<<table[x] for x in C.points(mask))

class Frames:
    def __init__(s,x):
        s.x=x
        # state at the start of B (A and centre descents as in frame_bill)
        ports=x['ports']; removed=set(x['removed']); s.live=[r for r in range(704) if r not in removed]
        cur={}
        for r in s.live: cur[r]=C.span((ports[r],)) if r<112 else C.ZERO
        for q,U in x['start_extra'].items(): cur[int(q)]=C.span(U)
        for g in x['A']:
            if g[0]=='warp': cur[g[1]]=C.span(g[4]); continue
            for r in C.touched(g): cur[r]=C.span(g[-1])
        levels={C.V+int(t):C.span(U) for t,U in x['target_levels'].items()}
        for q,U in zip(x['centers'],x['center_frames']):
            served={levels.get(gg[1],C.ZERO) for gg in x['cut'] if gg[2]==q}
            T=C.span(U)
            for S in sorted(served,key=lambda m:-C.dim(m)): T=S
            cur[q]=T
        s.start=cur
        _,_,_,_,end=C.frame_bill(x)
        s.end=end
        # nodes: B gates then restore; native warps
        s.gates=[]                       # (liste, indice)
        s.F=[]
        s.chain={r:[] for r in s.live}   # sequence of ('g',i) or ('w',k)
        at={}
        for k,rec in enumerate(x['warps'],1): at.setdefault(rec[0],[]).append(k)
        s.wtab={}
        for p in range(len(x['B'])+1):
            for k in at.get(p,()):
                rec=x['warps'][k-1]; s.chain[rec[1]].append(('w',k))
                if k not in s.wtab: s.wtab[k]=inv_images(rec[2])
            if p<len(x['B']):
                i=len(s.gates); s.gates.append(('B',p)); s.F.append(C.span(x['B'][p][-1]))
                for r in C.touched(x['B'][p]): s.chain[r].append(('g',i))
        for j,g in enumerate(x['restore']):
            i=len(s.gates); s.gates.append(('restore',j)); s.F.append(C.span(g[-1]))
            for r in C.touched(g): s.chain[r].append(('g',i))
        s.pos={}
        for r,ch in s.chain.items():
            for t,(kind,i) in enumerate(ch):
                if kind=='g': s.pos[(r,i)]=t
        s.regs=[C.touched(s.gate(i)) for i in range(len(s.gates))]
    def gate(s,i):
        sec,j=s.gates[i]; return s.x[sec][j]
    def before(s,r,i):
        """frame of r just before gate i (warps applied)"""
        ch=s.chain[r]; t=s.pos[(r,i)]
        f=s.start[r]; u=t-1; ws=[]
        while u>=0 and ch[u][0]=='w': ws.append(ch[u][1]); u-=1
        if u>=0: f=s.F[ch[u][1]]
        for k in reversed(ws): f=img(s.wtab[k][0],f)
        return f
    def after(s,r,i):
        """upper constraint on F_i from r: next gate pulled back through warps, or terminal"""
        ch=s.chain[r]; t=s.pos[(r,i)]; u=t+1; ws=[]
        while u<len(ch) and ch[u][0]=='w': ws.append(ch[u][1]); u+=1
        f=s.F[ch[u][1]] if u<len(ch) else s.end[r]
        for k in reversed(ws): f=img(s.wtab[k][1],f)
        return f
    def nextdim(s,r,i):
        ch=s.chain[r]; t=s.pos[(r,i)]; u=t+1
        while u<len(ch) and ch[u][0]=='w': u+=1
        return C.dim(s.F[ch[u][1]]) if u<len(ch) else C.dim(s.end[r])
    def prevdim(s,r,i):
        return C.dim(s.before(r,i))
    def local_cost(s,i,Fd):
        tot=0.0
        for r in s.regs[i]:
            tot+=cost(Fd-s.prevdim(r,i))+cost(s.nextdim(r,i)-Fd)
        return tot
    def options(s,L,U,limit=4):
        if (L & U)!=L: return []
        bl=set(C.points(L)); comp=[]
        cur=L
        for b in basis(U):
            if not cur>>b & 1:
                comp.append(b); cur=span_masks(cur,C.span((b,)))
        out=[L,U]
        if len(comp)<=limit:
            for k in range(1,len(comp)):
                for sub in itertools.combinations(comp,k):
                    m=L
                    for b in sub: m=span_masks(m,C.span((b,)))
                    out.append(m)
        return out
    def optimize(s,rounds=20):
        gain_total=0.0
        for rd in range(rounds):
            improved=0
            for i in range(len(s.gates)):
                L=0; U=C.FULL
                for r in s.regs[i]:
                    b=s.before(r,i); L=span_masks(L,b) if L else b
                    U=meet(U,s.after(r,i))
                if L==0: L=C.ZERO
                old=s.F[i]; oc=s.local_cost(i,C.dim(old))
                best=(oc,old)
                for m in s.options(L,U):
                    c=s.local_cost(i,C.dim(m))
                    if c<best[0]-1e-12: best=(c,m)
                if best[1]!=old:
                    # downstream warp feasibility is rechecked by frame_bill
                    s.F[i]=best[1]; improved+=1; gain_total+=oc-best[0]
            if not improved: break
        return gain_total
    def write(s):
        for i,(sec,j) in enumerate(s.gates):
            s.x[sec][j][-1]=basis(s.F[i]) if s.F[i]!=C.ZERO else []
        # warps: U = current frame, E = image
        cur=dict(s.start)
        at={}
        for k,rec in enumerate(s.x['warps'],1): at.setdefault(rec[0],[]).append(k)
        for p in range(len(s.x['B'])+1):
            for k in at.get(p,()):
                rec=s.x['warps'][k-1]; U=cur[rec[1]]; E=img(s.wtab[k][0],U)
                rec[3]=basis(U); rec[4]=basis(E); cur[rec[1]]=E
            if p<len(s.x['B']):
                for r in C.touched(s.x['B'][p]): cur[r]=C.span(s.x['B'][p][-1])
        return s.x
def total(b): return sum(n*r**(1-A_EXP) for r,n in b.items())
if __name__=='__main__':
    import copy,sys
    for tag in ('base',):
        w=load(tag); b0,w0,*_=C.frame_bill(w)
        fr=Frames(copy.deepcopy(w)); g=fr.optimize(); x=fr.write()
        b1,w1,*_=C.frame_bill(x)
        print(tag,'estimated local gain',round(g,4),'bill before',b0,'after',b1,'d_cost',round(total(b1)-total(b0),4))
