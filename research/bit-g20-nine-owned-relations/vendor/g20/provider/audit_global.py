"""Independent emitted-stream reader; never imports build_global.py."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import gzip,json
from local_ir import need,Geometry
N=11400;V=111
def read(p):return json.loads(gzip.decompress(p.read_bytes()))if p.suffix=='.gz'else json.loads(p.read_bytes())
def audit(root,mutant=None):
 root=Path(root);inp=root.parent/'inputs';data=root/'data';base=read(inp/'BASELINE-LOCAL.json.gz');frames=read(inp/'FRAMES.json')['frames'];geom=Geometry(frames);calls=read(data/'CALLS.json');claimed=read(data/'GLOBAL-RESULT.json');controller=read(inp/'CONTROLLER.json')
 if mutant=='duplicate_helper_owner':calls[1]['helper_owner_begin']=calls[0]['helper_owner_begin']
 owners=[i for c in calls for i in range(c['helper_owner_begin'],c['helper_owner_begin']+436)];need(len(calls)==18 and len(owners)==len(set(owners))==7848 and set(owners)==set(range(3552,N)),'All7848fresharbitraryhelperowners, nodoublecredit')
 values=[1<<i for i in range(N)]+[0,0];versions=[0]*(N+2);epochs=[0]*(N+2);norm=[1]*N+[0,0];peak=1;privatepeak=0;lease=None;shadow=None;current=None;state=None;seen=[];paid=Counter();counts=Counter();episodes=[];source_no=0;raw_hash=sha256();src_hash=sha256();changed=False;new4=0
 source_file=gzip.open(data/'SOURCE-DESCRIPTORS.jsonl.gz','rb')
 def local(role):
  need(current is not None,'ActualactiveLOCALowner')
  if role>=N:need(role<N+2,'Onlytwoownedstreams');return 658+role-N
  bank,port=divmod(role,V)
  if bank==current['x']:return port
  if bank==current['y']:return V+port
  k=role-current['helper_owner_begin'];need(0<=k<436,'LOCALcannotreadanothercalleehelper');return 222+k
 def finish():
  nonlocal current,state
  if current is None:return
  need(lease is None and shadow is None and values[N:]==[0,0],'BothownedbanksandCOPYleasecompletebeforecalleeexit')
  need(state==list(base['start']if current['inverse']else base['final'])+[None,None],'All658actualcalleeendframes')
  need(all(values[i]==1<<i for i in range(current['helper_owner_begin'],current['helper_owner_begin']+436)),'All436DIRTYhelperendrowsrestored')
  need(all(values[current['x']*V+i]==current['sx'][i]and values[current['y']*V+i]==current['sy'][i]^current['sx'][i]for i in range(V)),'CurrentSOURCE/Yexactcalleevalue law')
  current=None;state=None
 def enter(stage):
  nonlocal current,state
  if current is not None and current['stage']==stage:return
  finish();need(stage not in seen,'No hiddenresumptionofreturnedcallee');seen.append(stage);c=next(x for x in calls if x['stage']==stage);x,y=2*c['pair'],2*c['pair']+1
  if c['inverse']:x,y=y,x
  current=dict(c,x=x,y=y,sx=values[x*V:(x+1)*V],sy=values[y*V:(y+1)*V]);state=list(base['final']if c['inverse']else base['start'])+[None,None]
  need(all(values[i]==1<<i for i in range(c['helper_owner_begin'],c['helper_owner_begin']+436)),'Freshoriginalhelpers arenotzeroorcopy')
 def check_source(idx,prefix,owner,rank,geometry,extra=None):
  nonlocal source_no
  line=source_file.readline();need(bool(line),'MissingSOURCEdescriptor');src_hash.update(line);s=json.loads(line)
  need(s['event']==idx and s['prefix_sha256']==prefix and s['source_namespace']==f'G20_CURRENT_QUERY/{source_no}','FreshSOURCEprefixnamespace')
  need((s['owner'],s['owner_epoch'],s['version'],s['rank'])==(owner,epochs[owner],versions[owner],rank),'SOURCE actualowner/currentepoch/currentversion, notoldticket')
  need(s['geometry']==geometry,'ActualfixedSOURCEgeometrydescriptor')
  need(s['current_RAW_bitmap_sha256']==sha256(values[owner].to_bytes((N+7)//8,'little')).hexdigest(),'Actual currentall11400RAWargument hash')
  need(s.get('compound_or_context')==extra,'SOURCE compoundCOPY/context binding');source_no+=1
 local_record_no=0
 with gzip.open(data/'GLOBAL.jsonl.gz','rb')as stream:
  for idx,line in enumerate(stream):
   prefix=raw_hash.hexdigest();raw_hash.update(line);e=json.loads(line);kind=e[0]
   if kind in('LOCAL_ADD','LOCAL_QUERY','LOCAL_COPY_QUERY','LOCAL_PAID_CLEAR','SHADOW_PAID_INIT','SHADOW_PAID_CLEAR'):
    stage=e[3][0]if kind=='LOCAL_ADD'else e[1]
    if current is None or current['stage']!=stage:enter(stage);local_record_no=0
   elif current is not None:finish()
   if mutant=='omit_shadow_clear'and kind=='SHADOW_PAID_CLEAR'and not changed:changed=True;continue
   if mutant=='wrong_rank4'and kind=='LOCAL_QUERY'and local(e[2])==464 and {e[3],e[4]}=={0,507}and not changed:e[5]=3;changed=True
   if mutant=='wrong_shadow_frame'and kind=='SHADOW_PAID_INIT'and not changed:e[3]=0;changed=True
   counts[kind]+=1
   if kind in('ADD','LOCAL_ADD','THIN_ADD'):
    _,dst,src,meta=e;need(dst!=src and 0<=dst<N+2 and 0<=src<N+2,'LiteralpointwiseFIELDnames');need(lease is None or dst!=lease['source'],'ImmutableCOPY SOURCE notVALUEwritten')
    if kind=='LOCAL_ADD':
     need(state[local(dst)]==state[local(src)]==meta[1],'EveryactualsameFRAME ADD')
     if src==N:need(lease is not None,'LivecurrentownedCOPYsource')
     if dst==N+1 or src==N+1:need(shadow is not None,'Liveownedshadowargument')
    values[dst]^=values[src];versions[dst]+=1;norm[dst]+=norm[src];peak=max(peak,norm[dst])
   elif kind=='LOCAL_QUERY':
    _,stage,role,s,t,k,rev=e;r=local(role);need(state[r]==s and rev==current['inverse']and(lease is None or lease['source']!=role),'ActualQUERYowner/coframe/lease');geom.nested(s,t,k)
    check_source(idx,prefix,role,k,{'kind':'LOCAL_nested_projector','stage':stage,'from':s,'to':t,'rank':k,'native_local_head':8,'future_common_head':'embedE0andtensorthecolumnI_f'},{'local_record':local_record_no,'inverse':rev,'fresh_function':True})
    if r==464 and {s,t}=={0,507}:need(k==4,'FreshmergedSOURCErank4');new4+=1
    state[r]=t;versions[role]+=1;paid[k]+=1
   elif kind=='LOCAL_COPY_QUERY':
    _,stage,src,p,f,recv,k,rev=e;need(p==N and lease is None and values[p]==0 and state[658]is None and state[local(src)]==f and recv==0 and k==geom.dims[f]==7,'CurrentwholeSOURCEcapture intoownedzero')
    values[p]=values[src];norm[p]=norm[src];epochs[p]+=1;versions[p]+=1
    check_source(idx,prefix,p,k,{'kind':'LOCAL_capture_projector','stage':stage,'from':f,'to':0,'rank':k},{'local_record':local_record_no,'copy_from':src,'copy_source_version':versions[src],'copy_assignment_before_query':True,'inverse':rev})
    state[658]=0;paid[k]+=1;versions[p]+=1;lease={'source':src,'version':versions[src],'frame':f,'row':values[src],'begin':idx,'stage':stage,'kind':'LOCAL'}
   elif kind=='LOCAL_PAID_CLEAR':
    _,stage,p,rev=e;need(p==N and lease is not None and lease['kind']=='LOCAL'and versions[lease['source']]==lease['version']and values[p]==values[lease['source']]==lease['row']and state[local(lease['source'])]==lease['frame'],'ImmutablecurrentSOURCEfunction version untilERASE');state[658]=None;values[p]=norm[p]=0;versions[p]+=1;episodes.append(('COPY',lease['begin'],idx));lease=None
   elif kind=='SHADOW_PAID_INIT':
    _,stage,p,f,rev=e;need(p==N+1 and shadow is None and values[p]==0 and state[659]is None,'Wholeownedshadowzero, notoriginalDATA');state[659]=f;epochs[p]+=1;shadow={'begin':idx,'stage':stage,'frame':f}
   elif kind=='SHADOW_PAID_CLEAR':
    _,stage,p,rev=e;need(p==N+1 and shadow is not None and(lease is None or lease['source']!=p),'PaidownedwholepayloadCLEAR afterlastuse');values[p]=norm[p]=0;state[659]=None;versions[p]+=1;episodes.append(('SHADOW',shadow['begin'],idx));shadow=None
   elif kind=='PAID_PORT_ROUTE':
    _,stage,role,port,direction,index=e;need(stage in controller['invoice']['thick_stages']and stage!=0 and role<V*32 and role%V==port,'Actualwholefiberrole/port route');need(lease is None and shadow is None,'No liveprivatecrossesportchartboundary');versions[role]+=1
   elif kind=='PAID_WHOLE_IDLE':
    _,role,stages,k,port=e;need(role<V*32 and role%V==port and k==7*len(stages)and set(stages)<=set(controller['invoice']['thick_stages']),'Actualidlegeometrynot omitted');check_source(idx,prefix,role,k,{'kind':'WHOLE_IDLE_disjoint_stages','port':port,'stages':stages,'rank':k});paid[k]+=1;versions[role]+=1
   elif kind=='THIN_COPY':
    _,stage,src,p,port,v=e;need(p==N and values[N:]==[0,0]and lease is None and versions[src]==v,'ThinwholeSOURCEcurrentversionandbothbanksavailable');values[p]=values[src];norm[p]=norm[src];epochs[p]+=1;versions[p]+=1;lease={'kind':'THIN','source':src,'version':v,'row':values[src],'begin':idx,'stage':stage,'port':port}
   elif kind=='THIN_PAID_QUERY':
    _,stage,p,port,k,rev=e;need(p==N and lease is not None and lease['kind']=='THIN'and lease['stage']==stage and lease['port']==port and k==1,'ThinquerycompletesonactualownedCOPY');check_source(idx,prefix,p,k,{'kind':'THIN_central_portline','port':port,'rank':1},{'copy_from':lease['source'],'source_version':lease['version'],'inverse':rev});paid[1]+=1;versions[p]+=1
   else:
    need(kind=='THIN_PAID_CLEAR'and e[2]==N and lease is not None and lease['kind']=='THIN'and versions[lease['source']]==lease['version']and values[N]==lease['row'],'PaidfullownedthinCLEAR/currentSOURCE');values[N]=norm[N]=0;versions[N]+=1;episodes.append(('THIN',lease['begin'],idx));lease=None
   if kind in('LOCAL_ADD','LOCAL_QUERY','LOCAL_COPY_QUERY','LOCAL_PAID_CLEAR','SHADOW_PAID_INIT','SHADOW_PAID_CLEAR'):local_record_no+=1
   privatepeak=max(privatepeak,int(lease is not None)+int(shadow is not None))
 finish();need(not source_file.read(1),'NoextraSOURCEdescriptor');source_file.close();need(values==[1<<i for i in range(N)]+[0,0]and lease is None and shadow is None,'All11400originalRAWandownedreturn')
 expectedP=Counter({int(k):v for k,v in claimed['paid'].items()});T=Counter({8:18*432,4:18*4})
 for term in controller['diagonal']:need(term&1,'AllmainSOURCEcredit');T[1+7*(int(term)>>1).bit_count()]+=V
 need(paid==expectedP and T==Counter({int(k):v for k,v in claimed['targets'].items()})and sum(T.values())==N,'Literalpaidandactualrank4/8targetcredit')
 need(raw_hash.hexdigest()==claimed['expanded_event_sha256']and src_hash.hexdigest()==claimed['SOURCE_descriptors_sha256'],'ExactstreamandfreshSOURCEdescriptor digests')
 need(counts==Counter(claimed['operation_counts'])and len(episodes)==1845 and privatepeak==2 and new4==18,'Actualnewstock/episodes/requests')
 need(peak.bit_length()==claimed['majorant_bits']and str(peak)==claimed['majorant'],'Regeneratedcancellationfreemajorant')
 # Independent representation: each row is a set(initialbank,phase), not
 # the builder's phase->bitmask dictionary.
 poly=[{(i,0)}for i in range(32)]
 def boundary(program):
  for op,d,s in program:
   if op=='ADD':poly[d]^=poly[s]
   else:need(op=='SWAP','Physicalboundary');poly[d],poly[s]=poly[s],poly[d]
 boundary(controller['boundaries']['right_program'])
 for e in controller['physical_events']:
  if e[0]in('LOCAL','QUERY_SHEAR'):
   typ,stage,pair,rev=e;x,y=2*pair,2*pair+1
   if rev:x,y=y,x
   poly[y]^={(i,m^1)for i,m in poly[x]}
   if typ=='LOCAL':
    for bank in(x,y):poly[bank]={(i,m^(1<<(stage+1)))for i,m in poly[bank]}
  elif e[0]=='IDLE':
   _,pair,stages=e;m=sum(1<<(s+1)for s in stages)
   for bank in(2*pair,2*pair+1):poly[bank]={(i,t^m)for i,t in poly[bank]}
  elif e[0]=='ADD':poly[e[1]]^=poly[e[2]]
  else:need(e[0]=='SWAP','Physicalcontroller');poly[e[1]],poly[e[2]]=poly[e[2]],poly[e[1]]
 boundary(controller['boundaries']['left_program']);need(poly==[{(i,int(m))}for i,m in enumerate(controller['diagonal'])],'IndependentALLphysicalmaincoefficients, no character-onlycheck')
 return {'status':'PASS_INDEPENDENT_LITERAL_G23_STREAM_AND_FRESH_SOURCE_HISTORY','original_RAW':N,'calls':len(seen),'query_count':sum(paid.values()),'fresh_SOURCE_descriptors':source_no,'private_episodes':len(episodes),'private_peak':privatepeak,'new_rank4_requests':new4,'majorant_bits':peak.bit_length(),'event_sha256':raw_hash.hexdigest(),'paid':dict(sorted(paid.items())),'targets':dict(sorted(T.items()))}
