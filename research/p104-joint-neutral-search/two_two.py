"""Exact 2+2 ADD domain, deduplicating second-meeting response rows.

Every literal ADD sequence is represented. Probes are exact Q functionals;
passing probes triggers the complete coefficient and terminal-group tests.
"""
from joint import *

def run22(w,c,first,second,roles,second_frame,cap=50000000):
 snap=raw(w,c,{first,second});R1=snap[first][0];R2,ch=snap[second];g2=[r for r,f in enumerate(ch) if f==second_frame]
 need(len(g2)<=3,'second meeting bound');need(all(snap[first][1][r]==c['frame'] for r in roles),'first coframe')
 base,desired,*_=endpoints(w,c);groups=terminal_groups(w,c)
 bad=[f for f,rs in groups.items() if not groups_check(base,desired,{f:rs},[])];need(len(bad)==1 and len(groups[bad[0]])==1,'single critical endpoint frame')
 critical=groups[bad[0]][0];want=desired[critical]
 D1=responses(w,c['pivot'],first,roles);D2=responses(w,c['pivot'],second,g2);mid=responses(w,c['pivot'],first,roles,second)
 A=actions(roles);B=actions(g2);seq1=[()]+[(a,) for a in A]+[(a,b) for a in A for b in A];seq2=[()]+[(a,) for a in B]+[(a,b) for a in B for b in B]
 # Each K entry is an actual same-frame two-ADD endpoint correction matrix.
 matrices={}
 for seq in seq2:
  rows={r:{r:Q(1)} for r in g2}
  for r,s,a in seq:add(rows[r],rows[s],a)
  key=tuple(tuple(rows[r].get(s,0)-Q(r==s) for s in g2) for r in g2)
  matrices.setdefault(key,seq)
 effects=defaultdict(list)
 for matrix,seq in matrices.items():
  coeff=tuple(sum(D2[r].get(critical,0)*matrix[j][i] for j,r in enumerate(g2)) for i,s in enumerate(g2))
  effects[coeff].append((matrix,seq))
 probes=[c['pivot'],w['public']+w['owned_fields'],685,679,682,686]
 # First sequence provenance and integer multiplicities remain in seq counts.
 tested=0;probe_pass=0;row_pass=0;survivors=[];seen=set();first_unique=0
 for ix,seq in enumerate(seq1):
  loc={r:dict(R1[r]) for r in roles};up=[];rows2={r:dict(R2[r]) for r in g2};end=dict(base[critical])
  for r,s,a in seq:
   src=dict(loc[s]);add(loc[r],src,a);up.append((D1[r],src,a));add(end,src,a*D1[r].get(critical,0))
   for t in g2:add(rows2[t],src,a*mid[r].get(t,0))
  signature=(tuple(sorted(end.items())),tuple(tuple(sorted(rows2[r].items())) for r in g2),tuple((tuple(sorted(d.items())),tuple(sorted(s.items())),a) for d,s,a in up))
  # Do not dedup first paths: distinct endpoint updates outside the critical row matter.
  first_unique+=1
  for coeff,cases in effects.items():
   tested+=sum(1 for _ in cases)
   if tested>cap:raise ValueError('explicit unique-matrix resource cap exceeded')
   if any(end.get(j,0)+sum(a*rows2[r].get(j,0) for r,a in zip(g2,coeff)) for j in probes if j not in want):continue
   probe_pass+=len(cases);target=dict(end)
   for r,a in zip(g2,coeff):add(target,rows2[r],a)
   if set(target)!=set(want):continue
   pivot=min(want);ratio=target[pivot]/want[pivot]
   if not ratio or any(target[j]!=ratio*v for j,v in want.items()):continue
   row_pass+=len(cases)
   for matrix,seq2w in cases:
    updates=list(up)
    for j,r in enumerate(g2):
     source={}
     for i,s in enumerate(g2):add(source,rows2[s],matrix[j][i])
     if source:updates.append((D2[r],source,Q(1)))
    if groups_check(base,desired,groups,updates):
     survivors.append(dict(first=seq,second=seq2w));print('SURVIVOR',fmt(survivors[-1]),flush=True)
  if ix and ix%5000==0:print(dict(first_sequences=ix,total=len(seq1),survivors=len(survivors)),flush=True)
 return dict(first_sequences=len(seq1),second_sequences=len(seq2),literal_program_pairs=len(seq1)*len(seq2),second_distinct_matrices=len(matrices),second_critical_effects=len(effects),matrix_pairs=tested,probe_pass=probe_pass,critical_row_pass=row_pass,survivors=survivors,critical=critical,groups=[roles,g2])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--index',type=int,default=1196);ap.add_argument('--out',default='two-two680.json');a=ap.parse_args()
 w=retime(load('word5718.json.gz'),16655,16649);c=json.loads((HERE/'results/contacts5718.json').read_text())['cuts'][a.index]
 for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
 t=time.monotonic();out=run22(w,c,c['cut'],16652,[680,753,679,682,685,686],164);out.update(source_sha256=PINS['word5718.json.gz'],cut=c['cut'],pivot=c['pivot'],route=dict(move=16655,after=16649),seconds=time.monotonic()-t)
 (HERE/'results'/a.out).write_text(json.dumps(fmt(out),indent=2)+'\n');print(json.dumps(fmt(out)))
if __name__=='__main__':main()
