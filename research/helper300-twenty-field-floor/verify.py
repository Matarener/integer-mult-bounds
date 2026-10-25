#!/usr/bin/env python3
"""Exact twenty-field monotone scalar-ADD floor; standard library only.

Station mixing relaxes chronology, invertibility and field storage. Reachability
and rank conditions are necessary; passing is never a construction test.
OpenAI Codex assisted this source-bound research audit.
"""
import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path

CANONICAL = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PROVIDER = ('research/coupled-helper-neutral-completion/capsule/workspace/'
            'swarm-provider-audit-sol-high-20261024/repository/research/'
            'native-rank8-helper-provider/WORD.json.gz')
PINS = {CANONICAL: '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05',
        PROVIDER: '7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc'}
SEMANTIC_PINS = {
    'research/kappa-rebuild/complex/native_extensions.py': '50ad007d9c386393657e86c99a96ae0a63a8fbc52872579b185002cc626e88e3',
    'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py': '106b4d5e052427230df452f0c901d5390a0583782960b80a8af94d9a984022c7',
}
START, STOP = 9044, 9137
FIELDS = [18,19,39,40,*range(288,304)]

def need(ok, why):
    if not ok: raise ValueError(why)

def span(vectors):
    s = {0}
    for v in vectors: s |= {x ^ v for x in s}
    return frozenset(s)

def dim(s): return len(s).bit_length() - 1

def touched(e):
    if e[0] == 'scalar': return {tuple(x) for x in e[1][1:] if isinstance(x,list)}
    if e[0] == 'climb': return {('L',e[2])}
    if e[0] == 'warp': return {tuple(e[1])}
    if e[0] == 'center': return {('C',e[1])}
    return set()

def load(root):
    docs = {}
    for name,pin in PINS.items():
        raw = (root/name).read_bytes()
        need(sha256(raw).hexdigest() == pin, 'source container pin '+name)
        docs[name] = json.loads(gzip.decompress(raw))
    need(docs[PROVIDER]['direction'] == 'backward', 'provider direction')
    need(docs[PROVIDER]['source_sha256'] == sha256(gzip.decompress((root/CANONICAL).read_bytes())).hexdigest(), 'provider canonical payload link')
    need(docs[PROVIDER]['word'][START:STOP] == docs[CANONICAL]['programs']['backward'][START:STOP], 'provider local tape equals inherited backward tape')
    for name,pin in SEMANTIC_PINS.items():
        need(sha256((root/name).read_bytes()).hexdigest() == pin, 'semantic source pin '+name)
    return docs[CANONICAL]['canonical'], docs[PROVIDER]['word']

def invertible_prefix(w):
    """Native climb/warp invertibility is inherited, not re-proved here."""
    for e in w[:START]:
        need(e[0] in ('scalar','warp','climb','phase','adapter','residual_adapter'), 'invertible persistent prefix grammar')
        if e[0]=='scalar':
            op=e[1]
            need(op[0] in ('add','scale') and op[1][0]=='L','no destructive prefix scalar')
            if op[0]=='add':need(op[2][0]=='L' and op[1]!=op[2] and op[4]!=0,'invertible prefix ADD')
            else:need(op[2]!=0 and op[3]!=0,'nonzero prefix SCALE')
        elif e[0]=='warp':need(e[1][0]=='L','persistent prefix warp')

