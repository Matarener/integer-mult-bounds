"""Deterministic same-C signed-unit MST and disjoint helper candidate.

All arithmetic is exact on a common eighth grid. Writes only --out.
"""
import argparse, collections, fractions, gzip, hashlib, json, pathlib, subprocess
Q=fractions.Fraction
HEAD='3efbb5de06a49ffeea6684482f2d3fe48cdca3fb'
PKG='research/staged-644-660-width-reduction'
HASHES={'base':'735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653','extra':'886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f'}
def need(x,msg):
 if not x: raise ValueError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def price(q):
 if not q:return 0
 a=abs(q.numerator);d=q.denominator.bit_length()-1
 need(q.denominator==1<<d,'non dyadic')
 return 3+a.bit_length()-1+a.bit_count()+d
P={i:price(Q(i,8)) for i in range(-256,257)}
def pi(i):return P[i] if i in P else price(Q(i,8))
def plus(dst,src,q):
 for k,a in src.items():
  z=dst.get(k,Q(0))+q*a
  if z:dst[k]=z
  else:dst.pop(k,None)
def add(t,s,q):return ['add',t,s,q.numerator,q.denominator,[]]
def inverse(gs):return [add(g[1],g[2],-Q(g[3],g[4])) for g in reversed(gs)]
def matrix(word):
 M={i:{} for i in range(112,224)}
 for g in word['compensation']:
  need(len(g)==6 and g[0]=='add' and 112<=g[1]<224 and 224<=g[2]<704 and g[5]==[], 'compensation schema')
  plus(M[g[1]],{g[2]:Q(1)},Q(g[3],g[4]))
 need(sum(map(len,M.values()))==len(word['compensation']),'nonaggregated original matrix')
 return M

