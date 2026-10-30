"""Independent extraction and direct cut-certificate checker; no search imports."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from math import prod
from pathlib import Path
import gzip
import json

CANONICAL='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PROVIDER='research/coupled-helper-neutral-completion/capsule/workspace/swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/WORD.json.gz'
PINS={CANONICAL:'7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05',PROVIDER:'7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc'}

def require(ok,message):
    if not ok:raise ValueError(message)

def linear_span(vs):
    s={0}
    for v in vs:s.update([x^v for x in tuple(s)])
    return frozenset(s)

def touch(e):
    if e[0]=='scalar':return {tuple(v)for v in e[1]if isinstance(v,list)}
    if e[0]=='climb':return {('L',e[2])}
    if e[0]=='warp':return {tuple(e[1])}
    return set()

def rank(matrix):
    pivots={}
    for original in matrix:
        row={j:Q(x)for j,x in enumerate(original)if x}
        while row:
            j=min(row)
            if j not in pivots:
                d=row[j];pivots[j]={k:v/d for k,v in row.items()};break
            d=row[j]
            for k,v in pivots[j].items():row[k]=row.get(k,Q(0))-d*v
            row={k:v for k,v in row.items()if v}
    return len(pivots)

def paths(a,b):
    # Independently enumerate spans of every subset of the at-most-seven
    # nonzero terminal vectors, then every strict chain in the interval.
    vs=sorted(b-{0});spaces=set()
    for size in range(len(vs)+1):
        for basis in combinations(vs,size):
            v=linear_span(basis)
            if a<=v:spaces.add(v)
    def chains(u):
        if u==b:return [(u,)]
        return [(u,)+p for v in spaces if u<v for p in chains(v)]
    return set(chains(a))

def edges(domains):
    return {(a,b)for choices in domains.values()for path in choices for a,b in zip(path,path[1:])}

def reaches(edge_set,source,target):
    seen={source}
    while True:
        nxt=seen|{b for a,b in edge_set if a in seen}
        if nxt==seen:return target in seen
        seen=nxt

def path(raw):return tuple(frozenset(v)for v in raw)

def check(root,certificate_bytes):
    raw={p:(root/p).read_bytes()for p in PINS}
    for p,d in raw.items():require(sha256(d).hexdigest()==PINS[p],'frozen source '+p)
    native=json.loads(gzip.decompress(raw[CANONICAL]));provider=json.loads(gzip.decompress(raw[PROVIDER]))
    require(provider['direction']=='backward','backward direction')
    require(provider['source_sha256']==sha256(gzip.decompress(raw[CANONICAL])).hexdigest(),'source payload binding')
    w=provider['word'];c=native['canonical'];spaces=[linear_span(v)for v in c['frames']]
    selected={('L',19),('L',300),('L',301)}
    while True:
        nxt=selected|set().union(*(touch(e)for e in w[9044:9137]if selected&touch(e)))
        if nxt==selected:break
        selected=nxt
    fields=sorted(r for k,r in selected)
    require(fields==[18,19,39,40,*range(288,304)] and all(k=='L'for k,r in selected),'exact twenty-field closure')
    current=c['start'][:]
    for e in w[:9044]:
        if e[0]=='climb':require(current[e[2]]==e[3],'prefix climb');current[e[2]]=e[4]
        elif e[0]=='warp':require(current[e[1][1]]==e[3],'prefix warp');current[e[1][1]]=e[4]
        elif e[0]=='scalar':
            g=e[1];require(g[0]in('add','scale'),'invertible prefix scalar')
            require(g[1][0]=='L','persistent prefix target')
            if g[0]=='add':require(g[2][0]=='L'and g[1]!=g[2]and g[4]!=0,'prefix ADD')
            else:require(g[2]!=0 and g[3]!=0,'prefix SCALE')
        else:require(e[0]in('phase','adapter','residual_adapter'),'invertible prefix grammar')
    entry={r:spaces[current[r]]for r in fields}
    rows={r:{r:Q(1)}for r in fields};original={r:[entry[r]]for r in fields};bill=Counter();events=[]
    for index,e in enumerate(w[9044:9137],9044):
        if not touch(e)&selected:continue
        require(touch(e)<=selected,'closed contacts');events.append([index,e])
        if e[0]=='climb':
            _,_,r,a,b,k=e
            require(current[r]==a and spaces[a]<spaces[b],'legal source climb')
            require(k==len(c['frames'][b])-len(c['frames'][a]),'source paid rank')
            current[r]=b;original[r].append(spaces[b]);bill[k]+=1
        elif e[0]=='scalar':
            g,f=e[1:];r=g[1][1];require(current[r]==f,'target coframe')
            if g[0]=='add':
                s=g[2][1];require(current[s]==f and s!=r,'source coframe');q=Q(g[3],g[4])
                for k,v in rows[s].items():rows[r][k]=rows[r].get(k,Q(0))+q*v
                rows[r]={k:v for k,v in rows[r].items()if v}
            elif g[0]=='scale':
                q=Q(g[2],g[3]);require(q,'nonzero scale');rows[r]={k:q*v for k,v in rows[r].items()}
            else:raise ValueError('noninvertible local scalar')
        else:raise ValueError('non-scalar local frame operation')
    final={r:spaces[current[r]]for r in fields}
    require(bill=={1:38} and len(events)==85,'source block invoice')
    matrix=[[rows[r].get(s,Q(0))for s in fields]for r in fields];require(rank(matrix)==20,'full arbitrary-input rank')
    d=json.loads(certificate_bytes)
    require(d['fields']==fields and d['matrix']==[[str(v)for v in row]for row in matrix],'independent matrix agreement')
    require(d['source_events']==events,'independent event agreement')
    domains={r:paths(entry[r],final[r])for r in fields};initial_count=prod(map(len,domains.values()))
    require(initial_count==154618822656,'complete initial frame paths')
    def unreachable_witness(ed,witness):
        i,o=witness['input'],witness['output']
        require(rows[o].get(i,Q(0))!=0,'nonzero demanded coefficient')
        require(not reaches(ed,entry[i],final[o]),'claimed missing path')
    for rejected in d['reachability_rejections']:
        r=rejected['field'];p=path(rejected['path']);require(p in domains[r],'path not previously removed')
        trial=dict(domains);trial[r]={p}
        unreachable_witness(edges(trial),rejected['witness'])
        domains[r].remove(p);require(domains[r],'nonempty remaining domain')
    ordered={int(r):[path(p)for p in ps]for r,ps in d['reachability_remaining_paths'].items()}
    require(all(len(ps)==len(set(ps))for ps in ordered.values()),'no duplicate listed paths')
    expected={r:set(ps)for r,ps in ordered.items()}
    require(domains==expected,'all and only recorded remaining paths')
    candidates=set(product(*(domains[r]for r in fields)));require(len(candidates)==448,'exact reduced Cartesian product')
    variable={str(r)for r in fields if len(ordered[r])>1};counts=Counter()
    for rejection in d['rank_screen']['rejections']:
        indices=rejection['path_indices'];require(set(indices)==variable,'exact variable path selectors')
        require(all(type(i)is int and 0<=i<len(ordered[int(r)])for r,i in indices.items()),'legal path index')
        candidate=tuple(ordered[r][indices.get(str(r),0)]for r in fields)
        require(candidate in candidates,'unique covered candidate');candidates.remove(candidate)
        ed=Counter((a,b)for p in candidate for a,b in zip(p,p[1:]))
        if rejection['kind']=='reachability':
            unreachable_witness(set(ed),rejection['witness'])
        else:
            require(rejection['kind']=='rank_cut','known certificate type')
            ins,outs=rejection['inputs'],rejection['outputs'];minor=[[rows[o].get(i,Q(0))for i in ins]for o in outs]
            target_rank=rank(minor);require(target_rank==rejection['required_rank'],'independent minor rank')
            removed=set();capacity=0
            for a,b,n in rejection['cut']['cut_edges']:
                edge=(frozenset(a),frozenset(b));require(edge not in removed and ed[edge]==n,'complete original edge capacity')
                removed.add(edge);capacity+=n
            require(capacity==rejection['cut']['capacity'] and capacity<target_rank,'strict cut deficit')
            for i in ins:
                for o in outs:require(not reaches(set(ed)-removed,entry[i],final[o]),'listed edges really disconnect selected sources and sinks')
        counts[rejection['kind']]+=1
    source_paths=tuple(tuple(original[r])for r in fields)
    require(candidates=={source_paths},'only original paths survive all independently checked rejections')
    require(counts=={'reachability':315,'rank_cut':132},'complete rejection census')
    return dict(status='PASS_INDEPENDENT_TWENTY_FIELD_PATH_CERTIFICATE',
                source_pins=PINS,certificate_sha256=sha256(certificate_bytes).hexdigest(),
                initial_path_assignments=initial_count,domain_rejections=len(d['reachability_rejections']),
                reduced_assignments=448,missing_path_rejections=315,rank_cut_rejections=132,
                survivors=1,unique_survivor_is_original=True,minimum_paid_profile={'1':38},
                proof_boundary='Fixed twenty fields and entry/exit frames; arbitrary rational ADD/SCALE; strict monotone climbs; no auxiliary fields, new warps, descent or chart-changing exchange.')

def controls(root,certificate_bytes):
    results=[]
    for name in ('missing-rejection-creates-coverage-gap','changed-cut-capacity','changed-target-minor-rank'):
        d=json.loads(certificate_bytes)
        if name=='missing-rejection-creates-coverage-gap':
            d['rank_screen']['rejections'].pop()
        else:
            r=next(r for r in d['rank_screen']['rejections']if r['kind']=='rank_cut')
            if name=='changed-cut-capacity':r['cut']['cut_edges'][0][2]+=1
            else:r['required_rank']+=1
        try:
            check(root,json.dumps(d).encode())
        except ValueError as exc:
            results.append({'name':name,'rejected':True,'reason':str(exc)})
        else:
            raise ValueError('semantic certificate control was accepted: '+name)
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--certificate',type=Path,default=Path(__file__).with_name('RESULT.json'))
    p.add_argument('--json',action='store_true')
    a=p.parse_args()
    certificate_bytes=a.certificate.read_bytes()
    result=check(a.repo,certificate_bytes)
    result['controls']=controls(a.repo,certificate_bytes)
    if a.json:print(json.dumps(result,indent=2))
    else:print(result['status']+'; 68 domain removals, 315 missing paths, 132 rank cuts, one original 38-H1 survivor; 3 semantic controls rejected.')
