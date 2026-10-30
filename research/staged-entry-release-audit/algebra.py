"""Exact source-word algebra; no predecessor Python code is executed.

Tekalign (tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
Words list operators in application order; only adjacent inverse pairs cancel.
"""
from fractions import Fraction as Q
from difflib import SequenceMatcher
from collections import Counter

HELPERS=(600,608,609)
N=704

def need(ok,why):
    if not ok: raise ValueError(why)

def scalar(g):
    if g[0]=='add': return ('a',g[1],g[2],Q(g[3],g[4]))
    if g[0]=='scale': return ('s',g[1],Q(g[2],g[3]))
    if g[0]=='warp': return ('u',g[1],g[2])
    raise ValueError('unknown gate '+repr(g))

def body(w):
    out=[]
    for k in range(len(w['B'])+1):
        out.extend(('u',r[1],j+1) for j,r in enumerate(w['warps']) if r[0]==k)
        if k<len(w['B']):out.append(scalar(w['B'][k]))
    return clean(out)

def clean(xs):return [x for x in xs if not(x[0]=='s' and x[2]==1)]
def section(w,s):return clean([scalar(g) for g in w[s]])

def prefix(w,B):
    xs=[('c',c['target'],c['source'],Q(c['coefficient']),tuple(reversed(c['operator_word']))) for c in w['initial_corrections']]
    for s in ('precondition','compensation','A','cut'):xs+=section(w,s)
    return xs+B+section(w,'restore')

def inverse_tail(w,B):
    xs=clean([scalar(g) for g in w['A'][w['prelude_events']:]])+B+section(w,'restore')
    private=set(map(int,w['helper_final']))
    def reg(r):return r+N if r in private else r
    out=[]
    for x in xs[::-1]:
        if 112<=x[1]<224:continue
        if x[0]=='a':out.append(('a',reg(x[1]),reg(x[2]),-x[3]))
        elif x[0]=='s':out.append(('s',reg(x[1]),1/x[2]))
        else:out.append(('u',reg(x[1]),-x[2]))
    return out

def plans(o,n):
    for s in ('A','restore','cut','precondition','compensation'):
        need(section(o,s)==section(n,s),'changed operator section '+s)
    need(o['initial_corrections']==n['initial_corrections'],'changed initial corrections')
    need([x[1:] for x in o['warps']]==[x[1:] for x in n['warps']],'changed native interface')
    need(o['removed']==n['removed'] and o['helper_final']==n['helper_final'],'changed domain')
    a,b=body(o),body(n);edits=SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes()
    deleted=[];inserted=[]
    for tag,i,j,k,l in edits:
        if tag!='equal':deleted+=a[i:j];inserted+=b[k:l]
    need(len(deleted)==12 and len(inserted)==6,'edit count')
    need(all(x[0]=='a' and x[2] in HELPERS and abs(x[3])==Q(1,4) for x in deleted),'deleted read contract')
    need(Counter(x[2] for x in deleted)==Counter({h:4 for h in HELPERS}),'deleted helper inventory')
    need(all(x[0]=='a' and x[2] in HELPERS for x in inserted),'release contract')
    need(Counter(x[2] for x in inserted)==Counter({h:2 for h in HELPERS}),'release helper inventory')
    variants={}
    for mask in range(8):
        selected={h for j,h in enumerate(HELPERS) if mask>>j&1};out=[]
        for tag,i,j,k,l in edits:
            if tag=='equal':out+=a[i:j]
            else:
                out += [x for x in a[i:j] if x[2] not in selected]
                out += [x for x in b[k:l] if x[2] in selected]
        variants[mask]=out
    need(variants[0]==a and variants[7]==b,'subset endpoints')
    return variants,deleted,inserted

def reduce_word(word,ops):
    out=list(word)
    for k in ops:
        if out and out[-1]==-k:out.pop()
        else:out.append(k)
    return tuple(out)

def plus(dst,src,q=Q(1),ops=()):
    # Build a fresh sum, so even adversarial aliases cannot corrupt iteration.
    out=dict(dst)
    for (word,var),c in src.items():
        key=(reduce_word(word,ops),var);v=out.get(key,Q(0))+q*c
        if v:out[key]=v
        else:out.pop(key,None)
    return out

def run(w,B,include_tail=True):
    regs=sorted(set(range(N))-set(w['removed']))+sorted(int(x)+N for x in w['helper_final'])
    rows={r:{((),r):Q(1)} for r in regs}
    def execute(seq):
        for x in seq:
            kind,t=x[:2];need(t in rows,'gate targets missing register')
            if kind in ('a','c'):
                s,q=x[2:4];need(s in rows and s!=t and q,'invalid addition')
                rows[t]=plus(rows[t],rows[s],q, x[4] if kind=='c' else ())
            elif kind=='s':
                need(x[2]!=0,'zero scale');rows[t]={k:c*x[2] for k,c in rows[t].items()}
            else:
                need(kind=='u' and x[2]!=0,'unknown native');rows[t]=plus({},rows[t],ops=(x[2],))
    execute(prefix(w,B));boundary={r:dict(v) for r,v in rows.items()}
    if include_tail:execute(inverse_tail(w,B))
    return boundary,rows

def endpoint(rows):
    for r,row in rows.items():
        expected={((),r):Q(1)}
        if 112<=r<224:expected[(),r-112]=Q(1)
        need(row==expected,'endpoint discrepancy at '+str(r))

def difference(a,b):return {r:x for r in a if (x:=plus(a[r],b[r],Q(-1)))}
def serial(rows):
    return [[r,[[list(word),v,str(q)] for (word,v),q in sorted(row.items())]] for r,row in sorted(rows.items())]