def extract(c,w):
    chosen = {('L',i) for i in (19,300,301)}
    while True:
        nxt = chosen | set().union(*(touched(e) for e in w[START:STOP] if chosen & touched(e)))
        if nxt == chosen: break
        chosen = nxt
    need(sorted(chosen) == [('L',i) for i in FIELDS], 'twenty-field dependency closure')
    frames = {('L',i):f for i,f in enumerate(c['start'])}
    frames['C',0] = None
    for e in w[:START]:
        if e[0] == 'climb':
            _,_,i,a,b,r=e; need(frames['L',i]==a,'prefix climb'); frames['L',i]=b
        elif e[0] == 'warp':
            _,f,_,a,b=e; need(frames[tuple(f)]==a,'prefix warp'); frames[tuple(f)]=b
        elif e[0] == 'center':
            _,i,a,b,_=e; need(frames['C',i]==a,'prefix center'); frames['C',i]=b
        elif e[0] == 'scalar' and e[1][0]=='clear': frames[tuple(e[1][1])]=e[2]
    spaces=[span(v) for v in c['frames']]
    entry={i:frames['L',i] for i in FIELDS}
    rows={i:[Q(i==j) for j in FIELDS] for i in FIELDS}
    paths={i:[spaces[entry[i]]] for i in FIELDS}
    paid=Counter(); events=[]
    for k in range(START,STOP):
        e=w[k]
        if not touched(e)&chosen: continue
        need(touched(e)<=chosen,'closed local event'); events.append([k,e])
        if e[0]=='climb':
            _,_,i,a,b,r=e
            need(frames['L',i]==a and spaces[a]<spaces[b] and dim(spaces[b])-dim(spaces[a])==r,'local strict climb')
            frames['L',i]=b; paths[i].append(spaces[b]);paid[r]+=1
        elif e[0]=='scalar':
            op,f=e[1:]; target=op[1][1]
            need(frames['L',target]==f,'local receiver frame')
            if op[0]=='add':
                source=op[2][1]
                need(source!=target and frames['L',source]==f,'local ADD frame')
                rows[target]=[a+Q(op[3],op[4])*b for a,b in zip(rows[target],rows[source])]
            elif op[0]=='scale':
                q=Q(op[2],op[3]);need(q,'invertible scale'); rows[target]=[q*a for a in rows[target]]
            else: raise ValueError('local operation is not invertible ADD/SCALE')
        else: raise ValueError('local warp/center operation')
    need(paid=={1:38},'source 38-H1 invoice')
    return {'entry':entry,'exit':{i:frames['L',i] for i in FIELDS},'matrix':[rows[i] for i in FIELDS], 'spaces':spaces,'paths':paths,'events':events}

def all_paths(a,b):
    need(a<=b and dim(b)<=3,'bounded rank-three interval')
    found={a}; todo=[a]
    while todo:
        u=todo.pop()
        for x in b-u:
            v=span([*u,x])
            if v not in found: found.add(v);todo.append(v)
    choices=sorted(found,key=lambda s:(len(s),tuple(sorted(s))))
    def descend(u):
        if u==b: return [(u,)]
        return [(u,)+p for v in choices if u<v for p in descend(v)]
    return descend(a)

def rank(rows):
    rows=[list(r) for r in rows]; k=0
    for j in range(len(rows[0]) if rows else 0):
        p=next((i for i in range(k,len(rows)) if rows[i][j]),None)
        if p is None: continue
        rows[k],rows[p]=rows[p],rows[k]; q=rows[k][j];rows[k]=[x/q for x in rows[k]]
        for i in range(len(rows)):
            if i!=k:
                q=rows[i][j];rows[i]=[x-q*y for x,y in zip(rows[i],rows[k])]
        k+=1
    return k

def profile(path):
    p=Counter(dim(v)-dim(u) for u,v in zip(path,path[1:]))
    return tuple(p[r] for r in (1,2,3))

def polynomial(options):
    counts=Counter({(0,0,0):1})
    for opts in options.values():
        local=Counter(profile(p) for p in opts); nxt=Counter()
        for p,c in counts.items():
            for q,d in local.items(): nxt[tuple(x+y for x,y in zip(p,q))]+=c*d
        counts=nxt
    return counts

def reachable(domains, start):
    graph=defaultdict(set)
    for opts in domains.values():
        for p in opts:
            for a,b in zip(p,p[1:]): graph[a].add(b)
    seen={start}; todo=[start]
    while todo:
        a=todo.pop()
        for b in graph[a]-seen:seen.add(b);todo.append(b)
    return seen

