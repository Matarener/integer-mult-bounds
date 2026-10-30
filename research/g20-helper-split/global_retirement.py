"""Install the G20 helper split in all eighteen physical calls.

Adapted from PR5671 and ai-nanachi PR5512. All retained source, controller
and Dugongue credit remains in prior/. Ali Romman with substantial OpenAI
Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
from time import process_time
import gzip,json,importlib.util,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import integration as L
R=L.R;S=L.S
def need(c,m):
 if not c:raise ValueError(m)
def read(p):return L.read(p)
def put(n,x):L.put(n,x)
def run():
 clock=process_time();controller=read(S/'inputs/CONTROLLER.json');base,frames,_=L.source();local=read(R/'WORD.json.gz');owned=local['owned'];pivots=sorted(x for x in owned if x<658);need(pivots==sorted(L.RETIRED),'Exact twenty-two retired helper owners')
 oldcalls=read(S/'provider/data/CALLS.json');retired={c['helper_owner_begin']+p-222 for c in oldcalls for p in pivots};retained=[i for i in range(11400)if i not in retired];compact={x:i for i,x in enumerate(retained)};N=len(retained)+18;W=list(range(N,N+len(owned)));center,shadow=W[:2];pivotwork=dict(zip(pivots,W[2:2+len(pivots)]));snapshotwork=dict(zip(sorted(r for r in owned if r>=660),W[2+len(pivots):]));need(N==11022,'Independent successor inputs included')
 values=[1<<i for i in range(N+len(owned))];norm=[1]*(N+len(owned));versions=[0]*(N+len(owned));epochs=[0]*(N+len(owned));counts=Counter();paid=Counter();peak=1;events=[];source=[];calls=[];episodes=[];prefix=sha256()
 def emit(e):counts[e[0]]+=1;events.append(e);prefix.update((json.dumps(e,separators=(',',':'))+'\n').encode())
 def erase(d,why,frame=None):
  need(d in W,'Only owned wholepayload erasure');values[d]=norm[d]=0;versions[d]+=1;epochs[d]+=1;emit(['OWNED_CLEAR',d,frame,why])
 for d in W:erase(d,'GLOBAL_ENTRY_ARBITRARY_DIRTY')
 def add(d,s,why):
  nonlocal peak
  need(d!=s,'Distinct source/destination');values[d]^=values[s];norm[d]+=norm[s];peak=max(peak,norm[d]);versions[d]+=1;emit(['ADD',d,s,why])
 def query(d,k,detail):
  need(k>0,'Positive rank');source.append({'event':len(events),'prefix_sha256':prefix.hexdigest(),'owner':d,'version':versions[d],'epoch':epochs[d],'rank':k,'detail':detail,'RAW_hex':hex(values[d]),'function_identity':'Exact literal program prefix plus current owner/epoch/version and actual geometric source job; RAW bitmap is extra evidence, not a claim of purity.'});paid[k]+=1;versions[d]+=1;emit(['QUERY',d,k,detail])
 def swap(d,s,why):add(d,s,why);add(s,d,why);add(d,s,why)
 def boundary(program,why):
  for op,d,s in program:
   for p in range(111):
    if op=='ADD':add(compact[d*111+p],compact[s*111+p],why)
    else:need(op=='SWAP','Controller opcode');swap(compact[d*111+p],compact[s*111+p],why)
 boundary(controller['boundaries']['right_program'],'RIGHT_BOUNDARY')
 thick=controller['invoice']['thick_stages'];stage_index={s:i for i,s in enumerate(thick)}
 for event in controller['physical_events']:
  op=event[0]
  if op=='LOCAL':
   _,stage,pair,rev=event;x,y=2*pair,2*pair+1
   if rev:x,y=y,x
   helper=3552+436*stage_index[stage]
   def owner(r):
    if r==684:return 11004+stage_index[stage]
    if r==658:return center
    if r==659:return shadow
    if r in pivotwork:return pivotwork[r]
    if r in snapshotwork:return snapshotwork[r]
    return compact[(x if r<111 else y)*111+r%111]if r<222 else compact[helper+r-222]
   sx=[values[owner(i)]for i in range(111)];sy=[values[owner(111+i)]for i in range(111)];helpers=[r for r in range(222,658)if r not in pivotwork]+[684];before={r:values[owner(r)]for r in helpers}
   if stage:
    for bank in(x,y):
     for p in range(111):emit(['PAID_PORT_ROUTE',stage,compact[bank*111+p],p,'ENTRY'])
   start=len(events);lp=Counter();st=local['start'][:];livebegin={}
   for ix,e in enumerate(local['records']):
    typ,d=e[:2];gd=owner(d)
    if typ=='ERASE':
     erase(gd,['LOCAL',stage,ix],e[2]);st[d]=e[2]
     if gd in livebegin:episodes.append({'owner':gd,'stage':stage,'begin':livebegin.pop(gd),'end':len(events)-1})
    elif typ=='INIT':need(values[gd]==0,'Whole zero INIT');st[d]=e[2];emit(['OWNED_ZERO_HEADER',gd,e[2],stage])
    elif typ=='ADD':
     s,f=e[2:];need(st[d]==st[s]==f,'Actual instantiated coframe')
     if gd in W and gd not in livebegin:livebegin[gd]=len(events)
     add(gd,owner(s),['LOCAL',stage,f,ix])
    elif typ in('Q','ZERO_Q'):
     a,b,k=e[2:];need(st[d]==a,'Current instantiated query frame');st[d]=b
     if typ=='Q':query(gd,k,['LOCAL_INVERSE',stage,a,b,ix]);lp[k]+=1
     else:need(values[gd]==0,'Zero only free query');emit(['WHOLE_ZERO_FRAME',gd,a,b,k,stage])
    else:raise ValueError('Local opcode '+typ)
   need(not livebegin and st==local['final'],'No live local owned state at return')
   need(all(values[owner(i)]==sx[i]and values[owner(111+i)]==sy[i]^sx[i]for i in range(111)),'All retained main RAW inputs')
   need(all(values[owner(r)]==before[r]for r in helpers)and all(values[w]==0 for w in W),'All415 independent retained helper inputs and48owned returns')
   need(lp==Counter(read(R/'LOCAL-RESULT.json')['stats']['paid'])or lp==Counter({int(k):v for k,v in read(R/'LOCAL-RESULT.json')['stats']['paid'].items()}),'Actual local query count')
   calls.append({'stage':stage,'pair':pair,'source_bank':x,'target_bank':y,'old_direction_inverse':rev,'new_direction_inverse':True,'helper_old_owner_begin':helper,'core_begin':start,'core_end':len(events),'owned_global_indices':W,'retained_helper_count':415,'paid':dict(lp)})
   if stage:
    for bank in(x,y):
     for p in range(111):emit(['PAID_PORT_ROUTE',stage,compact[bank*111+p],p,'RETURN'])
  elif op=='QUERY_SHEAR':
   _,stage,pair,rev=event;x,y=2*pair,2*pair+1
   if rev:x,y=y,x
   for p in range(111):
    src,dst=compact[x*111+p],compact[y*111+p];need(values[center]==0,'Clean thin scratch');v=versions[src];begin=len(events);add(center,src,['THIN_COPY',stage,p]);query(center,1,['THIN',stage,p]);add(dst,center,['THIN_DELIVER',stage,p]);need(versions[src]==v,'Thin immutable SOURCE');erase(center,['THIN',stage,p]);episodes.append({'owner':center,'stage':stage,'kind':'THIN','begin':begin,'end':len(events)-1})
  elif op=='IDLE':
   _,pair,stages=event;k=7*len(stages)
   for bank in(2*pair,2*pair+1):
    for p in range(111):query(compact[bank*111+p],k,['WHOLE_IDLE',stages,p])
  elif op=='ADD':
   for p in range(111):add(compact[event[1]*111+p],compact[event[2]*111+p],'BRIDGE')
  else:
   need(op=='SWAP','Known controller event')
   for p in range(111):swap(compact[event[1]*111+p],compact[event[2]*111+p],'FINAL_SWAP')
 boundary(controller['boundaries']['left_program'],'LEFT_BOUNDARY')
 for d in W:erase(d,'GLOBAL_EXIT_TEARDOWN')
 need(values==[1<<i for i in range(N)]+[0]*len(owned),'All11022 independent retained RAW and all48 arbitrary DIRTY entry columns annihilated')
 oldtargets=read(S/'provider/data/TARGET-OWNERS.json');targets=[dict(t,original_owner=compact[t['original_owner']])for t in oldtargets if t['original_owner']not in retired]
 for si,call in enumerate(oldcalls):
  owner465=compact[call['helper_owner_begin']+465-222]
  target=next(t for t in targets if t['original_owner']==owner465);need(target['rank']==8,'One whole old helper target');target.pop('native_frame');target.update(rank=4,split='full8_to_frame508',native_source_frame=1,native_target_frame=508,matcher='FRAME508_COMPLEMENT',route_pair_required_in_generic_job_matching=True)
  targets.append({'original_owner':11004+si,'rank':4,'split':'frame508_to_zero','stage':call['stage'],'native_source_frame':508,'native_target_frame':0,'matcher':'FRAME508','route_pair_required_in_generic_job_matching':True})
 T=Counter(t['rank']for t in targets)
 P={int(k):v for k,v in read(S/'provider/data/INVOICE.json')['paid'].items()};raw_local=Counter(e[4] for e in L.source()[2] if e[0] in ('Q','COPY'));new_local=Counter({int(k):v for k,v in read(R/'LOCAL-RESULT.json')['stats']['paid'].items()})
 for k in set(raw_local)|set(new_local):P[k]=P.get(k,0)+18*(new_local[k]-raw_local[k])
 P={k:v for k,v in P.items() if v}
 need(paid==P and sum(T.values())==N and T[4]==36 and T[8]==7434,'Literal complete changed invoice including every partial helper')
 # Retained exact physical MAIN polynomial proof, independent of the new ledger.
 spec=importlib.util.spec_from_file_location('old_global',S/'provider/build_global.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);physical=mod.physical_main(controller)
 stream=b''.join((json.dumps(e,separators=(',',':'))+'\n').encode()for e in events);need(sha256(stream).hexdigest()==prefix.hexdigest(),'Exact prefix and fullstream identity');(R/'GLOBAL.jsonl.gz').write_bytes(gzip.compress(stream,mtime=0))
 invoice={'paid':dict(sorted(paid.items())),'targets':dict(sorted(T.items())),'originals':N,'owned_allocated':len(owned),'owned_output_credit':0,'QUERYs':sum(paid.values()),'rank_surplus':sum(k*v for k,v in T.items())-sum(k*v for k,v in paid.items())}
 result={'status':'PASS_LITERAL_G20_HELPER_SPLIT_11022_RETAINED_RAW','invoice':invoice,'expanded_event_count':len(events),'canonical_stream_sha256':sha256(stream).hexdigest(),'operation_counts':dict(counts),'calls':len(calls),'owned_payload_episodes':len(episodes),'source_descriptors':len(source),'majorant_bits':peak.bit_length(),'majorant':str(peak),'retired_original_old_ids':sorted(retired),'retained_old_ids':retained,'shared_owned_ids':W,'CPU_seconds':process_time()-clock,'physical_MAIN_coefficients':physical}
 put('GLOBAL-RESULT.json',result);put('INVOICE.json',invoice);put('CALLS.json',calls);put('PRIVATE-EPISODES.json',episodes);put('TARGET-OWNERS.json',targets);put('SOURCE-DESCRIPTORS.json.gz',source)
 return {k:result[k]for k in('status','invoice','expanded_event_count','canonical_stream_sha256','operation_counts','majorant_bits','owned_payload_episodes','CPU_seconds')}
if __name__=='__main__':print(json.dumps(run(),indent=2))
