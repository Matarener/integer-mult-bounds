"""Source-bound three-meeting obstruction, exact rational arithmetic only.

The first meeting allows any GL_m(Q) map on EVERY public field at its frame.
Later meetings are further relaxed to arbitrary linear transforms. The final
normalizer may be arbitrary rational within each actual final frame.
"""
from relax import *

def sumrows(rows,weights):
 out={}
 for r,q in weights.items():add(out,rows[r],q)
 return out

def walk(w,c,rows,start,stop):
 for e in w['program'][start+1:stop+1]:apply(rows,renamed(e,c['pivot'],len(rows)-1))

def certify(index,retimed):
 w,c,ts,fs,snap,roles=case(index,retimed);t1,t2,t3=ts
 R1=snap[t1][0];S=basis(R1[r] for r in roles[0])
 need(len(S)==len(roles[0]),'independent first-meeting source rows')
 # Independent formal rows represent arbitrary transformed first-meeting rows.
 formal={r:{2000+r:Q(1)} for r in roles[0]}
 rows=[dict(z) for z in R1]
 for r,z in formal.items():rows[r]=dict(z)
 walk(w,c,rows,t1,t2)
 A=dict(rows[479]);B=dict(rows[527])
 L=responses(w,680,t1,roles[0],t2)
 l={r:v.get(753,Q(0)) for r,v in L.items() if v.get(753)}
 lrow=sumrows(formal,l);want=dict(A);add(want,lrow)
 need(rows[753]==want,'second continuation = A+L')
 need(not (set(A)|set(B))&set().union(*(set(v) for v in formal.values())),'A/B independent of first transform')
 # A replaced second continuation Q carries the CHANGED first-meeting state.
 # Other second destinations have no transfer into the third meeting or output153.
 d2=responses(w,680,t2,roles[1]);mid2=responses(w,680,t2,roles[1],t3)
 for r in (479,527):
  need(153 not in d2[r] and not set(mid2[r])&set(roles[2]),'unused second outputs cannot repair153')
 rows[753]={3000:Q(1)}
 walk(w,c,rows,t2,t3)
 C=dict(rows[753]);add(C,{3000:Q(1)},-1)
 want=scale(C,Q(1,2));add(want,{3000:Q(1)},Q(-1,2))
 need(rows[685]==want,'third rows = (C-Q)/2, C+Q')
 N=dict(rows[153]);need(not set(N)&set().union(*(set(v) for v in formal.values())),'third153 unaffected by first transform')
 cweights={r:C.get(2000+r,Q(0)) for r in roles[0] if C.get(2000+r)}
 C0=dict(C);add(C0,sumrows(formal,cweights),-1)
 need(cweights=={685:Q(1)},'C = changed first685 + C0')
 # Propagate the formal rows to the endpoint, retaining Q as a free symbol.
 walk(w,c,rows,t3,len(w['program'])-1)
 target=endpoints(w,c)[1][153]
 end=rows[153];x={r:end.get(2000+r,Q(0))+l.get(r,Q(0)) for r in roles[0]}
 x={r:q for r,q in x.items() if q}
 X=sumrows(formal,x)
 want=dict(target);add(want,X);add(want,lrow,-1);add(want,A,-1);add(want,{3000:Q(1)})
 need(end==want,'exact final153 = target+X-L-A+Q')
 d3=responses(w,680,t3,roles[2])
 # Any later transform affects153 by a linear combination of N,C,Q.
 # The relaxed model grants all three coefficients independently.
 need(all(not set(snap[t3][0][r])&{680} for r in roles[2]),'third source sanity')
 need(terminal_groups(w,c)[164]==[153],'actual final153 singleton')
 # t,S,A,B,C0,N are independent. More specifically, N has private44,
 # C0 private22, A private479, B private527, target private153.
 external=[target,A,B,C0,N]
 ranks=[len(S)]
 sb=dict(S)
 for v in external:
  sb=basis(list(sb.values())+[v]);ranks.append(len(sb))
 need(ranks==list(range(len(S),len(S)+6)),'external independent directions')
 need(len(basis([x,l]))==2,'X and L independent coefficient combinations')
 # These linear functionals successively force g=0, lambda=1, k=0,
 # l*a=1, l*b=0 in target+X-L-A+k*C+l*(w*L+a*A+b*B)+g*N=lambda*target.
 probes={44:dict(N=N.get(44,0),C0=C0.get(44,0),A=A.get(44,0),B=B.get(44,0),target=target.get(44,0)),
         153:dict(N=N.get(153,0),C0=C0.get(153,0),A=A.get(153,0),B=B.get(153,0),target=target.get(153,0)),
         22:dict(C0=C0.get(22,0),A=A.get(22,0),B=B.get(22,0)),
         479:dict(A=A.get(479,0),B=B.get(479,0)),527:dict(A=A.get(527,0),B=B.get(527,0))}
 need(probes[44]==dict(N=Q(-1),C0=0,A=0,B=0,target=0),'private44 probe')
 need(probes[153]['target']==1 and all(probes[153][k]==0 for k in ('C0','A','B')),'target153 probe')
 need(probes[22]==dict(C0=Q(1,2),A=0,B=0),'private22 probe')
 need(probes[479]==dict(A=Q(1),B=0) and probes[527]==dict(A=0,B=Q(1)),'A/B probes')
 # Then X+(l*w-1)L=0 contradicts independence under any GL_m first map.
 return dict(index=index,retimed=retimed,sites=ts,frames=fs,roles=roles,first_rank=len(S),X=x,L=l,
             coefficient_pair_rank=2,external_ranks=ranks,A=A,B=B,C0=C0,N=N,target153=target,probes=probes,
             endpoint_identity='target153 + X - L - A + k*C + ell*Q + g*N; Q=w*L+a*A+b*B; C=first685+C0',
             forced_equations=['g=0','lambda=1','k=0','ell*a=1','ell*b=0','X+(ell*w-1)*L=0'],
             status='NO_GL_FIRST_MEETING_SOLUTION',all_input_coefficients_checked=True)

def main():
 out=[certify(i,r) for i in (1196,1199,1200) for r in (False,True)]
 (ROOT/'results/obstruction.json').write_text(json.dumps(fmt(out),indent=2)+'\n')
 print(json.dumps(fmt([{k:v for k,v in r.items() if k in ('index','retimed','sites','first_rank','X','L','coefficient_pair_rank','external_ranks','status')} for r in out])),flush=True)
if __name__=='__main__':main()
