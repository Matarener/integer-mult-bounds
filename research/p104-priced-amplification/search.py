"""Generate one source-bound amplification-price candidate with NetworkX3.5.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The default verifier does not import this search or NetworkX.
"""
import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import tarfile
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify import load,norms,floor_log,verify_price,need
import networkx as nx

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cap',type=Q,required=True)
p.add_argument('--strict',action='store_true')
p.add_argument('--output',type=Path,required=True)
args=p.parse_args();need(args.cap>=2,'cap at least the output lower bound')
need(nx.__version__=='3.5','declared NetworkX3.5 search environment')
here=Path(__file__).resolve().parent
pin=json.loads((here/'SOURCES.json').read_text())['exports'][0];archive=here/pin['path']
need(sha256(archive.read_bytes()).hexdigest()==pin['sha256'],'exact source export')
with tempfile.TemporaryDirectory(prefix='p104-amplification-search-') as directory:
    with tarfile.open(archive) as stream:stream.extractall(directory,filter='data')
    parent=Path(directory)/'research/p104-complete-dyadic-gauges'
    c=load(parent/'construct.py','search_construct');local=load(parent/'local.py','search_local')
    source=json.loads(gzip.decompress((parent/'inputs/WORD.json.gz').read_bytes()))
    data=c.graph(source);levels,_,_=norms(source,local,data,data['count']);n=data['count']+1
    upper={i:floor_log(args.cap/v)-int(args.strict and Q(2)**floor_log(args.cap/v)==args.cap/v)
           for i,v in enumerate(levels) if v}
    feasible=[min(0,upper.get(i,0)) for i in range(n)]
    penalty=1+sum(w*abs(e+feasible[a]-feasible[b]) for a,b,e,w in data['edges'])
    edges=[[a,b,e,-w,w] for a,b,e,w in data['edges']]+[[i,0,-u,0,penalty] for i,u in upper.items()]
    graph=nx.MultiDiGraph();supply=[0]*n
    for i,(a,b,e,lo,hi) in enumerate(edges):
        supply[a]-=lo;supply[b]+=lo;graph.add_edge(a,b,key=i,capacity=hi-lo,weight=-e)
    for i,v in enumerate(supply):graph.add_node(i,demand=-v)
    _,flow=nx.network_simplex(graph);dual=[];residual=[]
    for i,(a,b,e,lo,hi) in enumerate(edges):
        f=flow[a][b][i];dual.append(lo+f)
        if f<hi-lo:residual.append((a,b,-e))
        if f>0:residual.append((b,a,e))
    distance=[0]*n
    for _ in range(n):
        changed=False
        for a,b,v in residual:
            if distance[b]>distance[a]+v:distance[b]=distance[a]+v;changed=True
        if not changed:break
    else:raise ValueError('residual negative cycle')
    powers=[distance[0]-v for v in distance]
    objective=sum(w*abs(e+powers[a]-powers[b]) for a,b,e,w in data['edges'])
    result={'peak_cap':str(args.cap),'strict':args.strict,'potentials':powers,
            'original_dual':dual[:len(data['edges'])],'norm_dual':dual[len(data['edges']):],
            'norm_nodes':list(upper),'objective':objective,'penalty':penalty}
    verify_price(data,levels,result)
    args.output.write_text(json.dumps(result,indent=1)+'\n')
    print('PASS_EXACT_AMPLIFICATION_PRICE_CANDIDATE',args.cap,objective)
