"""Materialize the exact G23 stream and separate current-source descriptors."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
from datetime import datetime,timezone
from time import process_time
import gzip,json
from local_ir import N as LN,EXPECTED,need
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;INPUT=ROOT/'inputs';DATA=HERE/'data';N=11400;V=111
def read(p):return json.loads(gzip.decompress(p.read_bytes()))if p.suffix=='.gz'else json.loads(p.read_bytes())
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def xor(a,b):
 out=a.copy()
 for k,v in b.items():
  out[k]=out.get(k,0)^v
  if not out[k]:del out[k]
 return out
def shift(a,s):return{k^s:v for k,v in a.items()}
def physical_main(controller):
 rows=[{0:1<<i}for i in range(32)]
 def boundary(program):
  for op,d,s in program:
   if op=='ADD':rows[d]=xor(rows[d],rows[s])
   else:need(op=='SWAP','Boundaryopcode');rows[d],rows[s]=rows[s],rows[d]
 boundary(controller['boundaries']['right_program'])
 for e in controller['physical_events']:
  op=e[0]
  if op in('LOCAL','QUERY_SHEAR'):
   _,stage,pair,rev=e;x,y=2*pair,2*pair+1
   if rev:x,y=y,x
   rows[y]=xor(rows[y],shift(rows[x],1))
   if op=='LOCAL':rows[x]=shift(rows[x],1<<(stage+1));rows[y]=shift(rows[y],1<<(stage+1))
  elif op=='IDLE':
   _,pair,stages=e;s=sum(1<<(j+1)for j in stages)
   for bank in(2*pair,2*pair+1):rows[bank]=shift(rows[bank],s)
  elif op=='ADD':rows[e[1]]=xor(rows[e[1]],rows[e[2]])
  else:need(op=='SWAP','Controlleropcode');rows[e[1]],rows[e[2]]=rows[e[2]],rows[e[1]]
 boundary(controller['boundaries']['left_program']);need(rows==[{int(t):1<<i}for i,t in enumerate(controller['diagonal'])],'EveryphysicalMAINpolynomialcoefficient')
 return[{str(k):v for k,v in row.items()}for row in rows]
def main():
 clock=process_time();DATA.mkdir(exist_ok=True);controller=read(INPUT/'CONTROLLER.json');base=read(INPUT/'BASELINE-LOCAL.json.gz');frames=read(INPUT/'FRAMES.json')['frames'];expected=read(INPUT/'G23-EXPECTED.json');thick=controller['invoice']['thick_stages'];stage_index={s:i for i,s in enumerate(thick)};programs={False:read(DATA/'FORWARD.json.gz')['records'],True:read(DATA/'INVERSE.json.gz')['records']}
 mainrows=physical_main(controller);values=[1<<i for i in range(N)]+[0,0];versions=[0]*(N+2);norm=[1]*N+[0,0];epoch=[0]*(N+2);peak=1;privatepeak=0;counts=Counter();paid=Counter();calls=[];episodes=[];changed_requests=[];eventno=0;source_count=0;streamhash=sha256();sourcehash=sha256();tickets={}
 raw_file=(DATA/'GLOBAL.jsonl.gz').open('wb');out=gzip.GzipFile(filename='',fileobj=raw_file,mode='wb',mtime=0);src_file=(DATA/'SOURCE-DESCRIPTORS.jsonl.gz').open('wb');srcout=gzip.GzipFile(filename='',fileobj=src_file,mode='wb',mtime=0)
 def emit(e):
  nonlocal eventno
  b=(json.dumps(e,separators=(',',':'))+'\n').encode();streamhash.update(b);out.write(b);eventno+=1;counts[e[0]]+=1
 def source(owner,rank,geometry,extra=None,arg_version=None):
  nonlocal source_count
  desc={'event':eventno,'prefix_sha256':streamhash.hexdigest(),'source_namespace':f'G20_CURRENT_QUERY/{source_count}','owner':owner,'owner_epoch':epoch[owner],'version':versions[owner]if arg_version is None else arg_version,'rank':rank,'geometry':geometry,'current_RAW_bitmap_sha256':sha256(values[owner].to_bytes((N+7)//8,'little')).hexdigest(),'DOMAIN':'completecurrentGLOBALunitcoverROW/HEAD/pairedTAIL/spectatorARRAY','source_history':'Frozenprefix+owner+currentversiondefinesactualFUNCTION; thisRAWbitmaphashisextraevidence,nottheonlyfunctionclaim.'}
  if extra:desc['compound_or_context']=extra
  b=(json.dumps(desc,separators=(',',':'))+'\n').encode();sourcehash.update(b);srcout.write(b);source_count+=1
 def add(d,s,kind='ADD',meta=None):
  nonlocal peak
  need(d!=s,'DistinctDATAfields');need(not any(t[0]==d for t in tickets.values()),'ImmutableSOURCElease');values[d]^=values[s];versions[d]+=1;norm[d]+=norm[s];peak=max(peak,norm[d]);emit([kind,d,s,meta])
 def swap(d,s,label):add(d,s,meta=label);add(s,d,meta=label);add(d,s,meta=label)
 def boundary(program,label):
  for op,d,s in program:
   for p in range(V):
    if op=='ADD':add(d*V+p,s*V+p,meta=label)
    else:need(op=='SWAP','Fixedboundary');swap(d*V+p,s*V+p,label)
 boundary(controller['boundaries']['right_program'],'RIGHT_BOUNDARY')
 for event in controller['physical_events']:
  op=event[0]
  if op=='LOCAL':
   _,stage,pair,rev=event;baseh=32*V+436*stage_index[stage];helpers=list(range(baseh,baseh+436));need(all(values[h]==1<<h for h in helpers),'Distinctarbitraryoriginalhelperbank');x,y=2*pair,2*pair+1
   if rev:x,y=y,x
   sx=[values[x*V+i]for i in range(V)];sy=[values[y*V+i]for i in range(V)]
   def owner(r):return N+r-658 if r>=658 else((x if r<V else y)*V+r%V if r<222 else baseh+r-222)
   if stage:
    for bank in(x,y):
     for p in range(V):emit(['PAID_PORT_ROUTE',stage,bank*V+p,p,'ENTRY',stage_index[stage]]);versions[bank*V+p]+=1
   begin=eventno;st=list(base['final']if rev else base['start'])+[None,None];lp=Counter();shadowlive=False;localepisode=None
   for localno,e in enumerate(programs[rev]):
    typ,d=e[:2];gd=owner(d)
    if typ=='Q':
     s,t,k=e[2:];need(st[d]==s and 0<k<8 and abs(frames[str(s)]['dim']-frames[str(t)]['dim'])==k,'Actualproperlocalcurrentframe');need(not any(v[0]==gd for v in tickets.values()),'NoimmutableSOURCEquery')
     source(gd,k,{'kind':'LOCAL_nested_projector','stage':stage,'from':s,'to':t,'rank':k,'native_local_head':8,'future_common_head':'embedE0andtensorthecolumnI_f'},{'local_record':localno,'inverse':rev,'fresh_function':True})
     if d==464 and {s,t}=={0,507}:changed_requests.append({'event':eventno,'stage':stage,'owner':gd,'version':versions[gd],'rank':k,'frame_from':s,'frame_to':t,'current_RAW_hex':hex(values[gd])})
     st[d]=t;versions[gd]+=1;paid[k]+=1;lp[k]+=1;emit(['LOCAL_QUERY',stage,gd,s,t,k,rev])
    elif typ=='ADD':
     s,f=e[2:];need(st[d]==st[s]==f,'Actual commonFRAME LOCALADD');add(gd,owner(s),'LOCAL_ADD',[stage,f,rev])
    elif typ=='COPY':
     s,f,k=e[2:];gs=owner(s);need(d==658 and gd not in tickets and st[d]is None and values[gd]==0 and st[s]==f,'FreshownedwholeSOURCEcapture');values[gd]=values[gs];norm[gd]=norm[gs];epoch[gd]+=1;versions[gd]+=1
     source(gd,k,{'kind':'LOCAL_capture_projector','stage':stage,'from':f,'to':0,'rank':k},{'local_record':localno,'copy_from':gs,'copy_source_version':versions[gs],'copy_assignment_before_query':True,'inverse':rev})
     tickets[gd]=(gs,versions[gs],f,values[gs],eventno);st[d]=0;paid[k]+=1;lp[k]+=1;versions[gd]+=1;emit(['LOCAL_COPY_QUERY',stage,gs,gd,f,0,k,rev])
    elif typ=='TICKET_CLEAR':
     s,f=e[2:];gs=owner(s);need(gd in tickets and tickets[gd][:4]==(gs,versions[gs],f,values[gs])and values[gd]==values[gs]and st[s]==f,'ActualCOPYlease/version/completeRAW');episodes.append({'stage':stage,'kind':'immutable_LOCAL_COPY','owner':gd,'source':gs,'source_version':versions[gs],'begin':tickets[gd][4],'end':eventno});tickets.pop(gd);values[gd]=norm[gd]=0;st[d]=None;versions[gd]+=1;emit(['LOCAL_PAID_CLEAR',stage,gd,rev])
    elif typ=='INIT':
     f=e[2];need(d==659 and values[gd]==0 and st[d]is None and not shadowlive,'Newcompleteownedshadowinitializedzero');st[d]=f;shadowlive=True;shadowbegin=eventno;epoch[gd]+=1;emit(['SHADOW_PAID_INIT',stage,gd,f,rev])
    else:
     need(typ=='CLEAR'and d==659 and shadowlive and gd not in tickets,'PaidownedshadowwholepayloadCLEAR');episodes.append({'stage':stage,'kind':'new_sameFRAME_shadow','owner':gd,'frame':st[d],'begin':shadowbegin,'end':eventno});values[gd]=norm[gd]=0;st[d]=None;versions[gd]+=1;shadowlive=False;emit(['SHADOW_PAID_CLEAR',stage,gd,rev])
    privatepeak=max(privatepeak,len(tickets)+int(shadowlive))
   need(st==list(base['start']if rev else base['final'])+[None,None]and not tickets and not shadowlive and values[N:]==[0,0],'CompleteLOCALreturn')
   need(lp==Counter(EXPECTED)and all(values[x*V+i]==sx[i]and values[y*V+i]==sy[i]^sx[i]for i in range(V))and all(values[h]==1<<h for h in helpers),'Allarbitrarycalleeinputsandunchangedhelperjobs')
   if stage:
    for bank in(x,y):
     for p in range(V):emit(['PAID_PORT_ROUTE',stage,bank*V+p,p,'RETURN',stage_index[stage]]);versions[bank*V+p]+=1
   calls.append({'stage':stage,'pair':pair,'inverse':rev,'helper_owner_begin':baseh,'source_bank':x,'target_bank':y,'core_begin':begin,'core_end':eventno,'profile':dict(lp),'owned_global_indices':[N,N+1],'original_helper_jobs':{'4':4,'8':432}})
  elif op=='QUERY_SHEAR':
   _,stage,pair,rev=event;x,y=2*pair,2*pair+1
   if rev:x,y=y,x
   for p in range(V):
    sourcefield,dst=x*V+p,y*V+p;need(values[N:]==[0,0]and not tickets,'Noaliaswithparentownedshadow');v=versions[sourcefield];values[N]=values[sourcefield];norm[N]=norm[sourcefield];versions[N]+=1;epoch[N]+=1;begin=eventno;emit(['THIN_COPY',stage,sourcefield,N,p,v])
    source(N,1,{'kind':'THIN_central_portline','port':p,'rank':1},{'copy_from':sourcefield,'source_version':v,'inverse':rev});paid[1]+=1;versions[N]+=1;emit(['THIN_PAID_QUERY',stage,N,p,1,rev]);add(dst,N,'THIN_ADD',[stage,p,rev]);need(versions[sourcefield]==v,'ThinSOURCEunchanged');values[N]=norm[N]=0;versions[N]+=1;emit(['THIN_PAID_CLEAR',stage,N]);episodes.append({'stage':stage,'kind':'old_THIN','owner':N,'source':sourcefield,'source_version':v,'begin':begin,'end':eventno})
  elif op=='IDLE':
   _,pair,stages=event;k=7*len(stages)
   for bank in(2*pair,2*pair+1):
    for p in range(V):
     field=bank*V+p;source(field,k,{'kind':'WHOLE_IDLE_disjoint_stages','port':p,'stages':stages,'rank':k});paid[k]+=1;versions[field]+=1;emit(['PAID_WHOLE_IDLE',field,stages,k,p])
  elif op=='ADD':
   for p in range(V):add(event[1]*V+p,event[2]*V+p,meta='BRIDGE')
  else:
   need(op=='SWAP','Controlleropcode')
   for p in range(V):swap(event[1]*V+p,event[2]*V+p,'FINAL_SWAP')
 boundary(controller['boundaries']['left_program'],'LEFT_BOUNDARY');out.close();raw_file.close();srcout.close();src_file.close();need(values==[1<<i for i in range(N)]+[0,0],'All11400originalRAWandwholeownedreturn')
 targets=Counter({8:432*18,4:4*18})
 for term in controller['diagonal']:need(term&1,'RetainedcentralSOURCEfactor');targets[1+7*(int(term)>>1).bit_count()]+=V
 need(streamhash.hexdigest()==expected['expanded_event_sha256']and eventno==expected['expanded_event_count'],'ExactG23literalstreamnotanewunboundvariant')
 need(paid==Counter({int(k):v for k,v in expected['paid'].items()})and targets==Counter({int(k):v for k,v in expected['targets'].items()})and len(changed_requests)==18,'ExactG23invoiceandfreshrank4requests')
 need(peak.bit_length()==expected['cancellation_free_majorant_bits']and str(peak)==expected['cancellation_free_majorant'],'Actual newmajorantfullyregenerated')
 need(len(calls)==18 and len(episodes)==1845 and privatepeak==2,'Allownedepisodesandmaximumcoexistence')
 result={'status':'MATERIALIZED_EXACT_G23_ALL11400_RAW','at_utc':datetime.now(timezone.utc).isoformat(),'originals':N,'private_allocated':2,'private_peak':privatepeak,'private_episodes':len(episodes),'calls':18,'expanded_event_count':eventno,'expanded_event_sha256':streamhash.hexdigest(),'global_gzip_sha256':sha256((DATA/'GLOBAL.jsonl.gz').read_bytes()).hexdigest(),'SOURCE_descriptor_count':source_count,'SOURCE_descriptors_sha256':sourcehash.hexdigest(),'paid':dict(sorted(paid.items())),'targets':dict(sorted(targets.items())),'rank_surplus':sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items()),'operation_counts':dict(counts),'majorant_bits':peak.bit_length(),'majorant':str(peak),'newbound':None,'CPU_seconds':process_time()-clock}
 put(DATA/'GLOBAL-RESULT.json',result);put(DATA/'CALLS.json',calls);put(DATA/'PRIVATE-EPISODES.json',episodes);put(DATA/'NEW-RANK4-REQUESTS.json',changed_requests);put(DATA/'MAIN-PHYSICAL-COEFFICIENTS.json',mainrows);put(DATA/'INVOICE.json',{'paid':result['paid'],'targets':result['targets'],'originals':N,'private_output_credit':0,'QUERYs':sum(paid.values()),'rawrank_surplus':result['rank_surplus'],'rawprice_reference':'inputs/G23-RAW-PRICE.json only, notordinarysaving','ordinary_tail_bootstrap_status':'Pendingseparatecertificatewithfreshfees/constants; old4760/4814unchanged'})
 print(json.dumps({k:result[k]for k in('status','expanded_event_count','expanded_event_sha256','SOURCE_descriptor_count','private_episodes','majorant_bits','CPU_seconds')}))
if __name__=='__main__':main()
