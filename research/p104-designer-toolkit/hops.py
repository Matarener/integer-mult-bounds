"""tk hops MATRIX [--signed] [--program FILE] [--points vu.pkl] [--json] [--recomb]
Verify a delivery program against a delivery matrix and report hop / role / restore counts.
MATRIX    .npy / .json / whitespace text, rows = outputs, columns = leaves; entries 0/+-1 (SIGNHOP/Smodel.npy = 2*coef) -- zeros define the support.
program   one node per line, the format of HOPILP (unsigned) / SIGNHOP srecomb (signed):
            unsigned  `hi lo a`          S = (hi<<64)|lo leaf bitmask, a = affine functional (1..255) splitting S into S&mk[a] and S&~mk[a]
            signed    `hi lo keyhex a`   same + sign pattern of the consumer on S, bytes 02 = +1 / 00 = -1, normalised first = +
          default programs: unsigned HOPILP/rc1.txt (916), signed SIGNHOP/S.out (2797).  --points = leaf points (default DESIGNER/IDEAL/vu.pkl, key V).
Legality (cancellation-free): every node is a disjoint union of two children; a child is a leaf or another program node with the induced sign pattern;
every matrix row (support + normalised signs) is a node.  --signed distinguishes nodes by (set, sign pattern); unsigned merges patterns.
Counts: hops = non-leaf nodes; roles = hops - outputs (credited registers for non-output signals; the 400 cap of the P104 role budget is shown);
restores = 4*hops (SIGNHOP model constant: restore adds per node).  Reference: unsigned 590 <= H <= 916 (HOPILP), signed 2521 (pool bound) <= H <= 2704 (SIGNHOP)."""
import os,sys,json,pickle,subprocess
from tkcommon import *
D=(HERE+'/data/') if PACKAGE else W+'/cards/WILD/DESIGNER/'
UNS_DEFAULT=D+('rc1.txt' if PACKAGE else 'HOPILP/rc1.txt'); SGN_DEFAULT=D+('S.txt' if PACKAGE else 'SIGNHOP/S.out')
class Mat:
    """minimal 2-D matrix (stdlib): .shape and m[i,j]"""
    def __init__(s,rows): s.rows=rows; s.shape=(len(rows),len(rows[0]) if rows else 0)
    def __getitem__(s,k): return s.rows[k[0]][k[1]]
def load_matrix(p):
    if p.endswith('.npy'):
        import numpy as np; return np.load(p)
    if p.endswith('.json'): return Mat(json.load(open(p)))
    return Mat([[int(float(x)) for x in l.split()] for l in open(p) if l.split()])
def parse_prog(fn,signed):
    nodes=[]
    for l in open(fn):
        t=l.split()
        if not t: continue
        S=(int(t[0])<<64)|int(t[1])
        if signed and len(t)>=4: nodes.append((S,bytes.fromhex(t[2]),int(t[3])))
        else: nodes.append((S,None,int(t[-1])))
    return nodes
def analyse(Sm,nodes,P,signed):
    n=Sm.shape[0]; ncol=Sm.shape[1]
    par=lambda x: bin(x).count('1')&1
    mk=[sum(1<<i for i in range(ncol) if par(P[i]&a)) for a in range(256)]
    def leaves(S): return [i for i in range(ncol) if S>>i&1]
    def norm(vals):
        f=vals[0]; return bytes((v*f+1) for v in vals)         # +1->2, -1->0, normalised first=+1
    def ukey(S,k): return k if signed else None
    prog={}
    for S,k,a in nodes: prog[(S,ukey(S,k))]=a
    errors=[]; outs=[]
    for s in range(n):
        S=sum(1<<i for i in range(ncol) if Sm[s,i]!=0)
        if S==0: continue
        k=norm([int(Sm[s,i]) for i in leaves(S)]) if signed else None
        outs.append((S,k))
        if (S,k) not in prog: errors.append(('output row %d missing'%s,))
    # per-node checks and reachability
    reach=set(); st=list(outs)
    while st:
        nd=st.pop()
        if nd in reach: continue
        reach.add(nd)
        if nd not in prog: continue
        S,k=nd; a=prog[nd]; b=S&mk[a]; c=S&~b
        if not b or not c: errors.append(('node not split by functional %d'%a,hex(S))); continue
        lv=leaves(S)
        for ch in (b,c):
            if bin(ch).count('1')<2: continue
            ck=None
            if signed:
                vals=[(1 if k[j]==2 else -1) for j,i in enumerate(lv) if ch>>i&1]; ck=norm(vals)
            if (ch,ck) not in prog: errors.append(('missing child',hex(ch)))
            else: st.append((ch,ck))
    nout=len(outs); hops=len(reach & set(prog)) if not errors else len(prog)
    return dict(legal=not errors,errors=errors[:10],nerrors=len(errors),outputs=nout,program_nodes=len(prog),hops=hops,dead_nodes=len(prog)-len(reach&set(prog)),
                distinct_sets=len({S for S,_ in prog}),roles=hops-nout,restores=4*hops,role_cap=400,roles_over_cap=hops-nout-400)
def main(a):
    Sm=load_matrix(a.matrix)
    if a.recomb:
        if PACKAGE: raise SystemExit('tk hops --recomb: workspace-only (needs SIGNHOP/srecomb.py and CP-SAT)')
        if os.path.abspath(a.matrix)!=D+'SIGNHOP/Smodel.npy': raise SystemExit('tk hops --recomb: only SIGNHOP/Smodel.npy is wired into srecomb.py')
        out=HERE+'/out/recomb_%s.out'%('signed' if a.signed else 'unsigned'); os.makedirs(HERE+'/out',exist_ok=True)
        env_prefix=[] if a.signed else ['env','UNSIGNED=1']
        submit('tk_recomb_'+('s' if a.signed else 'u'),3600,env_prefix+[PY,'-B',D+'SIGNHOP/srecomb.py',out]+[D+'HOPILP/'+f for f in('rc1.txt','sa1.txt','sa2.txt','sa3.txt')],False,threads=4)
        print('output will be',out); return
    pts=a.points or (D+'vu.json' if PACKAGE else D+'IDEAL/vu.pkl')
    os.chdir(D+'IDEAL') if False else None
    P=list(json.load(open(pts))['V']) if pts.endswith('.json') else list(pickle.load(open(pts,'rb'))['V'])
    prog=a.program or (SGN_DEFAULT if a.signed else UNS_DEFAULT)
    r=analyse(Sm,parse_prog(prog,a.signed),P,a.signed); r['program']=prog; r['signed']=a.signed
    if a.json: print(json.dumps(r,indent=1,default=str)); return 0 if r['legal'] else 1
    print('%s program %s: %s'%('signed' if a.signed else 'unsigned',os.path.basename(prog),'LEGAL' if r['legal'] else 'ILLEGAL %s'%r['errors'][:3]))
    print('outputs %d  nodes in file %d (dead %d)  distinct leaf sets %d'%(r['outputs'],r['program_nodes'],r['dead_nodes'],r['distinct_sets']))
    print('HOPS %d   ROLES %d (cap %d, over by %d)   RESTORES %d'%(r['hops'],r['roles'],r['role_cap'],r['roles_over_cap'],r['restores']))
    print('reference: unsigned 590..916, signed 2521..2704 (best known 2704 is a fixed DAG, not a file)')
    return 0 if r['legal'] else 1
