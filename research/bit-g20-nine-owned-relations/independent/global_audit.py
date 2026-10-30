"""Separate literal-stream census/lifetime/column audit, without producer imports."""
from local_audit import *
def main():
 word=read(CAND/'WORD.json.gz');calls=read(CAND/'CALLS.json');oldcalls=read(SRC/'provider/data/CALLS.json')
 owned=set(range(11238,11249));pivots=list(range(469,478));retired={c['helper_owner_begin']+p-222 for c in oldcalls for p in pivots}
 keep=[i for i in range(11400)if i not in retired];mp={x:i for i,x in enumerate(keep)}
 need(len(retired)==162 and len(keep)==11238,'Exact target/column retirement')
 raw=gzip.decompress((CAND/'GLOBAL.jsonl.gz').read_bytes());events=[json.loads(l)for l in raw.splitlines()]
 rows=[1<<i for i in range(11249)];norm=[1]*11249;peak=1;paid=Counter();counts=Counter();queries=[];epochs=[0]*11249;versions=[0]*11249;prefix=hashlib.sha256();lines=raw.splitlines(keepends=True)
 for ix,e in enumerate(events):
  op,d=e[:2];counts[op]+=1
  if op=='OWNED_CLEAR':need(d in owned,'Only private owned erasure');rows[d]=norm[d]=0;epochs[d]+=1;versions[d]+=1
  elif op=='ADD':
   s=e[2];need(d!=s and 0<=d<11249 and 0<=s<11249,'ADD owner');rows[d]^=rows[s];norm[d]+=norm[s];versions[d]+=1;peak=max(peak,norm[d])
  elif op=='QUERY':
   need(e[2]>0,'Paid query rank');paid[e[2]]+=1;queries.append((ix,d,versions[d],epochs[d],e[2],rows[d],prefix.hexdigest()));versions[d]+=1
  elif op in('OWNED_ZERO_HEADER','WHOLE_ZERO_FRAME'):need(d in owned and rows[d]==0,'Zero-only frame/header')
  else:need(op=='PAID_PORT_ROUTE','Unknown event')
  prefix.update(lines[ix])
 need(rows==[1<<i for i in range(11238)]+[0]*11,'All11249 independent RAW/DIRTY columns endpoint')
 need(len(calls)==18,'All18 thick calls')
 for c in calls:
  x,y=c['source_bank'],c['target_bank'];h=c['helper_old_owner_begin'];w=c['owned_global_indices'];pmap=dict(zip(pivots,w[2:]))
  need(w==list(range(11238,11249))and c['retained_helper_count']==427,'Full allocated owned reserve and helper census')
  def owner(r):
   if r==658:return w[0]
   if r==659:return w[1]
   if r in pmap:return pmap[r]
   return mp[(x if r<111 else y)*111+r%111]if r<222 else mp[h+r-222]
  need(len({owner(i)for i in range(660)})==660,'No original/owned physical alias in call')
  core=events[c['core_begin']:c['core_end']];need(len(core)==len(word['records']),'Complete literal core length')
  for ix,(a,b)in enumerate(zip(word['records'],core)):
   op,d=a[:2];gd=owner(d)
   if op=='ERASE':need(b[:3]==['OWNED_CLEAR',gd,a[2]],'Exact mapped erasure')
   elif op=='ADD':need(b[:3]==['ADD',gd,owner(a[2])],'Exact mapped ADD')
   elif op=='Q':need(b[:3]==['QUERY',gd,a[4]]and b[3][2:4]==a[2:4],'Exact native residual query')
   elif op=='ZERO_Q':need(b[:5]==['WHOLE_ZERO_FRAME',gd,*a[2:]],'Exact mapped zero query')
   else:need(op=='INIT'and b[:3]==['OWNED_ZERO_HEADER',gd,a[2]],'Exact mapped zero header')
 old=read(SRC/'provider/data/INVOICE.json');want=Counter({int(k):v for k,v in old['paid'].items()});want[1]-=162;want[7]-=162;need(paid==want,'All paid queries from literal stream')
 ts=read(CAND/'TARGET-OWNERS.json');oldts=read(SRC/'provider/data/TARGET-OWNERS.json');expected=[dict(t,original_owner=mp[t['original_owner']])for t in oldts if t['original_owner']not in retired]
 need(ts==expected,'Exactly retained old target classes with compacted owners')
 need(len(ts)==11238 and len({t['original_owner']for t in ts})==11238,'One credit per retained independent original')
 target=Counter(t['rank']for t in ts);need(target[4]==72 and target[8]==7614,'All partial and full targets debited correctly')
 desc=read(CAND/'SOURCE-DESCRIPTORS.json.gz');need(len(desc)==len(queries),'All source descriptors')
 for d,q in zip(desc,queries):
  need((d['event'],d['owner'],d['version'],d['epoch'],d['rank'],int(d['RAW_hex'],16),d['prefix_sha256'])==q,'Actual complete-prefix hash/RAW/owner epoch/version descriptor')
  need(d['detail']==events[d['event']][3]and d['function_identity']=='Exact literal program prefix plus current owner/epoch/version and actual geometric source job; RAW bitmap is extra evidence, not a claim of purity.','Actual geometric current-source function descriptor')
 out={'status':'PASS_INDEPENDENT_LITERAL_GLOBAL_STREAM_11249_COLUMNS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stream_sha256':hashlib.sha256(raw).hexdigest(),'events':len(events),'paid':dict(sorted(paid.items())),'targets':dict(sorted(target.items())),'retired_originals':162,'retained_originals':11238,'private_owned_allocated':11,'private_output_credit':0,'calls':18,'query_descriptors_verified':len(queries),'majorant_bits':peak.bit_length(),'operation_counts':dict(counts),
 'physical_attachment':'Local exact QQ frame induction establishes the substituted program equals the same physical 2-bank endpoint for either direction. Each retained partial/full helper endpoint D_P is involutive. Thus identical rho entry/return conjugations compose to the unchanged controller physical operator. Inverse birth/exit frame names are internal to its new decomposition and are explicitly replayed locally; no extra address operator is inserted. Retain the inherited all-column route/whole-job assumptions.',
 'remaining':['Rebind native rho/full-row routes and main physical coefficient proof to exact retained inputs in the publication package.','Regenerate all finite cost/precision/owned stock constants and prove the ordinary tail/compiler/cover/bootstrap certificate.','This audit does not run selected complete multiplication cold replay or claim external review.']}
 (HERE/'GLOBAL-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps({k:out[k]for k in('status','events','calls','query_descriptors_verified','majorant_bits')}))
if __name__=='__main__':main()
