"""Cold, stdlib-only replay of the private G20/G23 candidate.

Run with Python -I [-O] -B.  All runtime reads stay under the candidate
directory; provenance origin paths are never followed.  This proves no
ordinary exponent.  It checks the literal native programme and fee schema.
"""
from pathlib import Path
import argparse,ctypes,gzip,hashlib,json,os,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from local_ir import N,EXPECTED,need,Geometry,replay,baseline_program,transpose_rows,rowproduct
from audit_global import audit
from bindings_fees import construct,project,mm,eye
from fractions import Fraction as F

def read(p):
 b=p.read_bytes()
 return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def put(p,value):
 p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def member(root,relative):
 p=(root/relative).resolve()
 need(p.is_relative_to(root.resolve())and p.is_file(),'Manifest relative local file '+relative)
 return p
def manifest_check(provider):
 root=provider.parent;m=read(provider/'MANIFEST.json')
 need(m['schema']=='g20-private-native-runtime/1','Runtime manifest schema')
 names=set()
 for item in m['files']:
  rel=item['relative_path'];need(rel not in names,'Unique manifest path');names.add(rel)
  p=member(root,rel);need(p.stat().st_size==item['bytes']and sha(p)==item['sha256'],'Runtime byte pin '+rel)
 required={'INPUT-PINS.json','provider/verify.py','provider/local_ir.py','provider/audit_global.py','provider/bindings_fees.py','provider/data/GLOBAL.jsonl.gz','provider/data/SOURCE-DESCRIPTORS.jsonl.gz'}
 need(required<=names,'All cold runtime leaves pinned')
 for item in read(root/'INPUT-PINS.json')['files']:
  p=member(root,item['relative_path']);need(item['relative_path']in names and sha(p)==item['sha256'],'Frozen input pin '+item['relative_path'])
 # A wrong source byte is rejected independently of mathematical rank guards.
 first=m['files'][0];p=member(root,first['relative_path'])
 need(hashlib.sha256(p.read_bytes()+b'changed').hexdigest()!=first['sha256'],'Source byte negative guard')
 return {'sha256':sha(provider/'MANIFEST.json'),'files':len(names),'input_files':len(read(root/'INPUT-PINS.json')['files'])}
def memory_peak():
 if os.name!='nt':return {'available':False,'reason':'Windows psapi counter unavailable on this OS'}
 class PMC(ctypes.Structure):
  _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(x,ctypes.c_size_t)for x in('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
 kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=ctypes.c_void_p
 psapi=ctypes.WinDLL('psapi',use_last_error=True);psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PMC),ctypes.c_ulong];psapi.GetProcessMemoryInfo.restype=ctypes.c_int
 p=PMC();p.cb=ctypes.sizeof(p)
 if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(p),p.cb):return {'available':False,'winerror':ctypes.get_last_error()}
 return {'available':True,'PeakWorkingSetSize':p.PeakWorkingSetSize,'PeakPagefileUsage':p.PeakPagefileUsage}
