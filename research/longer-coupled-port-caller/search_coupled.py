"""Solve chronology constraints for a coupled star frame.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Discovery only. A solver result is not a native endpoint.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
import z3
import search_star as S

# A polynomial is a set of square-free Boolean monomials. An integer gives
# the variable set of one monomial. Zero denotes its constant term.
def prod(a,b):
    out=set()
    for x in a:
        for y in b:
            z=x|y
            if z in out: out.remove(z)
            else: out.add(z)
    return frozenset(out)

ZERO=frozenset();ONE=frozenset((0,))

def madd(a,b): return [[x^y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def mmul(a,b):
    n=len(a);out=[[ZERO for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if not a[i][k]: continue
            for j in range(n):
                if b[k][j]:out[i][j]=out[i][j]^prod(a[i][k],b[k][j])
    return out

def mcomm(a,b):return madd(mmul(a,b),mmul(b,a))

def constant(rows):return [[ONE if row>>j&1 else ZERO for j in range(len(rows))] for row in rows]


def model(q,g):
    d=2*q;n=d*(g+1);nextvar=0;As=[];Bs=[];vars=[]
    for c in range(g):
        local=[]
        for label in ('a','b'):
            mat=[]
            for i in range(d):
                row=[]
                for j in range(d):
                    row.append(frozenset((1<<nextvar,)))
                    vars.append(z3.Bool(f'{label}{c}_{i}_{j}'));nextvar+=1
                mat.append(row)
            local.append(mat)
        As.append(local[0]);Bs.append(local[1])
    gates=[]
    for c,(a,b) in enumerate(zip(As,Bs)):
        p=[[ZERO for _ in range(n)] for _ in range(n)]
        r=[[ZERO for _ in range(n)] for _ in range(n)]
        e=[[ZERO for _ in range(n)] for _ in range(n)]
        off=d*(c+1)
        for i in range(d):
            e[i][i]=ONE;e[off+i][off+i]=ONE
            for j in range(d):
                p[i][j]=p[off+i][off+j]=a[i][j]^b[i][j]
                p[i][off+j]=p[off+i][j]=b[i][j]
                r[i][j]=r[i][off+j]=r[off+i][j]=r[off+i][off+j]=a[i][j]
        group=tuple(sum(1<<j for j in (i%d,off+i%d)) if i<d or off<=i<off+d else 0 for i in range(n))
        gates.append(((p,r),(madd(e,p),madd(constant(group),r))))
    bad=[]
    for half in range(2):
        p=(0,)*n;ra=(0,)*n;rb=(0,)*n
        for k in range(half*q,(half+1)*q):
            c=1<<k;w=sum(1<<(d*(j+1)+k) for j in range(g))
            p=S.add(p,S.add(S.outer(c,c,n),S.outer(w,w,n)))
            ra=S.add(ra,S.outer(c,w,n));rb=S.add(rb,S.outer(w,c,n))
        bad.extend(((constant(p),constant(ra)),(constant(p),constant(rb))))
    mono_cache={0:z3.BoolVal(True)}
    def expr(poly):
        terms=[]
        for m in poly:
            if m not in mono_cache:
                indices=[];x=m
                while x:
                    bit=x&-x;indices.append(vars[bit.bit_length()-1]);x^=bit
                mono_cache[m]=z3.And(indices)
            terms.append(mono_cache[m])
        if not terms:return z3.BoolVal(False)
        out=terms[0]
        for term in terms[1:]:out=z3.Xor(out,term)
        return out
    base=[]
    for a,b in zip(As,Bs):
        for matrix in (madd(mmul(a,a),a),madd(mcomm(a,b),b)):
            base.extend(z3.Not(expr(p)) for row in matrix for p in row if p)
        # For q=2, enumerate all 560 rank-two projectors on four coordinates.
        if q==2:
            projectors=sorted(set(p for p,_ in S.old.FULL))
            bits=[expr(x) for row in a for x in row]
            base.append(z3.Or([z3.And([bit if rows[i]>>j&1 else z3.Not(bit) for i in range(d) for j,bit in enumerate(bits[i*d:(i+1)*d])]) for rows in projectors]))
        else:raise ValueError('Use q=2 for this discovery entry point.')
    return n,gates,bad,vars,base,expr


def solve(q,g,order,timeout):
    n,gates,bad,variables,base,expr=model(q,g)
    defects=[[[ZERO for _ in range(n)] for _ in range(n)] for _ in range(g+2)]
    tail=[[ZERO for _ in range(n)] for _ in range(n)]
    for c,k in reversed(order):
        p,r=gates[c][k] if c<g else bad[2*(c-g)+k]
        defects[c]=madd(defects[c],mcomm(p,tail));tail=madd(tail,r)
    polys=set(p for mat in defects for row in mat for p in row if p)
    solver=z3.Solver();solver.set(timeout=timeout);solver.add(base)
    solver.add([z3.Not(expr(p)) for p in polys])
    started=time.monotonic();status=solver.check()
    record={'q':q,'g':g,'fields':n,'calls':2*g+4,'order':order,'status':str(status),'seconds':round(time.monotonic()-started,3),'nonzero_equations':len(polys)}
    if status==z3.sat:
        m=solver.model();record['bits']=[int(z3.is_true(m.eval(v,model_completion=True))) for v in variables]
    if status==z3.unknown:record['reason']=solver.reason_unknown()
    return record


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=144);ap.add_argument('--timeout-ms',type=int,default=10000);args=ap.parse_args()
    records=[];g=3
    for second in itertools.permutations(range(g)):
        for connectors in itertools.permutations(((3,0),(3,1),(4,0),(4,1))):
            order=[(j,0) for j in range(g)]+list(connectors)+[(j,1) for j in second]
            record=solve(2,g,order,args.timeout_ms);records.append(record);print(json.dumps(record),flush=True)
            if len(records)>=args.limit:break
        if len(records)>=args.limit:break
    Path(__file__).with_name('COUPLED-SEARCH.json').write_text(json.dumps({'z3':z3.get_version_string(),'records':records},indent=2)+'\n')

if __name__=='__main__':main()
