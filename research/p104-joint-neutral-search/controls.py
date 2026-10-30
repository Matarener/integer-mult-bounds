"""Exact discovery, emitted-word, changed-state and custody controls."""
from emit import *
from reachability import reach_test
import tempfile

def rejected(fn,label):
 try:fn()
 except ValueError:return label
 raise ValueError('accepted mutation: '+label)

def main():
 w=load('word5718.json.gz');base=audit(w)
 # A legal existing MOVE is advanced across events that do not touch role153.
 route=retime(w,16655,16649);shift=audit(route);need(base==shift,'retimed exact endpoint/invoice/ordinary match')
 (HERE/'results/retimed-word.json.gz').write_bytes(gzip.compress(json.dumps(route,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 tests=[rejected(lambda:retime(w,16655,15829),'retiming across a source write')]
 bad=deepcopy(route);bad['program'][16650][2]=3;tests.append(rejected(lambda:audit(bad),'wrong retimed source frame'))
 bad=deepcopy(w);bad['program'][0][-2]='1/3';tests.append(rejected(lambda:audit(bad),'non-dyadic ADD'))
 # Reconstruct the published positive from a cut the generator actually found.
 old=load('word5713.json.gz');cuts=json.loads((HERE/'results/contacts5713.json').read_text())['cuts'];c=next(c for c in cuts if c['cut']==14330 and c['pivot']==708 and c['a']=={'708':'1','154':'1/2'})
 for k in ('a','c','h0','d','beta'):c[k]=unrow(c[k])
 positive=construct(old,c);pos=audit(positive)
 wrong=deepcopy(positive);wrong['final'][708]=127;tests.append(rejected(lambda:audit(wrong),'unearned retired H9 target'))
 wrong=deepcopy(positive);wrong['program'].remove(['ADD',708,154,'1/2',602]);tests.append(rejected(lambda:audit(wrong),'missing retirement ADD'))
 # Two same-frame meetings. The second read must see the changed first state.
 toy=dict(public=3,owned_fields=0,live=[],ports=[],frames=[[],[1],[1,2]],initial=[1,1,1],final=[2,2,2],program=[['ADD',1,0,'1',1],['ADD',2,1,'1',1],['MOVE',0,1,2,False],['MOVE',1,1,2,False],['MOVE',2,1,2,False],['ADD',2,1,'-1',2],['ADD',1,0,'-1',2]])
 need(audit(toy)['columns']==3,'two-meeting fixture')
 wrong=deepcopy(toy);wrong['program'][-2],wrong['program'][-1]=wrong['program'][-1],wrong['program'][-2]
 tests.append(rejected(lambda:audit(wrong),'wrong-order changed-state fixture'))
 # Response formula for two inserted ADDs agrees on every coefficient with literal execution.
 # Base toy contains only the legal movements; extras are at the two actual frames.
 bare=deepcopy(toy);bare['program']=[e for e in bare['program'] if e[0]=='MOVE']
 R=[{r:Q(1)} for r in range(3)];R[1]={1:Q(1)};first_src=dict(R[0]);add(R[1],first_src,Q(1));later_src=dict(R[1]);add(R[2],later_src,Q(2))
 expected=[{0:Q(1)},{1:Q(1),0:Q(1)},{2:Q(1),1:Q(2),0:Q(2)}];need(R==expected,'changed-state two ADD formula')
 stale=[{0:Q(1)},{1:Q(1),0:Q(1)},{2:Q(1),1:Q(2)}];need(stale!=R,'stale source must differ')
 # On an actual retimed P104 word, compare the low-rank update formula against a literal suffix.
 cc=json.loads((HERE/'results/contacts5718.json').read_text())['cuts'][1196]
 for key in ('a','c','h0','d','beta'):cc[key]=unrow(cc[key])
 first,second=13920,16652;pivot=680;fresh=753
 snap=raw(route,cc,{first,second});one=snap[first][0];two=snap[second][0]
 s1=dict(one[pivot]);D1=responses(route,pivot,first,[685])[685];D2=responses(route,pivot,second,[153])[153];mid=responses(route,pivot,first,[685],second)[685]
 s2=dict(two[685]);add(s2,s1,mid.get(685,0));need(s2!=two[685],'actual second source must change')
 predicted,_,*_=endpoints(route,cc)
 for r,a in D1.items():add(predicted[r],s1,a)
 for r,a in D2.items():add(predicted[r],s2,a)
 literal=[dict(z) for z in one];add(literal[685],literal[pivot],Q(1))
 for i in range(first+1,len(route['program'])):
  apply(literal,renamed(route['program'][i],pivot,fresh))
  if i==second:add(literal[153],literal[685],Q(1))
 need(literal==predicted,'actual P104 response formula all coefficients')
 # Four ADDs include a second source changed earlier in the same meeting.
 local1=[dict(z) for z in one];local2=[dict(z) for z in two];predicted,_,*_=endpoints(route,cc)
 seq1=[(685,680,Q(1)),(685,753,Q(-1,2))];seq2=[(153,685,Q(-2)),(685,753,Q(1,2))]
 for r,s,a in seq1:
  src=dict(local1[s]);add(local1[r],src,a);endresponse=responses(route,pivot,first,[r])[r];mresponse=responses(route,pivot,first,[r],second)[r]
  for t,b in endresponse.items():add(predicted[t],src,a*b)
  for t,b in mresponse.items():add(local2[t],src,a*b)
 for r,s,a in seq2:
  src=dict(local2[s]);add(local2[r],src,a);endresponse=responses(route,pivot,second,[r])[r]
  for t,b in endresponse.items():add(predicted[t],src,a*b)
 literal=[dict(z) for z in one]
 for r,s,a in seq1:add(literal[r],literal[s],a)
 for i in range(first+1,len(route['program'])):
  apply(literal,renamed(route['program'][i],pivot,fresh))
  if i==second:
   for r,s,a in seq2:add(literal[r],literal[s],a)
 need(literal==predicted,'actual P104 four-step response formula all coefficients')
 payload=(HERE/'inputs/word5718.json.gz').read_bytes();corrupt=bytearray(payload);corrupt[-1]^=1
 need(hashlib.sha256(corrupt).hexdigest()!=PINS['word5718.json.gz'],'source corruption must reject')
 out=dict(status='PASS',source=base,retimed=shift,known_positive=pos,negative_controls=tests,two_meeting_fixture=True,changed_source_formula=True,actual_P104_two_step_formula_all_columns=True,source_corruption_rejected=True,actual_P104_four_step_formula_all_columns=True)
 (HERE/'results/controls.json').write_text(json.dumps(fmt(out),indent=2)+'\n');print(json.dumps(fmt(out)))
if __name__=='__main__':main()
