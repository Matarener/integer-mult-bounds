"""Lazy bucket factors and a complete sparse all-input-column lifecycle replay.

The supplied K macro is an explicit inherited contract, not a free native gate.
"""
from fractions import Fraction as F
from collections import defaultdict
import random
from e8_exact import vector,label,dot,need,mixed_port
from pair_factor import coefficient,factor_columns,primitive,product


def add_row(dst,src,c):
    for k,v in src.items():
        dst[k]=dst.get(k,F(0))+c*v
        if not dst[k]:del dst[k]


def group_ports(indices,geo):
    roots,pure,sig,buckets=geo
    result=defaultdict(list)
    for p in sorted(indices):result[label(p,roots,pure,sig,buckets)].append(p)
    return dict(sorted(result.items()))


def captures(source_indices,target_indices,geo,compressed=True):
    """Compile-time fixed H6 indices only; full outputs may be iterated lazily."""
    roots,pure,sig,buckets=geo
    source_groups=group_ports(source_indices,geo);targets=group_ports(target_indices,geo)
    for cap,ts in targets.items():
        for line,ss in source_groups.items():
            if line[0] and line[1]:
                need(len(ss)==2 and ss[0]>=2160 and ss[1]==ss[0]+1 and (ss[0]-2160)%2==0,
                     'complete actual mixed source pair')
                C=[[coefficient(vector(t,roots,pure),vector(s,roots,pure),t==s) for s in ss] for t in ts]
                sigma=None
                if compressed:
                    if all(r[1]==r[0] for r in C):sigma=1
                    elif all(r[1]==-r[0] for r in C):sigma=-1
                G,D=factor_columns(C,sigma)
                need(product(D,G)==C,'compiled local factor identity')
                for j,weights in enumerate(G):
                    yield {'line':line,'cap':cap,'source_pair':list(ss),
                           'G':{s:v for s,v in zip(ss,weights) if v},
                           'D':{t:D[i][j] for i,t in enumerate(ts) if D[i][j]}}
            else:
                for s in ss:
                    D={t:coefficient(vector(t,roots,pure),vector(s,roots,pure),t==s) for t in ts}
                    D={t:v for t,v in D.items() if v}
                    if D:yield {'line':line,'cap':cap,'source_pair':[s], 'G':{s:F(1)},'D':D}


def factor_check(records,sources,targets,geo):
    roots,pure,_,_=geo
    found={(t,s):F(0) for t in targets for s in sources}
    for row in records:
        for t,d in row['D'].items():
            for s,g in row['G'].items():found[t,s]+=d*g
    need(all(found[t,s]==coefficient(vector(t,roots,pure),vector(s,roots,pure),t==s)
             for t in targets for s in sources),'complete DG=C factor on every fixture entry')


