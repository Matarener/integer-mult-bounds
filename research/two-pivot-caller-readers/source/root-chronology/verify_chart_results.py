#!/usr/bin/env python3
"""Pure exact replay of optimizer-produced words and a finite lower bound.
No numerical optimizer is imported or trusted by this verifier.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
from chronology import need
from batch_paid_progress import replay
from native_chart_search import compile_word
from signed_chart_optimization import graph
HERE=Path(__file__).resolve().parent


def run():
    rows=[];sources=[]
    for name in('SIGNED-CHART-HANDOFF-SIX.json','SIGNED-CHART-HANDOFF-Q3.json'):
        p=HERE/name;d=json.loads(p.read_bytes());sp=Path(d['source_path']);raw=sp.read_bytes();s=json.loads(raw)
        need(hashlib.sha256(raw).hexdigest()==d['source_sha256'],'candidate source pin')
        n=d['width'];m=d['ambient_arity'];planes=m//2
        rebuilt=compile_word(s['events'],n,planes,m,d['choices'])
        need(rebuilt==d['events'],'serialized positive word matches declared chart choices')
        need(replay(rebuilt,n,planes)==replay(s['events'],n,planes),'every original column and both inverse orders')
        H=Counter(e['operator']['native_arity']for e in rebuilt if e['kind']=='NATIVE');mass=sum(r*c for r,c in H.items())
        need(mass==d['native_mass']==n*m,'exact zero deficit, no favorable cost claim')
        need(all(2*r*r<m*m for r in H),'native child contraction')
        rows.append({'candidate':name,'banks':n,'ambient_arity':m,'histogram':dict(sorted(H.items())),'mass':mass,'stock':n*m,'D':0})
        sources.extend((p,sp))
    cp=HERE/'CHART-CYCLE-PACK-HANDOFF-SIX.json';c=json.loads(cp.read_bytes());sp=Path(c['source_path']);raw=sp.read_bytes();s=json.loads(raw)
    need(hashlib.sha256(raw).hexdigest()==c['source_sha256'],'certificate source pin')
    nodes,edges,unused=graph(s['events'],6,6);used=set()
    for cycle in c['cycles']:
        need(len(set(cycle))==len(cycle)and not used.intersection(cycle),'each edge appears at most once globally')
        used.update(cycle);parity=0;degrees={}
        for k in cycle:
            need(type(k)is int and 0<=k<len(edges),'edge index in exact graph')
            a,b,sign=edges[k];parity^=sign;degrees[a]=degrees.get(a,0)+1;degrees[b]=degrees.get(b,0)+1
        need(parity==1 and all(d%2==0 for d in degrees.values()),'odd signed Eulerian subgraph')
    bound=2*len(c['cycles']);need(bound==72,'36 edge-disjoint subgraphs force stock72')
    sources.extend((cp,sp))
    sources.extend(HERE/p for p in('chronology.py','batch_paid_progress.py','native_chart_search.py','signed_chart_optimization.py'))
    return dict(status='PASS_EXACT_RETIMED_WORDS_AND_FIXED_N6_MASS_FLOOR',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),positive_words=rows,lower_bound={'banks':6,'ambient_arity':12,'cycles':36,'native_mass_at_least':72,'matching_word_mass':72},proof='For any bit assignment to the chart graph, XOR of variable endpoint labels around every selected Eulerian subgraph is zero. Its odd signed edge sum forces at least one charged violation. Selected edge sets are disjoint; each violation has native rank2f. The bound72f matches the independently replayed word.',scope='All native-product chart retimings with the fixed literal ADD/ADDRESS/bank-SWAP skeleton of INDEPENDENT-HANDOFF-SIX.json. It does not cover altered joint bridges, changed ADD skeletons, new source deliveries, projective splitting or different endpoint contracts.',moment_consequence='Within this fixed compiler, every full-output width6 caller has rankmass>=6*12. If every recursive rankr<12 and b>0, sum r^(1-b)>12^(-b)*sum r >=6*12^(1-b). Thus no favorable positive-b moment in this compiler; added costs cannot help.',sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(set(sources))},limits=['The exact lower-bound certificate concerns n6 only; n8 has a matching break-even candidate but no general lower-bound claim here.','This is a finite exact certificate plus an all-f chart-compiler argument, not a formal-kernel theorem.'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();o=json.loads(json.dumps(run()));p=HERE/'EXACT-CHART-RESULTS.json'
    if args.write:p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==o,'saved exact chart audit differs')
    print(o['status'],'n6 exactfloor72; n6/n8 break-even words; no new kappa')
if __name__=='__main__':main()
