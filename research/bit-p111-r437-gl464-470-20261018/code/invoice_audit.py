"""Independent fixed WORD lowering, actual hosted descriptors and finite invoice."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import json,gzip,struct,hashlib,time,ctypes
import sys
H=Path(sys.argv[1]).resolve();I=H
HOST_EXPECTED=json.loads((Path(__file__).resolve().parents[1]/'EXPECTED.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda n:json.loads((I/n).read_bytes())
word=lambda n:json.loads(gzip.decompress((I/n).read_bytes()))
def save(n,obj):
 with (H/n).open('x',encoding='utf8') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def peak():
 if sys.platform!='win32':
  try:
   import resource
   amount=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
   return amount if sys.platform=='darwin' else amount*1024
  except ImportError:return None
 class M(ctypes.Structure):_fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
 m=M();m.cb=ctypes.sizeof(m)
 ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
 proc=ctypes.windll.kernel32.GetCurrentProcess()
 fn=ctypes.windll.psapi.GetProcessMemoryInfo;fn.argtypes=[ctypes.c_void_p,ctypes.POINTER(M),ctypes.c_ulong]
 assert fn(proc,ctypes.byref(m),m.cb)
 return m.PeakWorkingSetSize

def local():
 w=word('WORD.json.gz');assert hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='da77deaf11368d016622348227657b98404b6afbc7e4f3d6fe9a246baae0dcce'
 f=load('records/frames.json')['frames'];dims=[f[str(j)]['dim'] for j in range(636)]
 # Check provided basis/annihilator orthogonality and exact dimensions against
 # the earlier independently computed frame geometry, not a scalar receipt.
 for j,z in f.items():
  assert len(z['B'])==z['dim'] and len(z['A'])+len(z['B'])==8
  assert all(sum(x*y for x,y in zip(a,b))==0 for a in z['A'] for b in z['B'])
 v=111;n=659;cur=w['start'][:];r=[]
 def mov(role,new):
  old=cur[role]
  if old!=new:
   assert set(w['frames'][old])<=set(w['frames'][new]) and dims[new]>dims[old]
   r.append((0,role,old,new,dims[new]-dims[old],0));cur[role]=new
 for phase,sec in ((1,'D'),(2,'A'),(4,'B'),(5,'C')):
  if sec=='B':
   for j,src in enumerate(w['ret']):
    f0=cur[src];r.append((2,src,n,f0,0,dims[f0]))
    r.extend((1,v+t,n,1,0,3) for t,js in enumerate(w['scatter']) if j in js)
    r.append((3,src,n,f0,0,0))
  for frame,d,ss in w[sec]:
   for role in [d]+ss:mov(role,frame)
   r.extend((1,d,s,1,frame,phase) for s in ss)
 for role,frame in enumerate(w['final']):mov(role,frame)
 actual=list(struct.iter_unpack('<6i',(I/'records/249-records.bin').read_bytes()))
 assert r==actual
 state=load('records/249-states.json');assert state['n']==n and state['v']==v and state['R']==437
 assert [state['initial'][str(i)] for i in range(n)]==w['start']
 assert [state['final'][str(i)] for i in range(n)]==w['final']
 assert state['retained_totals']==w['ret']
 streams={};details={}
 for rev in (False,True):
  norm=[1]*n+[0];maxl1=1;opened=None;val=[1<<i for i in range(n)]+[0];h=Counter();events=[];adds=0
  for op,d,s,c,f,z in (reversed(r) if rev else r):
   if op==0:
    old,new=(c,s) if rev else (s,c);h[f]+=int(f>0);events.append([0,d,old,new,f,int(rev)])
   elif op==1:
    assert d!=opened and (s!=n or opened is not None)
    val[d]^=val[s];norm[d]+=abs(c)*norm[s];maxl1=max(maxl1,norm[d]);adds+=1
    events.append([1,d,s,-c if rev else c,f,int(rev)])
   elif op==(3 if rev else 2):
    assert opened is None and val[n]==0;opened=d;val[n]=val[d];norm[n]=norm[d]
    rank=abs(dims[c]-dims[f]);h[rank]+=1;events.append([2,d,n,c,f,rank,int(rev)])
   else:
    assert opened==d and val[n]==val[d];val[n]^=val[d];norm[n]=0;opened=None
    events.append([3,d,n,c,f,z,int(rev)])
  assert opened is None and val[n]==0
  assert val[:n]==[(1<<j)^((1<<(j-v)) if v<=j<2*v else 0) for j in range(n)]
  key='reverse' if rev else 'forward';streams[key]=events
  details[key]={'records':len(r),'adds':adds,'l1':maxl1,'profile':dict(sorted(h.items())),
   'stream_sha256':hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()}
 assert len(r)==27132 and details['forward']['adds']==24208
 assert details['forward']['l1']==49347 and details['reverse']['l1']==1113998
 assert details['forward']['profile']==details['reverse']['profile']
 return streams,details

def host(streams,details):
 packed=(I/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes();blob=gzip.decompress(packed)
 assert hashlib.sha256(blob).hexdigest()==HOST_EXPECTED['template_content_sha256']
 t=json.loads(blob);del blob,packed
 g=load('hosted/GLOBAL.json');pg=load('nine/GLOBAL.json');geo=load('nine/GEOMETRY.json')
 assert t['local_programs']==streams
 assert t['m']==64 and t['live']==28416 and t['stages']==9 and t['replicas']==32
 assert t['private_centre_reserve']==9 and not any(t['banks_per_stage'].values())
 assert g['geometry_sha256']==sha(I/'nine/GEOMETRY.json')==pg['geometry_sha256']
 for key,z in details.items():
  p=pg['local_checks'][key]
  assert p['sha256']==z['stream_sha256'] and p['adds']==z['adds'] and p['cancellation_free_row_l1']==z['l1']
 windows={};last={};local_positions=[]
 for pos,e in enumerate(t['schedule']):
  kind=e['kind']
  if kind=='local_cover_sweep':local_positions.append((pos,e['stage'],e['pair']));last[e['pair']]=pos
  elif kind=='bridge':last[e['dst']]=pos;last[e['src']]=pos
  elif kind=='idle':
   stages={s for q,s,p in local_positions if last.get(e['pair'],-1)<q<pos and p!=e['pair']}
   windows[e['idx']]=(e['pair'],e['rank'],stages)
  else:assert kind=='exchange'
 assert t['hosting']['windows']=={str(i):[p,r,sorted(s)] for i,(p,r,s) in windows.items() if r and s}
 occupied=defaultdict(int);assigned={}
 for i,cp,off,width,stage,helper in t['hosting']['slots']:
  p,r,eligible=windows[i]
  assert stage in eligible and 0<=cp<222 and width==8 and 0<=helper<437 and off>=0 and off+8<=r
  assert (stage,helper) not in assigned
  bits=((1<<8)-1)<<off;assert not occupied[i,cp]&bits;occupied[i,cp]|=bits
  assigned[stage,helper]=(i,cp,off,width)
 assert len(assigned)==9*437==3933
 remainder=Counter();perwindow={}
 for i,(p,r,eligible) in windows.items():
  if not r:continue
  counts=Counter()
  for cp in range(222):
   used=occupied[i,cp];remain=((1<<r)-1)^used
   # Crucial concrete tariff: remaining coordinates form ONE contiguous run.
   count=remain.bit_count();start=(remain&-remain).bit_length()-1 if remain else 0
   assert not remain or remain==((1<<count)-1)<<start
   counts[count]+=1
   if count:remainder[count]+=32
  perwindow[i]=dict(sorted(counts.items()))
  if str(i) in t['hosting']['windows']:
   assert {str(k):n for k,n in counts.items()}==t['hosting']['remainders'][str(i)]
 paid=Counter({k:n*288 for k,n in details['forward']['profile'].items()});paid.update(remainder)
 assert dict(sorted(paid.items()))=={int(k):n for k,n in g['profile'].items()}
 assert sum(k*n for k,n in paid.items())==1808352 and 64*28416-1808352==10272
 # Independent source-bound owner/digest construction using pre-serialized
 # invariant suffixes; avoids materializing 7.8 million mapped instructions.
 cache={}
 for key,events in streams.items():
  cache[key]=[(z[0],z[1],None if z[0]==0 else z[2],
    (','+','.join(str(x) for x in z[2 if z[0]==0 else 3:])+']\n').encode()) for z in events]
 digest=hashlib.sha256();events=0;seen=set();owned=0
 for c in t['calls']:
  s,rep,p=c['stage'],c['replica'],c['pair'];assert (s,rep) not in seen;seen.add((s,rep))
  own=c['owners'];assert len(own)==659 and c['orientation']==('reverse' if s%2 else 'forward')
  for r in range(222):
   side=r//111
   if c['orientation']=='reverse':side=1-side
   assert own[r]==[rep*888+(2*p+side)*111+r%111,['data',s,r%111]]
  for h in range(437):
   i,cp,off,w=assigned[s,h];pair,_,_=windows[i];side,port=divmod(cp,111)
   assert own[222+h]==[rep*888+(2*pair+side)*111+port,['hosted',i,off,w]]
   assert pair!=p;owned+=1
  owners=[json.dumps(x,separators=(',',':')).encode() for x in own]+[b'[28416,["private",0]]']
  buf=bytearray()
  for op,d,src,suffix in cache[c['orientation']]:
   buf.extend(b'['+str(op).encode()+b','+owners[d])
   if src is not None:buf.extend(b','+owners[src])
   buf.extend(suffix)
  digest.update(buf);events+=len(cache[c['orientation']])
 assert len(seen)==288 and owned==125856 and events==7814016
 assert digest.hexdigest()==g['emitted_program_sha256']==HOST_EXPECTED['program_sha256']
 return g,pg,geo,paid,{'template_content_sha256':g['template_sha256'],'program_sha256':digest.hexdigest(),
  'events':events,'owner_occurrences':owned,'helper_per_replica':len(assigned),'idle_remainders':perwindow,
  'all_remaining_idle_axes_single_contiguous_run':True,'additional_positive_rank_children':0,'paid_profile':dict(sorted(paid.items()))}

@lru_cache(None)
def log_bounds(num,den=1):
 k=0;a=Q(num,den)
 while a>=2:a/=2;k+=1
 z=(a-1)/(a+1)
 def atanh(z):
  total=Q(0);term=z
  for j in range(40):total+=2*term/(2*j+1);term*=z*z
  return total,total+2*term/(81*(1-z*z))
 lo,hi=atanh(z);l2,h2=atanh(Q(1,3));return lo+k*l2,hi+k*h2
def exp_bounds(lo,hi):
 def series(x):
  total=term=Q(1)
  for j in range(1,19):term=term*x/j;total+=term
  nextterm=term*x/19
  return total,total+nextterm/(1-x/20)
 return series(lo)[0],series(hi)[1]
def price(p,c):
 low=high=Q(0);E=sum(p.values())
 pp=dict(p);pp[1]=pp.get(1,0)+Q(32*64*64*E,10**16)
 for r,n in pp.items():
  ll,hh=log_bounds(64,r);lo,hi=exp_bounds(c*ll,c*hh);factor=Q(n*r,64*28416)
  low+=factor*lo;high+=factor*hi
 return low,high

def main():
 start=time.process_time();streams,details=local();g,pg,geo,p,hosted=host(streams,details)
 m=64;W=28416;physical=W+9;R=437;V=111;T=32;L=9;K=4;DEPTH=2;E=sum(p.values());d=m*m;N=2*m
 assert 2*max(p)**DEPTH<m**DEPTH and W+9<2**80
 prefix=2**18*details['forward']['l1']**5*details['reverse']['l1']**4
 assert prefix==int(pg['global_prefix_bound'])==int(g['global_prefix_bound'])
 unit=L*T*details['forward']['adds']+6*(K-1)*V*T
 J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*L*T*R+2*(9*L*T)
 high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3
 selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+144+2+(m-1)+m))
 components={'unit':unit,'J_times_high':J*high,'J_times_physical':J*physical,'E_times_good':E*good,
  'E_times_compiler':E*compiler,'matrix_test':16*m**3,'copy_erase_episodes':9*L*T,
  'selectors':selectors,'prefix':prefix,'one':1}
 coefficient=sum(components.values());two=(coefficient+1)**DEPTH*(E+1)**DEPTH
 row=DEPTH*(m*m+1)+9909+252
 assert prefix.bit_length()==coefficient.bit_length()==177 and two.bit_length()==393 and row==18355<20161
 assert two<2**512 and prefix<2**192
 exactfallback=6*N*(N-1)+3*N+6*(N-1);fb=32*m*m*E
 assert exactfallback==98682<32*m*m==131072
 author=load('ASSEMBLY-BIT-AND-HISTORICAL-CONTROL.json');c=Q(author['bit_lower']);nextc=Q(author['next_grid_point_rejected'])
 assert nextc-c==Q(1,10**24)
 prices=[]
 for name,x in [('candidate',c),('next_grid',nextc),('selected_plus_point1percent',Q(1733427039589844234749,10**24)*Q(1001,1000)),('governing_1043_plus_point1percent',Q(1734176288479865766692,10**24)*Q(1001,1000)),('pending_2423_plus_point1percent',Q(1734846264120199151475,10**24)*Q(1001,1000))]:
  lo,hi=price(p,x)
  scale=10**60
  lo=Q((lo.numerator*scale)//lo.denominator,scale)
  hi=Q(-((-hi.numerator*scale)//hi.denominator),scale)
  assert (hi<1) if name!='next_grid' else (lo>1)
  prices.append({'test':name,'c':str(x),'lower':str(lo),'upper':str(hi),'moment_lower_float':float(lo),'moment_upper_float':float(hi),
   'strict_margin_lower':str(1-hi) if hi<1 else None,'strict_excess_lower':str(lo-1) if lo>1 else None})
 for key,val in [('prefix_bits',177),('charged_prefix_bits',192),('coefficient_bits',177),('two_level_coefficient_bits',393),('charged_two_level_coefficient_bits',512),('row_coefficient',18355),('halving_depth',2)]:assert author['bit'][key]==val
 selected=Q(1733427039589844234749,10**24)
 result={'status':'PASS_SAME_WORD_RECORD_HOST_DESCRIPTOR_INVOICE_AND_INDEPENDENT_PRICE',
  'local':details,'records_sha256':sha(I/'records/249-records.bin'),'hosted':hosted,
  'invoice':{'m':m,'W':W,'physical':physical,'V':V,'R':R,'DEPTH':DEPTH,'E':E,'J':J,
   'route_factors':geo['max_route_factors'],'components':{k:str(v) for k,v in components.items()},'coefficient':str(coefficient),
   'coefficient_bits':coefficient.bit_length(),'prefix_bits':prefix.bit_length(),'charged_prefix_bits':192,
   'two_level_coefficient':str(two),'two_level_bits':two.bit_length(),'charged_two_level_bits':512,
   'row_coefficient':row,'retained_ROW_limit':20161,'old_coarse_ROW_reserve':9909,'old_leaf_ROW_reserve':252,
   'maximum_child':max(p),'halving_integer_pair':[2*max(p)**2,m*m],
   'bad_fraction':'1/10000000000000000','fallback_exact_primitive_bound':exactfallback,'fallback_overcharge_per_edge':32*m*m,'fallback_total':fb},
  'price':{'independent_method':'Rational atanh log bounds with explicit tail, then rational Taylor exp bounds with explicit tail. All32m²E bad-class children retained.',
   'candidate_c':str(c),'candidate_decimal':author['bit_lower_decimal'],'next_grid':str(nextc),'checks':prices,
   'relative_selected_gain':str(c/selected-1),'relative_selected_gain_percent':float(100*(c/selected-1))},
  'binding':'Same WORD -> independent regenerated binary records -> exact local streams -> all125856 owner descriptors -> hashed7814016-event actual program -> full profile/invoice.',
  'scope':'Inherited selected SOURCE/common-field/all-size compiler contract is unchanged. Concrete record/owner/restored-idle descriptor guards are checked here; broad generic physical all-size theorem is not newly required or claimed.',
  'final_manifest_rebind':'PENDING author frozen manifest; accepted stable paths and actual content/program hashes are fixed in INTAKE.',
  'historical_outer_pr548_ignored':True,'new_whole_kappa':False,'manager_release_decision':False,'CPU_seconds':time.process_time()-start,'peak_working_set_bytes':peak()}
 save('INVOICE-INDEPENDENT.json',result)
 print(json.dumps({'status':result['status'],'invoice':{'prefix':177,'two_level':393,'ROW':row},'candidate_c':str(c),'gain_percent':result['price']['relative_selected_gain_percent'],'CPU_seconds':result['CPU_seconds'],'peak_bytes':result['peak_working_set_bytes']}))
if __name__=='__main__':main()
