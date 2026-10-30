"""Generate a candidate dual with NetworkX3.5; verification needs no solver.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
NetworkX's network simplex is predecessor software, not a new algorithm.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from construct import graph,verify_dual
import networkx as nx

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
if nx.__version__!='3.5':raise ValueError('Use the declared NetworkX3.5 search environment')
source=json.loads(gzip.decompress((Path(__file__).resolve().parent/'inputs/WORD.json.gz').read_bytes()))
data=graph(source);g=nx.MultiDiGraph();supply=[0]*(data['count']+1)
for i,(a,b,e,w) in enumerate(data['edges']):
    supply[a]+=w;supply[b]-=w;g.add_edge(a,b,key=i,capacity=2*w,weight=-e)
for i,v in enumerate(supply):g.add_node(i,demand=-v)
cost,flow=nx.network_simplex(g)
y=[];residual=[]
for i,(a,b,e,w) in enumerate(data['edges']):
    f=flow[a][b][i];y.append(f-w)
    if f<2*w:residual.append((a,b,-e))
    if f>0:residual.append((b,a,e))
distance=[0]*len(supply)
for iteration in range(len(supply)):
    changed=False
    for a,b,c in residual:
        if distance[b]>distance[a]+c:distance[b]=distance[a]+c;changed=True
    if not changed:break
else:raise ValueError('Residual negative cycle')
x=[distance[0]-v for v in distance]
objective=sum(e*v for (a,b,e,w),v in zip(data['edges'],y))
certificate={'schema':'p104-gauge-dual/1','potentials':x,'dual':y,'objective':objective,
             'search_environment':'Python3.12.14; NetworkX3.5; integer network_simplex',
             'network_cost':cost,'residual_passes':iteration+1}
verify_dual(data,certificate)
args.output.write_text(json.dumps(certificate,indent=1)+'\n')
print('EXACT_MATCHING_DUAL',data['count'],len(y),objective,'zero gauge',sum(abs(e)*w for a,b,e,w in data['edges']))