def local_check(provider):
 inp=provider.parent/'inputs';data=provider/'data';base=read(inp/'BASELINE-LOCAL.json.gz');frames=read(inp/'FRAMES.json')['frames'];geometry=Geometry(frames)
 saved=read(data/'LOCAL-INVOICE.json');savedrows=read(data/'LOCAL-ROWS.json.gz');rows={};receipts={}
 for name in('FORWARD','INVERSE','RAW-DUAL'):
  payload=read(data/(name+'.json.gz'));expected_birth=base['final']if name=='INVERSE'else base['start'];expected_exit=base['start']if name=='INVERSE'else base['final']
  need(payload['start']==expected_birth and payload['final']==expected_exit,'All original birth/exit flags '+name)
  result,stats,_=replay(payload['records'],payload['start'],payload['final'],geometry)
  need(stats['paid']==EXPECTED and stats['private_peak']==2,'Proper new local profile and exact owned peak '+name)
  # JSON object keys encode integer ranks as strings. Compare the exact
  # scientific record after that lossless, explicit serialization step.
  need(json.loads(json.dumps(stats))==saved['directions'][name]and [hex(v)for v in result]==savedrows[name],'Recomputed local invoice and every RAW column '+name)
  controls=[]
  for modulus in(101,101**2):
   actual,_,_=replay(payload['records'],payload['start'],payload['final'],geometry,modulus);need(actual==result,'All independent native symbols '+name);controls.append(modulus)
  rows[name]=result;receipts[name]={'rankmass':stats['rankmass'],'paid':stats['paid'],'private_peak':stats['private_peak'],'majorant_bits':stats['majorant_bits'],'native_moduli_all658_symbols':controls,'whole_function_proof':'Every ADD has exact common coframe, every QUERY is the nested-projector MOVE, and every owned erase/reheader has a literal lifecycle. FRAME induction supplies all functions; finite pulses are controls.'}
 old,_,_=replay(baseline_program(base),base['start'],base['final'],geometry);oldinverse,_,_=replay(baseline_program(base,True),base['final'],base['start'],geometry)
 need(rows['FORWARD']==old and rows['INVERSE']==oldinverse,'Unchanged old all658 forward and true inverse operators')
 identity=[1<<i for i in range(N)];need(rowproduct(rows['FORWARD'],rows['INVERSE'])==rowproduct(rows['INVERSE'],rows['FORWARD'])==identity,'Both true inverse compositions')
 need(rows['RAW-DUAL']==transpose_rows(rows['INVERSE']),'FUNCTION inverse-transpose, not ADDRESS inverse-transpose')
 requests=read(inp/'G22-FRESH-REQUESTS.json')
 for req in requests:
  s,t,r=req['old_frame'],req['new_frame'],req['rank'];geometry.nested(s,t,r);p=[[x-y for x,y in zip(a,b)]for a,b in zip(project(frames[str(t)]),project(frames[str(s)]))];S=[[F(x)for x in row]for row in req['matcher_S']];Si=[[F(x)for x in row]for row in req['matcher_inverse']];q=[[F(i==j and i<r)for j in range(8)]for i in range(8)]
  need([[F(x)for x in row]for row in req['projector']]==p and mm(p,p)==p and sum(p[i][i]for i in range(8))==r and mm(S,Si)==mm(Si,S)==eye(8)and mm(mm(S,q),Si)==p,'Exact new proper-rank callback geometry and matcher')
 negatives={};forward=read(data/'FORWARD.json.gz')
 for mutation in('wrong_rank4','omit_shadow_clear','wrong_shadow_frame'):
  try:replay(forward['records'],forward['start'],forward['final'],geometry,mutant=mutation)
  except ValueError as error:negatives[mutation]=str(error)
  else:raise ValueError('Accepted local mutation '+mutation)
 try:replay(forward['records']+[['CLEAR',0]],forward['start'],forward['final'],geometry)
 except ValueError as error:negatives['original_CLEAR']=str(error)
 else:raise ValueError('Accepted original erasure')
 return receipts,negatives
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--provider',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 provider=args.provider.resolve();output=args.output.resolve();need(provider==Path(__file__).resolve().parent,'CLI provider must match the executed pinned module');need(not output.exists(),'Output must be fresh');need(not output.is_relative_to(provider),'No writes to frozen provider');output.mkdir(parents=True)
 begin=time.perf_counter();cpu=time.process_time();pins=manifest_check(provider);local,localneg=local_check(provider);glob=audit(provider)
 globalneg={}
 for mutation in('duplicate_helper_owner','omit_shadow_clear','wrong_rank4','wrong_shadow_frame'):
  try:audit(provider,mutant=mutation)
  except ValueError as error:globalneg[mutation]=str(error)
  else:raise ValueError('Accepted global mutation '+mutation)
 fees=construct(provider,False)
 for name,key in [('PORT-CHARTS.json','ports'),('PARTIAL-JOB-MATCHERS.json','partial_matchers'),('MAIN-JOB-MATCHERS.json','main_matcher_templates'),('TARGET-OWNERS.json','targets'),('JOB-MATCHING-ROUTES.json','canonical_route_program'),('FULL-FEES.json','fees')]:need(read(provider/'data'/name)==fees[key],'Literal rational binding/fee schema '+name)
 result={'status':'PASS_PRIVATE_NATIVE_CANDIDATE_READY_FOR_ORDINARY_CERTIFICATE','runtime_manifest':pins,'isolated':sys.flags.isolated,'optimized':sys.flags.optimize,'python':sys.version,'local_all_originals':local,'local_negative_controls':localneg,'global':glob,'global_negative_controls':globalneg,'rational_source_and_job_bindings':{'original_targets':len(fees['targets']),'canonical_matching_routes':len(fees['canonical_route_program']),'internal_main_routes':fees['fees']['in_BODY_paid_MAINport_wholefiber_routes'],'owned_banks':2,'owned_original_credit':0},'fee_schema_status':fees['fees']['status'],'ordinary_saving':None,'whole_kappa':None,'publication_authorized_by_this_receipt':False,'elapsed_seconds':time.perf_counter()-begin,'CPU_seconds':time.process_time()-cpu,'memory':memory_peak()}
 put(output/'RESULT.json',result);put(output/'FULL-FEES-CHECKED.json',fees['fees']);print(json.dumps({'status':result['status'],'originals':glob['original_RAW'],'paid_queries':glob['query_count'],'literal_event_sha256':glob['event_sha256'],'owned_peak':glob['private_peak'],'global_majorant_bits':glob['majorant_bits'],'optimized':sys.flags.optimize,'CPU_seconds':result['CPU_seconds'],'memory':result['memory']}))
if __name__=='__main__':main()
