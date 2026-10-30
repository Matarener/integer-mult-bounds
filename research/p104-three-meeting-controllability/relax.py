"""Exact, necessary (not sufficient) causal tensor relaxation over Q.

At meeting j, each local destination gets an independent arbitrary injection
from a source space Vj. Vj contains its baseline rows and the source spaces of
earlier meetings with a nonzero literal transfer into this meeting. This grants
more memory and independent control than an actual invertible local program.
Endpoint rows must belong to their desired final frame's target rowspace.
We also test rank after quotienting unchanged same-frame output rows.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
from emit import *

def project(row,b):
 """Linear canonical quotient; unlike early-exit membership remainder."""
 z=dict(row)
 for p,v in sorted(b.items()):
  if p in z:add(z,v,-z[p])
 return z

def case(index=1196,retimed=True):
 w=load('word5718.json.gz')
 if retimed:w=retime(w,16655,16649)
 c=json.loads((HERE/'results/contacts5718.json').read_text())['cuts'][index]
 for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
 sites=[c['cut'],15468,16652 if retimed else 16651]
 frames=[1049,1075,164]
 snap=raw(w,c,set(sites))
 roles=[[r for r,f in enumerate(snap[t][1]) if f==frame] for t,frame in zip(sites,frames)]
 return w,c,sites,frames,snap,roles

def equations_solve(equations,n):
 """Return affine solution x_j = constant + sum a_jk free_k, or failure."""
 b={}
 for row,rhs in equations:
  z=dict(row);v=rhs
  while z:
   p=min(z)
   if p not in b:
    a=z[p];z=scale(z,1/a);v/=a;b[p]=(z,v);break
   a=z[p];add(z,b[p][0],-a);v-=a*b[p][1]
  if not z and v:return None
 free=sorted(set(range(n))-set(b));aff={j:{j:Q(1)} for j in free};const={j:Q(0) for j in free}
 for p,(z,rhs) in sorted(b.items(),reverse=True):
  a={};v=rhs
  for j,q in z.items():
   if j==p:continue
   add(a,aff[j],-q);v-=q*const[j]
  aff[p]=a;const[p]=v
 return const,aff,free

def relaxation(w,c,sites,frames,snap,roles):
 need(sites==sorted(sites) and len(set(sites))==len(sites),'chronology')
 for t,f,rs in zip(sites,frames,roles):
  need(all(snap[t][1][r]==f for r in rs),'meeting source/frame')
 base,desired,*_=endpoints(w,c);groups=terminal_groups(w,c)
 outframe={r:f for f,rs in groups.items() for r in rs}
 Vs=[];Ds=[];gen=[];edges=[]
 for j,(t,rs) in enumerate(zip(sites,roles)):
  src=[dict(snap[t][0][r]) for r in rs]
  for i in range(j):
   tr=responses(w,c['pivot'],sites[i],roles[i],t)
   if any(set(tr[d])&set(rs) for d in roles[i]):
    src.extend(Vs[i]);edges.append([i,j])
  V=list(basis(src).values());Vs.append(V)
  D=responses(w,c['pivot'],t,rs);Ds.append(D)
  for d in rs:
   for v in V:gen.append((j,d,D[d],v))
 affected=sorted(set(c['d'])|{len(base)-1}|set().union(*(set(d) for _,_,d,_ in gen)))
 desired_b={f:basis(desired[r] for r in rs) for f,rs in groups.items()}
 eq=defaultdict(dict);rhs={}
 for r in affected:
  if r not in outframe:continue
  f=outframe[r];z=project(base[r],desired_b[f])
  for col,v in z.items():rhs[r,col]=-v
 for k,(_,_,d,v) in enumerate(gen):
  for r,a in d.items():
   if r not in outframe:continue
   z=project(v,desired_b[outframe[r]])
   for col,b in z.items():eq[r,col][k]=a*b
 allkeys=sorted(set(eq)|set(rhs));sol=equations_solve([(eq[k],rhs.get(k,Q(0))) for k in allkeys],len(gen))
 result=dict(source_ranks=list(map(len,Vs)),source_edges=edges,roles=roles,sites=sites,frames=frames,generators=len(gen),equations=len(allkeys),consistent=sol is not None,affected=affected)
 if sol is None:return result,None
 const,aff,free=sol;rows={r:dict(base[r]) for r in affected};coeff={r:{} for r in affected}
 for key in allkeys:
  need(sum(q*const[j] for j,q in eq[key].items())==rhs.get(key,Q(0)),'affine particular solution')
  for k in free:need(sum(q*aff[j].get(k,0) for j,q in eq[key].items())==0,'affine nullspace')
 for k,(_,_,d,v) in enumerate(gen):
  for r,a in d.items():
   add(rows[r],v,a*const[k])
   for j,b in aff[k].items():
    coeff[r].setdefault(j,{})
    add(coeff[r][j],v,a*b)
 ranks=[]
 for f,rs in groups.items():
  changed=[r for r in rs if r in affected]
  if not changed:continue
  fixed=basis(desired[r] for r in rs if r not in affected)
  available=[project(rows[r],fixed) for r in changed]
  available += [project(v,fixed) for r in changed for v in coeff[r].values()]
  rk=len(basis(available))
  ranks.append(dict(frame=f,roles=changed,required=len(changed),favorable_union_rank=rk,rank_obstruction=rk<len(changed)))
 result.update(free_parameters=len(free),rank_tests=ranks)
 # A point here is only a witness for this overly permissive tensor model.
 # It is NOT a compatible sequence of physical local matrices.
 for seed in range(1,4):
  values={j:Q((j*seed+seed)%11-5) for j in free}
  sample={r:dict(rows[r]) for r in affected}
  for r in affected:
   for j,v in coeff[r].items():add(sample[r],v,values[j])
  ok=True
  for f,rs in groups.items():
   vals=[sample.get(r,base[r]) for r in rs]
   if len(basis(vals))!=len(rs) or any(project(v,desired_b[f]) for v in vals):ok=False;break
  if ok:
   result['relaxed_full_independent_target_witness']=dict(seed=seed,free_values=values)
   break
 else:result['relaxed_full_independent_target_witness']=None
 return result,(gen,sol,rows,coeff)

def main():
 out=[]
 for idx in (1196,1199,1200):
  for rt in (False,True):
   w,c,sites,frames,snap,roles=case(idx,rt)
   r,_=relaxation(w,c,sites,frames,snap,roles);r.update(index=idx,retimed=rt)
   out.append(r);print(json.dumps(fmt(r)),flush=True)
 (ROOT/'results/relaxation.json').write_text(json.dumps(fmt(out),indent=2)+'\n')
if __name__=='__main__':main()