def check_reachability(domains, block):
    endpoints={i:(opts[0][0],opts[0][-1]) for i,opts in domains.items()}
    demands=defaultdict(list)
    for r,o in enumerate(FIELDS):
        for j,i in enumerate(FIELDS):
            if block['matrix'][r][j]: demands[endpoints[i][0]].append((i,o,endpoints[o][1]))
    for start,outs in demands.items():
        seen=reachable(domains,start)
        for i,o,end in outs:
            if end not in seen:return {'input':i,'output':o,'entry_space':sorted(start),'exit_space':sorted(end),
                                      'reachable_stations':[sorted(s) for s in sorted(seen,key=lambda x:(len(x),tuple(sorted(x))))]}
    return None

def reduce_domains(options,block):
    domains={i:list(p) for i,p in options.items()}; failures=[];round_number=0
    while True:
        round_number+=1
        changed=False
        for i in FIELDS:
            if len(domains[i])==1: continue
            keep=[]
            for p in domains[i]:
                trial=dict(domains);trial[i]=[p]
                failed=check_reachability(trial,block)
                if failed:
                    failures.append({'ordinal':len(failures),'round':round_number,'field':i,
                                     'path':[sorted(x) for x in p],'witness':failed});changed=True
                else:keep.append(p)
            need(keep,'reachability screen eliminated every path');domains[i]=keep
        if not changed:break
    return domains,failures

def rank_cut(paths,inputs,outputs):
    source,sink='SOURCE','SINK'; cap=Counter(); neighbors=defaultdict(set)
    for p in paths.values():
        for a,b in zip(p,p[1:]):cap[a,b]+=1
    for i in inputs:cap[source,paths[i][0]]+=1
    for o in outputs:cap[paths[o][-1],sink]+=1
    for a,b in cap:neighbors[a].add(b);neighbors[b].add(a)
    residual=Counter(cap);flow=0
    key=lambda x:(0,x) if isinstance(x,str) else (1,tuple(sorted(x)))
    while True:
        prior={source:None};todo=deque([source])
        while todo and sink not in prior:
            a=todo.popleft()
            for b in sorted(neighbors[a],key=key):
                if b not in prior and residual[a,b]>0:prior[b]=a;todo.append(b)
        if sink not in prior:break
        edges=[];b=sink
        while b!=source:a=prior[b];edges.append((a,b));b=a
        amount=min(residual[e] for e in edges)
        for a,b in edges:residual[a,b]-=amount;residual[b,a]+=amount
        flow+=amount
    cut=[(a,b,n) for (a,b),n in cap.items() if a in prior and b not in prior]
    need(sum(n for a,b,n in cut)==flow,'exact maxflow cut certificate')
    encode=lambda x:x if isinstance(x,str) else sorted(x)
    return {'capacity':flow,'cut_edges':[[encode(a),encode(b),n] for a,b,n in cut],
            'source_side':[encode(x) for x in sorted(prior,key=key)]}