def replay(records,indices,geo,dual=False,omit=None,wrong_sigma=False,early_full=False):
    roots,pure,_,_=geo
    groups=group_ports(indices,geo)
    representative={g:vector(m[0],roots,pure) for g,m in groups.items()}
    labels={p:g for g,m in groups.items() for p in m}
    x={p:{('x',p):F(1)} for p in indices};y={p:{('y',p):F(1)} for p in indices}
    h=[{('e',j):F(1)} for j in range(len(records))]
    xf={p:('line',labels[p]) for p in indices};yf={p:('zero',) for p in indices}
    hf=[('zero',) for _ in records];paths=[[] for _ in records]
    def plus(dst,src,c,df,sf,phase):
        need(df==sf,'actual same-frame operands at '+phase)
        if phase==omit:return
        if dual:add_row(src,dst,-c)
        else:add_row(dst,src,c)
    def climb(j,kind,target,increment):
        if kind=='line':need(hf[j]==('zero',),'helper starts at ZERO')
        if kind=='cap':
            need(hf[j]==('line',records[j]['line']),'captured helper source line')
            a,b=representative[records[j]['line']],representative[target]
            need(dot(a,b)%4==0 and (dot(a,b)//4)%2==1,'source line lies in bucket cap')
        if kind=='full':need(hf[j]==('cap',records[j]['cap']),'helper reaches its cap before FULL')
        hf[j]=(kind,target) if kind!='full' else ('full',);paths[j].append(increment)
    for j,row in enumerate(records):
        for t,d in row['D'].items():plus(y[t],h[j],-d,yf[t],hf[j],'dirt_prefix')
    for j,row in enumerate(records):
        climb(j,'line',row['line'],1)
        for at,(s,g) in enumerate(row['G'].items()):
            if wrong_sigma and g==-1:g=1
            plus(h[j],x[s],g,hf[j],xf[s],'capture')
    if early_full:
        xf={p:('full',) for p in indices}
    # Exact full K contract from4027/legacy theorem: it accepts arbitrary
    # current source/target values, advances its own sources and targets,
    # restores its unrelated auxiliary dirt, and has its own separately paid bill.
    need(all(xf[p]==('line',labels[p]) and yf[p]==('zero',) for p in indices),
         'complete K receives actual source lines and ZERO targets')
    if omit!='K':
        if dual:
            for s in indices:
                for t in indices:
                    k=F(int(s==t))-coefficient(vector(t,roots,pure),vector(s,roots,pure),s==t)
                    if k:add_row(x[s],y[t],-k)
        else:
            for t in indices:
                for s in indices:
                    k=F(int(s==t))-coefficient(vector(t,roots,pure),vector(s,roots,pure),s==t)
                    if k:add_row(y[t],x[s],k)
    xf={p:('full',) for p in indices};yf={p:('cap',labels[p]) for p in indices}
    for j,row in enumerate(records):
        climb(j,'cap',row['cap'],15)
        for t,d in row['D'].items():plus(y[t],h[j],d,yf[t],hf[j],'scatter')
    for j,row in enumerate(records):
        climb(j,'full',None,1)
        for s,g in row['G'].items():
            if wrong_sigma and g==-1:g=1
            plus(h[j],x[s],-g,hf[j],xf[s],'cleanup')
    # Check dirt first: a matched wrong capture/cleanup sign can restore every
    # helper and nevertheless compute the wrong data map.
    need(all(row=={('e',j):F(1)} for j,row in enumerate(h)),'every arbitrary logical helper entrance returned')
    need(all(f==('full',) and p==[1,15,1] for f,p in zip(hf,paths)),'complete helper frame paths')
    for p in indices:
        X={('x',p):F(1)};Y={('y',p):F(1)}
        if dual:X[('y',p)]=F(-1)
        else:Y[('x',p)]=F(1)
        need(x[p]==X and y[p]==Y,'all data and helper-dirt columns at complete endpoint')
    return {'dual':dual,'data_ports':len(indices),'helper_roles':len(records),
            'all_input_columns':2*len(indices)+len(records),'helper_path':[1,15,1],
            'logical_dirt_return':True,'physical_helper_endpoint':'FULL applied to its original dirt, not literal physical entrance'}


def choose_fixture(geo,seed=83):
    roots,pure,sig,buckets=geo
    rng=random.Random(seed);i,j=rng.randrange(120),rng.randrange(120)
    odd=lambda v:[k for k,r in enumerate(roots) if (dot(v,r)//4)%2]
    zero=lambda v:[k for k,r in enumerate(roots) if dot(v,r)==0]
    a=rng.choice(odd(roots[i]));b=rng.choice(zero(roots[j]))
    c=rng.choice(zero(roots[i]));d=rng.choice(odd(roots[j]))
    pair_indices={(i,j),(a,b),(c,d),(i,d)}  # plus, minus, full-rank cases
    selected=[]
    for x,y in sorted(pair_indices):selected.extend((mixed_port(x,y),mixed_port(x,y,True)))
    for block,root in ((0,roots[i]),(1,roots[j])):
        groups=[g for g,m in buckets.items() if (dot(root,pure[m[0]])//4)%2]
        chosen=rng.choice(groups)
        selected.extend(p+1080*block for p in buckets[chosen])
    return sorted(set(selected)),{'seed':seed,'source_pair':[i,j],'mixed_label_pairs':sorted(map(list,pair_indices))}


def fixture(geo):
    indices,domain=choose_fixture(geo)
    old=list(captures(indices,indices,geo,False));new=list(captures(indices,indices,geo,True))
    factor_check(old,indices,indices,geo);factor_check(new,indices,indices,geo)
    def counts(rows):
        return {'helpers':len(rows),'capture_entries':sum(len(r['G']) for r in rows),
                'scatter_entries':sum(len(r['D']) for r in rows),
                'component_primitives':2*sum(primitive(v) for r in rows for v in r['G'].values())+
                                       2*sum(primitive(v) for r in rows for v in r['D'].values())}
    need(counts(old)['capture_entries']==counts(new)['capture_entries'],'sharing retains both charged source reads')
    need(len(new)<len(old) and any(-1 in r['G'].values() for r in new),'both useful sharing signs in complete fixture')
    return {'domain':domain,'indices':indices,'old':counts(old),'new':counts(new),
            'old_orientations':[replay(old,indices,geo,d) for d in (False,True)],
            'orientations':[replay(new,indices,geo,d) for d in (False,True)]},(indices,old,new)
