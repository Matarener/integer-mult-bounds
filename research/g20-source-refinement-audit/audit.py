"""Audit the fixed G20 source windows without importing predecessor engines."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import gzip,hashlib,json,sys
P=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:
        raise ValueError(message)


def read(name):
    raw=(P/name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def table(name,width):
    rows=[]
    for line in (P/name).read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells=[v.strip() for v in line.split("|")[1:-1]]
        if len(cells)==width and all(v.isdigit() for v in cells):
            rows.append(list(map(int,cells)))
    return rows


def references(program,field,lo,hi):
    return [i for i in range(lo,hi+1) if program[i][1]==field or
            (program[i][0] in ("ADD","COPY","TICKET_CLEAR") and program[i][2]==field)]


def source_windows(fwd):
    upper=table("inputs/bit.md",11)
    refined=table("inputs/bit-refinement.md",12)
    recipients={v[0]:v[1:] for v in table("inputs/bit-refinement.md",5)}
    need(len(upper)==6 and len(refined)==8 and len(recipients)==8,"complete proposal tables")
    result=[]
    for row in upper:
        h,r,x,l,u,cold,proper,rq,sq1,sq2,hq3=row
        first=[i for i,e in enumerate(fwd) if e==["Q",h,0,l,1]]
        need(len(first)==1,"unique helper entrance")
        q1=first[0];inj=q1+1
        checks={cold:["ADD",r,h,0],proper:["ADD",r,h,l],rq:["Q",r,0,l,1],
                q1:["Q",h,0,l,1],inj:["ADD",h,x,l],hq3:["Q",h,l,u,3]}
        for i,e in checks.items():need(fwd[i]==e,"upper literal event")
        need(fwd[sq1][:3]==["Q",x,l] and fwd[sq1][4]==1,"SOURCE first query")
        mid=fwd[sq1][3]
        need(fwd[sq2]==["Q",x,mid,u,2],"SOURCE second query")
        need(references(fwd,h,q1,hq3)==sorted([q1,inj,proper,hq3]),"complete helper observations")
        need(references(fwd,r,cold,proper)==[cold,rq,proper],"complete recipient observations")
        for i in range(inj+1,sq2):
            if fwd[i][1]==x:need(i==sq1,"unchanged SOURCE version")
        result.append(dict(kind="upper",h=h,r=r,x=x,l=l,p=mid,u=u,cold=cold,proper=proper,
                           rq=rq,sq1=sq1,sq2=sq2,hqs=[q1,hq3],inj=inj))
    for h,r,x,l,mid,u,cold,proper,q1,q2,q3,sq in refined:
        inj=q1+1
        checks={cold:["ADD",r,h,0],proper:["ADD",r,h,mid],q1:["Q",h,0,l,1],
                inj:["ADD",h,x,l],q2:["Q",h,l,mid,1],q3:["Q",h,mid,u,2],sq:["Q",x,l,u,3]}
        for i,e in checks.items():need(fwd[i]==e,"refined literal event")
        ra,ri,rb,rx=recipients[r]
        need(fwd[ra][0:3]==["Q",r,0] and fwd[ra][4]==1,"recipient first query")
        rl=fwd[ra][3]
        need(fwd[ri]==["ADD",r,rx,rl] and fwd[rb]==["Q",r,rl,mid,1],"independent recipient injection")
        need(references(fwd,r,cold,proper)==[cold,ra,ri,rb,proper],"complete injected-recipient interval")
        need(references(fwd,h,q1,q3)==[q1,inj,q2,proper,q3],"complete refined helper interval")
        need(all(fwd[i][1]!=x for i in range(inj+1,sq)),"refined SOURCE version")
        result.append(dict(kind="refined",h=h,r=r,x=x,l=l,p=mid,u=u,cold=cold,proper=proper,
                           hqs=[q1,q2,q3],inj=inj,sq=sq,independent_source=rx))
    need(len({v['h'] for v in result})==14 and len({v['r'] for v in result})==14,"distinct helpers and recipients")
    for i,e in {3156:["Q",444,0,79,1],3157:["ADD",444,77,79],6372:["Q",444,79,509,3],7570:["Q",77,186,509,2]}.items():
        need(fwd[i]==e,"retained helper444 source")
    need(references(fwd,444,3156,6372)==[3156,3157,6372],"retained direct interval")
    return result


def inverse_event(e):
    if e[0]=="Q":return ["Q",e[1],e[3],e[2],e[4]]
    need(e[0]=="ADD","supported anchored source event")
    return e


def construct(base,fwd,windows):
    old=base['records'];where={}
    for i,e in enumerate(old):where.setdefault(tuple(e),[]).append(i)
    changed={};bank=len(base['start']);new_queries=[];anchors=[]
    def index(i):
        event=inverse_event(fwd[i]);hits=where.get(tuple(event),[])
        need(len(hits)==1,"unique exact inverse anchor "+str(i))
        return hits[0]
    def replace(i,events):
        j=index(i);need(j not in changed,"disjoint old event edits")
        changed[j]=events;anchors.append(dict(forward=i,baseline=j,before=old[j],after=events))
    def q(d,a,b,k):
        new_queries.append((a,b,k));return ["Q",d,a,b,k]
    for w in windows:
        h,r,x,l,mid,u=(w[k] for k in ['h','r','x','l','p','u'])
        upper=bank;bank+=1
        capture=[["ERASE",upper,u],["ADD",upper,x,u]]
        if w['kind']=="upper":
            replace(w['sq2'],capture+[inverse_event(fwd[w['sq2']])])
            replace(w['hqs'][-1],[["ADD",h,upper,u],q(h,u,0,4),["ERASE",upper,None]])
            if w['sq1']<w['proper']:
                replace(w['proper'],[]);replace(w['rq'],[])
                replace(w['sq1'],[inverse_event(fwd[w['sq1']]),["ADD",r,x,l],q(r,l,0,1)])
            else:
                replace(w['proper'],[["ADD",r,x,l]])
        else:
            plane=bank;bank+=1
            replace(w['sq'],capture+[q(x,u,mid,2),["ERASE",plane,mid],["ADD",plane,x,mid],q(x,mid,l,1)])
            replace(w['hqs'][-1],[["ADD",h,upper,u],q(h,u,0,4),["ERASE",upper,None]])
            replace(w['proper'],[["ADD",r,plane,mid],["ERASE",plane,None]])
        replace(w['cold'],[])
        replace(w['inj'],[])
        for i in w['hqs'][:-1]:replace(i,[])
    program=[]
    for i,e in enumerate(old):program.extend(changed.get(i,[e]))
    extra=bank-len(base['start'])
    word=dict(records=program,owned=base['owned']+list(range(len(base['start']),bank)),
              start=base['start']+[None]*extra,final=base['final']+[None]*extra)
    return word,anchors,sorted(set(new_queries))


def matmul(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def inverse(a):
    n=len(a);v=[list(map(F,row))+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next((k for k in range(j,n) if v[k][j]),None);need(k is not None,"nonsingular Gram matrix")
        v[j],v[k]=v[k],v[j];q=v[j][j];v[j]=[z/q for z in v[j]]
        for k in range(n):
            if k!=j:
                q=v[k][j];v[k]=[x-q*y for x,y in zip(v[k],v[j])]
    return [r[n:] for r in v]


def projectors(frames,ids):
    result={}
    for idx in ids:
        frame=frames[str(idx)];b=[list(map(F,r)) for r in frame['B']]
        a=[list(map(F,r)) for r in frame['A']]
        need(len(b)==frame['dim'] and len(a)+len(b)==8,"frame dimensions")
        need(all(sum(x*y for x,y in zip(r,s))==0 for r in a for s in b),"actual frame orthogonality")
        if not b:p=[[F(0)]*8 for _ in range(8)]
        else:
            bt=list(map(list,zip(*b)));p=matmul(matmul(bt,inverse(matmul(b,bt))),b)
        need(matmul(p,p)==p and sum(p[i][i] for i in range(8))==frame['dim'],"exact projector")
        result[idx]=p
    return result


def physical_pairs(frames,queries):
    ps=projectors(frames,{v for a,b,_ in queries for v in (a,b)})
    checked=[]
    for a,b,k in queries:
        lo,hi=sorted([a,b],key=lambda v:frames[str(v)]['dim'])
        l,h=ps[lo],ps[hi]
        need(frames[str(hi)]['dim']-frames[str(lo)]['dim']==k,"new actual query rank")
        need(matmul(l,h)==l and matmul(h,l)==l,"exact nested physical subspaces")
        d=[[y-x for x,y in zip(rr,ss)] for rr,ss in zip(l,h)]
        need(matmul(d,d)==d and sum(d[i][i] for i in range(8))==k,"residual projector rank")
        # The address action uses (x,y)->(x-D(x-y),y+D(x-y)).
        # Reflection composition has projector L+H-2LH=H-L.
        lh=matmul(l,h)
        need([[l[i][j]+h[i][j]-2*lh[i][j] for j in range(8)] for i in range(8)]==d,"all-address transport composition")
        checked.append([a,b,k])
    return checked


def matcher_506(frames):
    frame=frames['506']
    # Columns are the given subspace basis, then its orthogonal complement.
    columns=[list(map(F,r)) for r in frame['B']+frame['A']]
    w=list(map(list,zip(*columns)));wi=inverse(w)
    eye=[[F(i==j) for j in range(8)] for i in range(8)]
    need(matmul(w,wi)==eye and matmul(wi,w)==eye,'both ordinary matcher directions')
    d=[[F(i==j and i<4) for j in range(8)] for i in range(8)]
    p=projectors(frames,{506})[506]
    need(matmul(matmul(w,d),wi)==p,'actual new residual matcher')
    a=frame['A'];b=frame['B']
    need(len(a)==len(b)==4,'rank-four complement orientation')
    bad=[row[:] for row in w];bad[0][0]+=1
    need(matmul(matmul(bad,d),wi)!=p,'changed matcher rejected')
    def norm(a):return str(max(sum(map(abs,r)) for r in a))
    return dict(frame=506,rank=4,forward=[[str(v) for v in r] for r in w],
                inverse=[[str(v) for v in r] for r in wi],forward_norm=norm(w),inverse_norm=norm(wi),
                nonzero_coefficients=sum(v!=0 for m in [w,wi] for row in m for v in row),
                max_numerator_bits=max(abs(v.numerator).bit_length() for m in [w,wi] for row in m for v in row),
                common_denominator=__import__('math').lcm(*(v.denominator for m in [w,wi] for row in m for v in row)),
                physical_tape_price_supplied=False)


def replay(word):
    st=word['start'][:];width=len(st);rows=[1<<i for i in range(width)];paid=Counter();owned=set(word['owned']);ops=Counter()
    for e in word['records']:
        op,d=e[:2];ops[op]+=1
        if op=='ERASE':
            need(d in owned,"retained input erased");rows[d]=0;st[d]=e[2]
        elif op=='INIT':
            need(d in owned and rows[d]==0,"INIT needs whole zero");st[d]=e[2]
        elif op=='ADD':
            _,d,s,f=e;need(d!=s and st[d]==st[s]==f,"actual common-frame ADD");rows[d]^=rows[s]
        elif op in ('Q','ZERO_Q'):
            _,d,a,b,k=e;need(st[d]==a,"actual query entrance");st[d]=b
            if op=='Q':paid[k]+=1
            else:need(rows[d]==0,"zero query needs whole zero")
        else:raise ValueError("unknown operation")
    need(st==word['final'],"complete final frame vector")
    need(all(rows[i]==0 for i in owned),"all owned fields returned zero")
    return rows,paid,ops


def reverse_oracle(word, expected):
    width=len(word['start']);rows=[1<<i for i in range(width)]
    for e in reversed(word['records']):
        if e[0]=='ADD':rows[e[2]]^=rows[e[1]]
        elif e[0]=='ERASE':rows[e[1]]=0
    want=[0]*width
    for i,row in enumerate(expected):
        while row:
            bit=row & -row;want[bit.bit_length()-1]^=1<<i;row^=bit
    need(rows==want,'separate reverse all-column oracle')


@lru_cache(None)
def log_bounds(n):
    if n==1:return F(0),F(0)
    def atanh(z):
        z=F(z);k=32;s=2*sum((z**(2*j+1)/F(2*j+1) for j in range(k)),F(0))
        return s,s+2*z**(2*k+1)/(F(2*k+1)*(1-z*z))
    k=n.bit_length()-1;a,b=atanh(F(1,3));c,d=atanh(F(n-(1<<k),n+(1<<k)))
    return k*a+c,k*b+d


def power_bounds(n,c):
    l,u=log_bounds(n);lo,hi=c*l,c*u
    need(F(0)<=lo<=hi<F(1,20),"small exact exponential interval")
    def taylor(x,k):
        term=F(1);total=term
        for j in range(1,k+1):term*=(-x)/j;total+=term
        return total
    return n*taylor(hi,13),n*taylor(lo,12)


def moment(paid,targets,c):
    lo=hi=F(0)
    for k in set(paid)|set(targets):
        a,b=power_bounds(k,c);v=targets.get(k,0)-paid.get(k,0)
        lo+=v*(a if v>=0 else b);hi+=v*(b if v>=0 else a)
    return lo,hi


def compact_bounds(pair):
    scale=10**18
    return [str(F(pair[0].numerator*scale//pair[0].denominator,scale)),
            str(F(-((-pair[1].numerator*scale)//pair[1].denominator),scale))]


def main():
    for v in read('PINS.json'):need(hashlib.sha256((P/v['file']).read_bytes()).hexdigest()==v['sha256'],"source hash")
    forward=read('inputs/FORWARD.json.gz')['records'];base=read('inputs/BASE-WORD.json.gz')
    windows=source_windows(forward);word,anchors,queries=construct(base,forward,windows)
    old,oldbill,_=replay(base);new,newbill,ops=replay(word)
    need(new[:len(old)]==old and all(v==0 for v in new[len(old):]),"complete all-column join")
    reverse_oracle(word,new)
    old_types={tuple(e[2:]) for e in base['records'] if e[0]=='Q'}
    missing=sorted(set(map(tuple,queries))-old_types)
    need(missing==[(506,0,4)],'exact new residual orientation inventory')
    delta={k:newbill[k]-oldbill[k] for k in set(newbill)|set(oldbill) if newbill[k]!=oldbill[k]}
    need(delta=={1:-14,3:-14,4:14},"actual changed local invoice")
    need(newbill==Counter({1:1288,2:1342,3:56,4:57,5:102,6:10,7:9}),"proposal local profile")
    frames=read('inputs/FRAMES.json')['frames'];geometry=physical_pairs(frames,queries);matcher=matcher_506(frames)
    invoice=read('inputs/BASE-INVOICE.json');p={int(k):v for k,v in invoice['paid'].items()};t={int(k):v for k,v in invoice['targets'].items()}
    for k,v in delta.items():p[k]=p.get(k,0)+18*v
    want={1:24849,2:24156,3:1008,4:1026,5:1836,6:180,7:162,14:444,21:444,28:444,35:444,42:444,49:444,56:444,63:222}
    need(p==want and sum(t.values())==11166,"complete controller substitution")
    original=read('inputs/ORIGINAL-INVOICE.json');po={int(k):v for k,v in original['paid'].items()};to={int(k):v for k,v in original['targets'].items()}
    need({k:p.get(k,0)-po.get(k,0) for k in set(p)|set(po) if p.get(k,0)!=po.get(k,0)}=={1:-378,3:-378,4:306},"original paid delta")
    need({k:t.get(k,0)-to.get(k,0) for k in set(t)|set(to) if t.get(k,0)!=to.get(k,0)}=={4:-72},"original target debit")
    tails=[]
    for u in range(1,129):
        gap=sum(k*v for k,v in t.items() if k>=u)-sum(k*v for k,v in p.items() if k>=u)
        need(gap>=0,"rank-mass tail dominance");tails.append(gap)
    test=moment(p,t,F(3497,1000000));need(test[0]>F(1,32),"funded first moment")
    left,right=F(3497,1000000),F(35,10000)
    need(moment(p,t,right)[1]<0,"upper crossing bracket")
    while right-left>F(1,10**13):
        mid=(left+right)/2;v=moment(p,t,mid)
        if v[0]>0:left=mid
        elif v[1]<0:right=mid
        else:raise ValueError("interval precision exhausted")
    controls=['changed_residual_matcher']
    # Each of the fourteen source-version conditions must reject a data write.
    for w in windows:
        bad=[e[:] for e in forward];idx=w['inj']+1
        bad[idx]=['ADD',w['x'],0,w['l']]
        try:source_windows(bad)
        except ValueError:controls.append('source_version_'+str(w['h']))
        else:raise ValueError('stale source accepted')
    for name,choose in [('missing_snapshot',lambda e:e[0]=='ADD' and e[1]>=662),
                        ('missing_refinement',lambda e:e[0]=='Q' and e[1]==9 and e[2]==506 and e[3]==115),
                        ('missing_teardown',lambda e:e[0]=='ERASE' and e[1]>=662 and e[2] is None)]:
        mutant=dict(word);events=[e[:] for e in word['records']];idx=next(i for i,e in enumerate(events) if choose(e));events.pop(idx);mutant['records']=events
        try:
            rows,_,_=replay(mutant);need(rows==new,'changed all-column map')
        except ValueError:controls.append(name)
        else:raise ValueError('changed word accepted')
    mutant=dict(word);mutant['records']=[['ERASE',241,1]]+word['records']
    try:replay(mutant)
    except ValueError:controls.append('retained_helper_erasure')
    else:raise ValueError('arbitrary helper erased')
    events=[e[:] for e in word['records']]
    idx=next(i for i,e in enumerate(events) if e==['ADD',234,6,8]);events.pop(idx)
    mutant=dict(word);mutant['records']=events
    try:
        rows,_,_=replay(mutant);need(rows==new,'independent recipient injection lost')
    except ValueError:controls.append('recipient_injection_removed')
    else:raise ValueError('lost independent injection accepted')
    result=dict(status='PASS_G20_SOURCE_REFINEMENT_AUDIT' ,windows=windows,retained_helper444=True,
                all_input_columns=len(new),retained_local_originals=len(new)-len(word['owned']),owned=len(word['owned']),
                local_paid=dict(sorted(newbill.items())),delta_from_5653=delta,operation_counts=dict(ops),
                changed_old_events=len(anchors),new_query_types=geometry,new_residual_orientation=missing,matcher=matcher,controller_paid=p,controller_targets=t,
                paid_queries=sum(p.values()),rank_surplus=tails[0],test_C='3497/1000000',test_moment=compact_bounds(test),
                raw_crossing=[str(left),str(right)],controls=controls,source_independent=True,new_kappa=False)
    payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    outputs={'RESULT.json':payload,'EDITS.json':json.dumps(anchors,indent=2)+'\n',
             'WORD.json.gz':gzip.compress((json.dumps(word,separators=(',',':'))+'\n').encode(),mtime=0)}
    if '--write' in sys.argv:
        for name,data in outputs.items():
            (P/name).write_bytes(data if isinstance(data,bytes) else data.encode())
    else:
        for name,data in outputs.items():need((P/name).read_bytes()==(data if isinstance(data,bytes) else data.encode()),'deterministic output '+name)
    print(result['status'],len(new),'columns',len(anchors),'old event edits',len(controls),'controls',flush=True)
    print('root',float(left),float(right),'test',result['test_moment'],flush=True)


if __name__=='__main__':main()