def construct(C,w):
 targets=sorted(C); helpers=sorted(set().union(*map(set,C.values())))
 rows=[[int(8*C[t].get(h,0)) for h in helpers] for t in targets]
 need(all(Q(a,8)==C[t].get(h,0) for t,row in zip(targets,rows) for h,a in zip(helpers,row)), 'eighth grid')
 edges=[]
 for t,row in zip(targets,rows):edges.append((sum(map(pi,row)),-1,t,0))
 for i,t in enumerate(targets):
  for j in range(i):
   u=targets[j]
   for s in (-1,1):edges.append((8+sum(pi(a-s*b) for a,b in zip(rows[i],rows[j])),u,t,s))
 need(len(edges)==12544,'edge coverage')
 edges.sort(); dsu={i:i for i in [-1]+targets}
 def root(x):
  while dsu[x]!=x: x=dsu[x]
  return x
 tree=[]
 for e in edges:
  cost,a,b,s=e;ra,rb=root(a),root(b)
  if ra!=rb:dsu[ra]=rb;tree.append(e)
 need(len(tree)==112,'tree size')
 graph={i:[] for i in [-1]+targets}
 for cost,a,b,s in tree:graph[a].append((b,s,cost));graph[b].append((a,s,cost))
 parent={-1:None}; depth={-1:0}; bfs=[-1]
 for a in bfs:
  for b,s,cost in sorted(graph[a]):
   if b in parent:continue
   parent[b]=(a,s,cost);depth[b]=depth[a]+1;bfs.append(b)
 # Full all-edge cycle certificate.
 maxpaths={}
 for a in graph:
  dist={a:0};todo=[a]
  for v in todo:
   for u,s,cost in graph[v]:
    if u not in dist:dist[u]=max(dist[v],cost);todo.append(u)
  maxpaths[a]=dist
 need(all(cost>=maxpaths[a][b] for cost,a,b,s in edges),'MST cycle inequality')
 # Different Prim graph traversal (same complete edge costs).
 adjacency={i:[] for i in graph}
 for cost,a,b,s in edges:adjacency[a].append((cost,b));adjacency[b].append((cost,a))
 seen={-1}; best={t:min(cost for cost,b in adjacency[-1] if b==t) for t in targets}; prim=0
 while len(seen)<113:
  cost,t=min((v,t) for t,v in best.items() if t not in seen);seen.add(t);prim+=cost
  for cost2,b in adjacency[t]:
   if b not in seen:best[b]=min(best[b],cost2)
 need(prim==sum(e[0] for e in tree),'Prim mismatch')
 T=[];D={t:list(row) for t,row in zip(targets,rows)}
 for t in sorted(targets,key=lambda t:(-depth[t],t)):
  a,s,cost=parent[t]
  if a!=-1:T.append(add(t,a,Q(-s)))
 for t in targets:
  a,s,cost=parent[t]
  if a!=-1:D[t]=[x-s*y for x,y in zip(rows[t-112],rows[a-112])]
 # Legal full-lifetime helpers only. The parent must verify the source's
 # default frame interpretation against its frozen emitter.
 eligible=[h for h in helpers if str(h) not in w['start_extra'] and str(h) not in w['helper_final'] and h not in w['removed']]
 cols={h:[D[t][j] for t in targets] for j,h in enumerate(helpers)}
 candidates=[];count=0
 for a in eligible:
  for b in eligible:
   if a==b:continue
   old=sum(map(pi,cols[b]))
   for s in (-1,1):
    gain=old-sum(pi(v-s*u) for u,v in zip(cols[a],cols[b]))-8
    candidates.append((gain,a,b,s));count+=1
 positive=sorted((e for e in candidates if e[0]>0),key=lambda e:(-e[0],e[1:]))
 used=set();pairs=[]
 for e in positive:
  gain,a,b,s=e
  if a not in used and b not in used:pairs.append(e);used.update((a,b))
 H=[add(a,b,Q(s)) for gain,a,b,s in pairs]
 E={t:list(row) for t,row in D.items()};index={h:j for j,h in enumerate(helpers)}
 for gain,a,b,s in pairs:
  for t in targets:E[t][index[b]]-=s*D[t][index[a]]
 def injections(M):return [add(t,h,Q(a,8)) for t in targets for h,a in zip(helpers,M[t]) if a]
 f=T+injections(D)+inverse(T)
 g=T+H+injections(E)+inverse(H)+inverse(T)
 def bill(gs):return {'logical_additions':len(gs),'component_primitives':sum(price(Q(z[3],z[4])) for z in gs),'coefficient_histogram':dict(sorted(collections.Counter(str(Q(z[3],z[4])) for z in gs).items()))}
 original=bill(w['compensation']);fb=bill(f);gb=bill(g)
 need(fb['component_primitives']==prim,'literal forest bill')
 need(gb['component_primitives']==prim-sum(x[0] for x in pairs),'helper additive bill')
 rec={'edge_count':len(edges),'edge_census_sha256':sha(canonical(edges)),'tree':tree,'parent':parent,'prim_cost':prim,'all_cycle_inequalities':len(edges),'roots':len([t for t in targets if parent[t][0]==-1]),'target_edges':len(T),'max_depth':max(depth.values())-1,'active_helpers':helpers,'eligible_helpers':eligible,'helper_candidate_count':count,'helper_candidates_sha256':sha(canonical(candidates)),'profitable_helpers':len(positive),'pairs':pairs,'source_frame_predicate':'helper absent from start_extra and helper_final; not removed','target_only_bill':fb,'two_sided_bill':gb,'original_bill':original,'target_residual_nonzeros':sum(map(lambda r:sum(a!=0 for a in r),D.values())),'two_sided_residual_nonzeros':sum(map(lambda r:sum(a!=0 for a in r),E.values()))}
 return rec,f,g

def endpoint(gs,live,mode):
 rows={r:{r:Q(1)} for r in live}
 seq=inverse(gs) if mode=='inverse' else gs
 for g in seq:
  t,s,q=g[1],g[2],Q(g[3],g[4])
  if mode=='dual':t,s,q=s,t,-q
  plus(rows[t],rows[s],q)
 return rows

