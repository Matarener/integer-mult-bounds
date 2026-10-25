"""Self-contained, Git-free, read-only cold replay of the local E construction."""
import argparse,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def normal(x):return json.loads(json.dumps(x))
def load(name):
 spec=importlib.util.spec_from_file_location('local_E_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
def old(name):
 p=HERE/name
 return json.loads(gzip.decompress(p.read_bytes()))if name.endswith('.gz')else json.loads(p.read_bytes())
def calculate():
 before={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in HERE.rglob('*')if p.is_file()}
 reports={}
 x=load('e_adapter').calc();need(normal(x)==old('E-ADAPTER.json'),'exact local E adapter receipt');reports['local_exact']=x['status']
 for name,receipt,program in [('checkpoint','ROOT-CHECKPOINT.json','ROOT-CHECKPOINT-PROGRAM.json.gz'),('owned_e','OWNED-E.json','OWNED-E-PROGRAM.json'),('modes','MODES.json','MODES-PROGRAM.json'),('n3','N3.json','N3-PROGRAM.json'),('two_cube_native','TWO-CUBE-NATIVE.json','TWO-CUBE-NATIVE-PROGRAM.json.gz')]:
  m=load(name);r,p=m.calculate(m.SOURCE)if name=='checkpoint'else m.calculate();need(normal(r)==old(receipt),name+' exact science receipt');need(normal(p)==old(program),name+' complete canonical literal program');reports[name]=r.get('status',r.get('schema'))
  if name=='modes':modes=r
  if name=='checkpoint':checkpoint=r
  if name=='two_cube_native':twocube=r
 files=['run.py','e_adapter.py','checkpoint.py','owned_e.py','modes.py','n3.py','two_cube_native.py','two_cube_frame_tools.py','inputs/B-PROGRAM.json.gz','inputs/K-TEMPLATE.json','inputs/NORMALIZERS.json','inputs/clifford_exact.py']
 result={'schema':'source-consuming-E-local-positive-cold-replay/v1','status':'PASS_LOCAL_BOTH_ORIENTATION_E_AND_TYPED_N3','components':reports,'global_paid_per_full':{'8':112**3,'9':112**3,'15':112**3,'16':112**3,'25':20480},'actual_root_source_contacts':checkpoint['source_contacts_checked'],'actual_root_source_reads':checkpoint['actual_source_ADD_reads_checked'],'global_nonzero_modes':modes['nonzero_global_modes'],'N3_negative_endpoint':'Q^-1 E3 E2^-1 E1 D123; Gaussian admission UNKNOWN','N3_positive_endpoint':'D123 Q after ordinary code inverse; rank73','conditional_margin_interval':modes['preflight']['certified_margin20480_interval'],'whole_caller_Gaussian_admission':False,'new_kappa':False,'code_and_input_sha256':{p:hashlib.sha256((HERE/p).read_bytes()).hexdigest()for p in files},'scope':'Pure same-folder Python standard library. Default does not write. Full physical local E word and inverse/transpose source-contact mechanism plus typed N3; independent Gaussian negative terminal and outer TM/precision/storage admission remain UNKNOWN.'}
 after={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in HERE.rglob('*')if p.is_file()}
 need(before==after,'default combined calculation leaves every package file byte-identical')
 result['all_package_files_readonly']=True
 return normal(result)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=calculate()
 if a.write:(HERE/'RESULT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:need(r==old('RESULT.json'),'frozen combined local-positive receipt')
 print(json.dumps(r,sort_keys=True))
