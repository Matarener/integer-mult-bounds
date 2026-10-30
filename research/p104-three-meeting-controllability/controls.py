"""Constructive positive and semantic rejection controls for the exact model."""
from obstruction import *

def reject(fn,label,contains=None):
 try:fn()
 except ValueError as e:
  need(contains is None or contains in str(e),'wrong rejection: '+label+': '+str(e))
  return dict(control=label,reason=str(e))
 raise ValueError('mutation accepted: '+label)

def run():
 w,c,ts,fs,snap,roles=case(1196,True)
 source=audit(load('word5718.json.gz'));retimed=audit(w)
 need(source==retimed,'route retiming preserves all endpoints, costs, frames and ownership')
 old=load('word5713.json.gz')
 pc=next(c for c in json.loads((HERE/'results/contacts5713.json').read_text())['cuts']
         if c['cut']==14330 and c['pivot']==708 and c['a']=={'708':'1','154':'1/2'})
 for k in ('a','c','h0','d','beta'):pc[k]=unrow(pc[k])
 positive=construct(old,pc);pos=audit(positive)
 need(pos['paid']==source['paid'] and pos['targets']==source['targets'],'known positive published recursive profile')
 rejected=[]
 rejected.append(reject(lambda:relaxation(w,c,[ts[1],ts[0],ts[2]],fs,snap,roles),'wrong meeting chronology','chronology'))
 badroles=deepcopy(roles);badroles[1].append(153)
 rejected.append(reject(lambda:relaxation(w,c,ts,fs,snap,badroles),'inaccessible source at intermediate meeting','source/frame'))
 badframes=list(fs);badframes[1]=164
 rejected.append(reject(lambda:relaxation(w,c,ts,badframes,snap,roles),'wrong intermediate frame','source/frame'))
 bad=deepcopy(positive);bad['program'].append(['ADD',old['public'],682,'1',127])
 rejected.append(reject(lambda:audit(bad),'independent new target changed at a legal frame','endpoint '+str(old['public'])))
 rejected.append(reject(lambda:retime(load('word5718.json.gz'),16655,15829),'route retiming across a write','role touch'))
 # A singular first map can fool the singleton-output condition. Its dropped
 # original e683 cannot be recovered anywhere, even after ignoring all frames.
 rows=[dict(z) for z in snap[ts[0]][0]]
 rows[683]=sumrows(rows,{682:Q(1),684:Q(1),686:Q(1)})
 localrank=len(basis(rows[r] for r in roles[0]));need(localrank==len(roles[0])-1,'singular first map')
 walk(w,c,rows,ts[0],ts[1]);rows[753]=dict(rows[479])
 walk(w,c,rows,ts[1],len(w['program'])-1)
 desired=endpoints(w,c)[1]
 need(rows[153]==desired[153],'rank-loss fake passes singleton153')
 missing=project({683:Q(1)},basis(rows));need(bool(missing),'rank-loss fake loses independent target683')
 # Nonlinear temporal cross terms must use the actually changed second state.
 literal=[dict(z) for z in snap[ts[0]][0]]
 add(literal[753],literal[685],Q(1))
 walk(w,c,literal,ts[0],ts[1]);changed=dict(literal[753]);stale=snap[ts[1]][0][753]
 need(changed!=stale,'second source really changed')
 want=dict(stale);add(want,snap[ts[0]][0][685],Q(1))
 need(changed==want,'changed temporal source exact all coefficients')
 need(changed!=stale,'stale-state rejection')
 # Canonical quotient must remain linear even with a missing low pivot.
 qb=basis([{2:Q(1),3:Q(1)}]);a={1:Q(1),2:Q(1)};b={1:Q(-1)}
 lhs=dict(a);add(lhs,b);lhs=project(lhs,qb);rhs=project(a,qb);add(rhs,project(b,qb))
 need(lhs==rhs,'linear quotient control')
 # Literal changed-state replay independently checks the universal endpoint
 # identity with several noncommuting dyadic shears at each actual meeting.
 imports=[]
 for idx in (1196,1199,1200):
  ww,cc,tt,ff,ss,rr=case(idx,True);cert=certify(idx,True)
  literal=[dict(z) for z in ss[tt[0]][0]]
  for a,b in zip(rr[0],rr[0][1:]):add(literal[a],literal[b],Q(-1,2))
  X=sumrows(literal,cert['X']);L=sumrows(literal,cert['L'])
  walk(ww,cc,literal,tt[0],tt[1]);A=dict(literal[479])
  add(literal[753],literal[479],Q(2));add(literal[527],literal[753],Q(-1,2));add(literal[753],literal[527],Q(1))
  Qrow=dict(literal[753]);walk(ww,cc,literal,tt[1],tt[2])
  before=[dict(z) for z in literal]
  add(literal[153],literal[685],Q(1));add(literal[685],literal[753],Q(-1,2));add(literal[753],literal[153],Q(2))
  predicted=dict(cert['target153']);add(predicted,X);add(predicted,L,-1);add(predicted,A,-1);add(predicted,Qrow)
  for r,d in responses(ww,680,tt[2],rr[2]).items():
   delta=dict(literal[r]);add(delta,before[r],-1);add(predicted,delta,d.get(153,Q(0)))
  walk(ww,cc,literal,tt[2],len(ww['program'])-1)
  need(predicted==literal[153],'three-meeting literal changed-state identity')
  imports.append(idx)
 return dict(status='PASS',source=source,retimed=retimed,known_positive=pos,
             rejection_controls=rejected,rank_loss_control=dict(first_rank=localrank,
             output153_passes=True,independent_target683_missing=missing),
             changed_second_source_all_coefficients=True,linear_quotient=True,
             literal_three_meeting_identity_all_columns=imports)

if __name__=='__main__':
 out=run();(ROOT/'results/controls.json').write_text(json.dumps(fmt(out),indent=2)+'\n');print(json.dumps(fmt(out)))