def enumerate_remaining(domains,block):
    indices={f:i for i,f in enumerate(FIELDS)}
    allspaces=set(s for pp in domains.values() for p in pp for s in p)
    groups=defaultdict(list)
    for i in FIELDS:groups[domains[i][0][0]].append(i)
    zero=[300,301,302,303]
    inputsets=[zero]+[v for v in groups.values() if v!=zero]
    inputsets += [sorted(set(zero+v)) for v in groups.values() if v!=zero]
    tests=[];seen=set()
    for ins in inputsets:
        for space in sorted(allspaces,key=lambda s:(len(s),tuple(sorted(s)))):
            outs=[i for i in FIELDS if not space<=domains[i][0][-1]]
            key=(tuple(ins),tuple(outs))
            if key in seen or not outs:continue
            seen.add(key)
            required=rank([[block['matrix'][indices[o]][indices[i]] for i in ins] for o in outs])
            if required:tests.append((ins,outs,required,space))
    rejects=[];passing=[];summary=Counter();classified=Counter()
    for assignment,selected in enumerate(itertools.product(*(domains[i] for i in FIELDS))):
        paths=dict(zip(FIELDS,selected));p=tuple(sum(profile(q)[i] for q in selected) for i in range(3))
        need(sum((i+1)*v for i,v in enumerate(p))==38,'boundary rank mass for every path assignment')
        path_indices={i:domains[i].index(paths[i]) for i in FIELDS if len(domains[i])>1}
        common={'assignment':assignment,'path_indices':path_indices,'profile':p}
        category='neutral' if p==(38,0,0) else 'saving'
        reach=check_reachability({i:[q] for i,q in paths.items()},block)
        if reach:
            rejects.append({**common,'kind':'reachability','witness':reach});summary['reachability']+=1;classified['reachability_'+category]+=1;continue
        for ins,outs,required,space in tests:
            cut=rank_cut(paths,ins,outs)
            if cut['capacity']<required:
                rejects.append({**common,'kind':'rank_cut',
                                'inputs':ins,'outputs':outs,'required_rank':required,'excluded_upset':sorted(space),
                                'cut':cut});summary['rank_cut']+=1;classified['rank_cut_'+category]+=1;break
        else:
            passing.append({**common,'paths':{i:[sorted(s) for s in paths[i]] for i in FIELDS}});summary['passing']+=1;classified['passing_'+category]+=1
    return {'tests':len(tests),'summary':summary,'classified':classified,'rejections':rejects,'passing':passing}

def reject(call,label):
    try:call()
    except ValueError:return label
    raise ValueError('negative control accepted: '+label)

def controls(b):
    labels=[];original={i:tuple(p) for i,p in b['paths'].items()}
    exact_domains={i:[p] for i,p in original.items()}
    need(check_reachability(exact_domains,b) is None,'retained word has all required scalar routes')
    altered=dict(exact_domains);altered[288]=[(original[288][0],original[288][-1])]
    failure=check_reachability(altered,b)
    need(failure is not None and (failure['input'],failure['output'])==(288,40),'skip plane422 destroys required coefficient route')
    labels.append('skip-and-restore-plane422-required-route')
    ins=[300,301,302,303];outs=[19,301,302,303];indices={f:i for i,f in enumerate(FIELDS)}
    minor=[[b['matrix'][indices[o]][indices[i]] for i in ins] for o in outs]
    need(rank(minor)==4,'independent four-helper target directions')
    broken=dict(original);broken[300]=(original[300][0],*original[300][2:])
    cut=rank_cut(broken,ins,outs)
    need(cut['capacity']==3 and rank_cut(original,ins,outs)['capacity']==4,'remove-and-restore-line273 rank channel')
    labels.append('skip-and-restore-helper300-line273-rank-channel')
    changed=[list(r) for r in minor];changed[0][1]=Q(0)
    need(rank(changed)==cut['capacity']==3,'deleting required b301 coefficient removes rank contradiction')
    labels.append('delete-target-coefficient-changes-required-rank')
    labels.append(reject(lambda:need(sum(e[2] for e in cut['cut_edges'])==cut['capacity']+1,'forged unit capacity'),'inflated-cut-capacity-rejected'))
    labels.append(reject(lambda:invertible_prefix([['scalar',['scale',['L',0],0,1],0]]),'zero-prefix-scale-rejected'))
    labels.append(reject(lambda:need(rank(changed)==4,'mutated target rank'),'mutated-rank-four-claim-rejected'))
    return labels