def semantic_controls(original, candidate, rec, live):
 """Actual operator mutations, independent of file authentication."""
 nt=rec['target_edges']; nh=len(rec['pairs'])
 ninj=rec['two_sided_residual_nonzeros']
 T=candidate[:nt]; H=candidate[nt:nt+nh]
 injection=candidate[nt+nh:nt+nh+ninj]
 Hi=candidate[nt+nh+ninj:nt+2*nh+ninj]
 Ti=candidate[nt+2*nh+ninj:]
 need(len(Hi)==nh and len(Ti)==nt,'five-stage partition')
 def changed(xs,index):
  ys=[list(g) for g in xs];ys[index]=list(ys[index]);ys[index][3]*=-1;return ys
 mutants={
  'omit_target_preparation':H+injection+Hi+Ti,
  'omit_target_restoration':T+H+injection+Hi,
  'parent_before_child_preparation':list(reversed(T))+H+injection+Hi+Ti,
  'omit_helper_preparation':T+injection+Hi+Ti,
  'omit_helper_restoration':T+H+injection+Ti,
  'flip_helper_preparation_sign':T+changed(H,0)+injection+Hi+Ti,
  'flip_residual_sign':T+H+changed(injection,0)+Hi+Ti,
  'flip_target_restoration_sign':T+H+injection+Hi+changed(Ti,-1),
  'stale_original_injection':T+H+original+Hi+Ti,
 }
 results=[]
 expected={mode:endpoint(original,live,mode) for mode in ('forward','inverse','dual')}
 for label,gs in mutants.items():
  bad={}
  for mode in expected:
   actual=endpoint(gs,live,mode)
   differing=[r for r in live if actual[r]!=expected[mode][r]]
   need(differing,'insensitive semantic control '+label+' '+mode)
   r=differing[0]; keys=sorted(set(actual[r])|set(expected[mode][r]))
   c=next(c for c in keys if actual[r].get(c,0)!=expected[mode][r].get(c,0))
   bad[mode]={'row':r,'column':c,'expected':str(expected[mode][r].get(c,0)),'actual':str(actual[r].get(c,0))}
  results.append({'mutation':label,'witnesses':bad})
 # The target preparation is essential even though a helper-only test misses it.
 omitted=endpoint(mutants['omit_target_preparation'],live,'forward')
 outside_targets=[c for c in live if not 112<=c<224]
 need(all(omitted[r].get(c,0)==expected['forward'][r].get(c,0)
          for r in live for c in outside_targets),'helper-only counterexample premise')
 results.append({'mutation':'omit_target_preparation',
                 'helper_only_projection_passes':True,
                 'projected_input_columns':len(outside_targets),
                 'full_arbitrary_target_domain_rejects':True})
 return results

def main():
 a=argparse.ArgumentParser()
 source=a.add_mutually_exclusive_group(required=True)
 source.add_argument('--repo',type=pathlib.Path)
 source.add_argument('--source-dir',type=pathlib.Path)
 a.add_argument('--out',type=pathlib.Path,required=True)
 args=a.parse_args()
 if args.source_dir:
  source_root=args.source_dir.resolve(); output_root=args.out.resolve()
  need(output_root!=source_root and source_root not in output_root.parents,
       'output must be outside frozen input directory')
 args.out.mkdir(parents=True,exist_ok=True)
 report={'head':HEAD,'providers':{}}
 for provider in ('base','extra'):
  raw=(args.source_dir/f'SOURCE-{provider}.json.gz').read_bytes() if args.source_dir else subprocess.check_output(['git','show',f'{HEAD}:{PKG}/STAGED644-660-{provider}.json.gz'],cwd=args.repo)
  need(sha(raw)==HASHES[provider],'source digest');(args.out/f'SOURCE-{provider}.json.gz').write_bytes(raw)
  w=json.loads(gzip.decompress(raw));C=matrix(w);rec,f,g=construct(C,w);live=sorted(set(range(704))-set(w['removed']));checks=[]
  for name,gs in [('forest',f),('two-sided',g)]:
   for mode in ('forward','inverse','dual'):
    need(endpoint(gs,live,mode)==endpoint(w['compensation'],live,mode),'operator mismatch '+name+mode);checks.append([name,mode,len(live)])
   panel=canonical(gs);(args.out/f'{name.upper()}-COMPENSATION-{provider}.json.gz').write_bytes(gzip.compress(panel,mtime=0))
   candidate=dict(w);candidate['compensation']=gs
   for key in w:
    if key!='compensation':need(candidate[key]==w[key],'outside changed')
   whole=canonical(candidate);(args.out/f'{name.upper()}-WORD-{provider}.json.gz').write_bytes(gzip.compress(whole,mtime=0));rec[name+'_panel_sha256']=sha(panel);rec[name+'_word_sha256']=sha(whole)
  rec['semantic_controls']=semantic_controls(w['compensation'],g,rec,live)
  rec['all_column_checks']=checks;rec['source_compressed_sha256']=sha(raw);report['providers'][provider]=rec
  print(provider,rec['original_bill']['component_primitives'],rec['target_only_bill']['component_primitives'],rec['two_sided_bill']['component_primitives'],'pairs',len(rec['pairs']),'eligible',len(rec['eligible_helpers']),flush=True)
 (args.out/'DESIGN.json').write_bytes(json.dumps(report,indent=2,sort_keys=True).encode()+b'\n')
if __name__=='__main__':main()
