"""Read-only independent audit of the exported one-frame support certificate.

Does not import verify.py, predecessor-experiment.py, or clifford_exact.py.
It uses the retained independent Gaussian circuit interpreter for frame maps.
Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import gzip, importlib.util, json, sys
R=Path(__file__).resolve().parent

def check(x,why):
    if not x:raise ValueError(why)

def read(p):
    b=(R/p).read_bytes();return json.loads(gzip.decompress(b) if p.endswith('.gz') else b)

def binary_dimension(vectors):
    # Low-pivot elimination, separate from producer's high-pivot routine.
    pivots={}
    for x in vectors:
        while x:
            p=(x&-x).bit_length()-1
            if p in pivots:x^=pivots[p]
            else:pivots[p]=x;break
    return len(pivots)

def scalar_rank(rows):
    prime=1000003;basis={}
    for row in rows:
        row={int(k):(Q(v).numerator*pow(Q(v).denominator,-1,prime))%prime for k,v in row.items()}
        while row:
            pivot=max(row);a=row[pivot]
            if pivot not in basis:
                scale=pow(a,-1,prime);basis[pivot]={k:v*scale%prime for k,v in row.items()};break
            for k,v in basis[pivot].items():
                z=(row.get(k,0)-a*v)%prime
                if z:row[k]=z
                else:row.pop(k,None)
    return len(basis)


def run():
    cert=read('results/CERTIFICATE.json.gz');maps=read('inputs/QUERY-MAPS.json.gz');w=read('inputs/word5718.json.gz')
    main=set(w['live'])|{r+112 for r in w['live']};helper=set(range(w['public']))-main
    projected=lambda p:{k:Q(v) for k,v in p['row'].items() if int(k) in helper}
    by_event={str(p['event']):p for p in maps['queries']}
    query=by_event['13660'];check(query==cert['query'],'Target query map')
    events=cert['prefix_events'];check(events==[p['event'] for p in maps['queries'] if p['event']<13660],'All and only chronological prefix outputs')
    co=cert['source_helper_coordinates'];tc=cert['target_helper_coordinates'];dc=cert['destination_observation_coordinates']
    obs=next(x for x in maps['selected_current_frame_rows'] if x['event']==13660)
    sources=dict(by_event)
    for r,v,last,row in obs['donors']:sources[f'current:{r}:v{v}']={'row':row}
    for p in obs['retained']:sources[f"retained:{p['event']}"]=p
    all_labels=set().union(*(set(c) for c in co),set(tc),*(set(c) for c in dc))
    check(scalar_rank([projected(sources[label]) for label in all_labels])==len(all_labels),'Coordinate source rows independent over Q (full modular rank suffices)')
    def expand(c):
        out=Counter()
        for label,q in c.items():
            for k,v in projected(sources[label]).items():out[k]+=Q(q)*v
        return {k:v for k,v in out.items() if v}
    for event,c in zip(events,co):check(expand(c)==projected(by_event[str(event)]),'Every exact coordinate expansion')
    check(expand(tc)==projected(query),'Exact target-coordinate expansion')
    destination_rows=[row for r,v,last,row in obs['donors']]+[p['row'] for p in obs['retained']]
    check(len(dc)==len(destination_rows),'All destination observations')
    for c,row in zip(dc,destination_rows):check(expand(c)==projected({'row':row}),'Exact destination-coordinate expansion')
    check(all(not row.get('21') for row in destination_rows),'Destination cannot supply fresh helper21')
    check(Q(query['row']['21'])==Q(-1,4),'Nonzero fresh-helper response')
    groups={}
    for event in events:groups.setdefault(str(by_event[str(event)]['new']),[]).append(event)
    check(groups==cert['source_frame_groups'],'Complete source-coframe bundles')
    coords_by_event=dict(zip(events,co))
    supports={f:set().union(*(set(coords_by_event[e]) for e in es)) for f,es in groups.items()}
    spec=importlib.util.spec_from_file_location('independent_native',R/'inputs/native_verify.py');V=importlib.util.module_from_spec(spec);sys.modules[spec.name]=V;spec.loader.exec_module(V)
    L=[]
    for frame in w['frames']:
        tab=V.tableau(V.adjoint(V.frame(tuple(frame),9)))
        L.append(tuple(x|(z<<9) for x,z,p in tab[9:]))
    @lru_cache(None)
    def distance(a,b):return binary_dimension(L[a]+L[b])-9
    counts=Counter();dc_support=set().union(*(set(c) for c in dc))
    check([r['frame'] for r in cert['frame_receipts']]==list(range(1090)),'Every pinned frame exactly once')
    for r in cert['frame_receipts']:
        f=r['frame'];final=distance(f,598);B=6-final
        check((r['final_rank'],r['ingress_rank_budget'])==(final,B),'Final charge and residual budget')
        if B<0:
            check(r['status']=='FINAL_DELIVERY_ALREADY_COSTS_AT_LEAST_H7','Final rank rejection');counts['final_rank']+=1;continue
        costs={s:distance(int(s),f) for s in groups}
        h21=[costs[str(by_event[str(e)]['new'])] for e in events if Q(by_event[str(e)]['row'].get('21','0'))]
        if r['status']=='FRESH_HELPER21_UNAVAILABLE_WITHIN_INGRESS_BUDGET':
            check(min(h21)>B and min(h21)==r['minimum_helper21_ingress_rank'],'Every source lacking affordable fresh helper21');counts['helper21']+=1;continue
        check(r['status']=='EXACT_HELPER_COORDINATE_COVER_EXCEEDS_BUDGET','Support certificate status')
        s=r['certificate'];check(costs==s['source_frame_ingress_ranks'],'Every source-frame ingress charged')
        free=[f for f,c in costs.items() if c==0 or (c<=B and len(supports[f])>s['threshold'])]
        check(list(map(str,s['free_source_frames']))==free,'Favorable free source bundles')
        ignored=dc_support|set().union(*(supports[f] for f in free))
        check(set(map(str,s['ignored_coordinates']))==ignored,'Ignored-coordinate union')
        uncovered=set(tc)-ignored;check(set(map(str,s['uncovered_target_coordinates']))==uncovered,'All mandatory target coordinates')
        maxwidth={str(rank):max((len(supports[f]-ignored) for f,c in costs.items() if c==rank),default=0) for rank in range(1,B+1)}
        check(maxwidth==s['max_coordinate_coverage_by_ingress_rank'],'Complete coverage tariff')
        dp=s['coverage_capacity_dp'];check(len(dp)==B+1 and dp[0]==0,'DP base and extent')
        for b in range(1,B+1):check(dp[b]==max([dp[b-1]]+[maxwidth[str(rank)]+dp[b-rank] for rank in range(1,b+1)]),'Optimistic knapsack upper bound')
        check(len(uncovered)>dp[B] and len(uncovered)-dp[B]==s['obstruction_margin'],'Strict support-budget obstruction');counts['support']+=1
    check(dict(counts)=={'final_rank':411,'helper21':338,'support':341},'Complete exhaustive result')
    print('PASS_INDEPENDENT_SHARED_GATHER_CERTIFICATE_AUDIT frames=1090 source_bundles=465 prefix_answers=1211')

if __name__=='__main__':run()