def run(root):
    c,w=load(root);invertible_prefix(w);b=extract(c,w);need(rank(b['matrix'])==20,'invertible local transfer')
    options={i:all_paths(b['spaces'][b['entry'][i]],b['spaces'][b['exit'][i]]) for i in FIELDS}
    domains,failures=reduce_domains(options,b)
    hist=polynomial(options);reduced_hist=polynomial(domains);screen=enumerate_remaining(domains,b)
    need(len(hist)==35 and sum(hist.values())==154618822656,'complete trajectory geometry count')
    need(sum(reduced_hist.values())==448 and len(failures)==68,'exact scalar-reachability domain reduction')
    need(screen['summary']=={'reachability':315,'rank_cut':132,'passing':1},'complete surviving-path classification')
    need(screen['passing'][0]['paths']=={i:[sorted(s) for s in p] for i,p in b['paths'].items()},'unique survivor is exactly retained source paths')
    need(screen['passing'][0]['profile']==(38,0,0),'retained source attains38H1')
    copies=[[k,e] for k,e in enumerate(w) if e[0]=='scalar' and e[1][0]=='copy' and e[1][1][0]=='C' and e[1][1][1] in range(1,9)]
    retags=[[k,e] for k,e in enumerate(w) if e[0]=='zero_retag']
    need(len(copies)==8 and min(k for k,e in copies)==11207 and all(k>=STOP for k,e in copies),'eight later protected centre copies')
    need(len(retags)==8 and all(k>=STOP for k,e in retags),'eight later zero-retags')
    endpoint=Counter(dim(b['spaces'][b['exit'][i]])-dim(b['spaces'][b['entry'][i]]) for i in FIELDS)
    capped={k:sum(n*min(r,k) for r,n in endpoint.items())-38 for k in (1,2,3)}
    need(endpoint=={1:3,2:16,3:1} and capped=={1:-18,2:-1,3:0},'optimistic infeasible endpoint invoice')
    return {'status':'PASS_TWENTY_FIELD_MONOTONE_ADD_FLOOR_NO_NEW_KAPPA','schema_version':1,
            'scope':'Fixed twenty arbitrary persistent fields, exact normalized transfer and boundary frames; rational scalar ADD/SCALE and strict monotone subspace climbs; no auxiliary fields, new warps, chart-changing exchanges, erasure or zero-retags. Native chart semantics remain inherited conditional.',
            'block':[START,STOP],'indexing':'zero-based half-open','fields':FIELDS,
            'entry':b['entry'],'exit':b['exit'],'matrix':[[str(x) for x in r] for r in b['matrix']],
            'source_inputs':[{'path':p,'sha256':h} for p,h in {**PINS,**SEMANTIC_PINS}.items()],
            'source_events':b['events'],'original_paid':{1:38},'path_counts':{i:len(p) for i,p in options.items()},
            'histograms':[{'profile':p,'count':n} for p,n in sorted(hist.items())],
            'complete_assignments':sum(hist.values()),'saving_assignments_rejected':sum(hist.values())-hist[38,0,0],
            'remaining_histograms':[{'profile':p,'count':n} for p,n in sorted(reduced_hist.items())],
            'reachability_remaining_counts':{i:len(p) for i,p in domains.items()},
            'reachability_remaining_paths':{i:[[sorted(x) for x in p] for p in pp] for i,pp in domains.items()},
            'reachability_rejections':failures,'rank_screen':screen,
            'prefix_events_checked_for_invertible_grammar':START,
            'protected_cache_copies':copies,'later_zero_retags':retags,
            'infeasible_endpoint_relaxation':{'paid_profile':dict(endpoint),'signed_capped_rank_moments_versus_38H1':capped},
            'minimum_paid_profile':{1:38},'moment_exponent_interval':'0<s<1',
            'attainment':'retained source local tape','caller_targets':'unchanged by the fixed boundary contract',
            'controls':controls(b)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--write-result',action='store_true',help='explicitly regenerate package-local RESULT.json')
    args=ap.parse_args();report=run(args.repo.resolve())
    serialized=json.dumps(report,sort_keys=True,indent=2)+'\n';expected=Path(__file__).with_name('RESULT.json')
    if args.write_result:expected.write_text(serialized,encoding='utf-8')
    else:need(json.loads(expected.read_text(encoding='utf-8'))==json.loads(serialized),'recomputed certificate differs from RESULT.json')
    print(report['status']+' minimum=38H1 rejected_saving_assignments='+str(report['saving_assignments_rejected'])+' controls='+str(len(report['controls'])))

if __name__=='__main__':main()
