"""Portable corruption controls; no optimizer or private imports."""
import copy,importlib.util,json,tempfile,sys
from pathlib import Path
H=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('ceiling',H/'verify_ceiling.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=Path(sys.argv[1]);d=json.loads(p.read_text());c=json.loads((H/'CEILING.json').read_text());count=0
with tempfile.TemporaryDirectory()as tmp:
 t=Path(tmp);dp=t/'candidate.json';cp=t/'certificate.json'
 def run(dd,cc):
  dp.write_text(json.dumps(dd));cp.write_text(json.dumps(cc));return m.verify(dp,cp)
 run(d,c);count+=1
 dd=copy.deepcopy(d);dd['prose_only']='portable metadata';run(dd,c);count+=1
 # Formatting changes preserve canonical payload binding.
 dp.write_text(json.dumps(d,indent=1));cp.write_text(json.dumps(c));m.verify(dp,cp);count+=1
 cases=[('payload profile',lambda dd,cc:dd['profile'].__setitem__('1',dd['profile']['1']+1)),('width inventory',lambda dd,cc:cc['inventory'].__setitem__('7',cc['inventory']['7']+1)),('normalization',lambda dd,cc:cc['rhs_per_replica'].__setitem__(0,'673')),('root endpoint',lambda dd,cc:cc['root_interval'].__setitem__(1,'1/500')),('dual dimension',lambda dd,cc:cc['dual_by_constraint'].pop()),('negative primal',lambda dd,cc:cc['basis'][0].__setitem__('amount_per_replica','-1'))]
 for name,change in cases:
  dd=copy.deepcopy(d);cc=copy.deepcopy(c);change(dd,cc)
  try:run(dd,cc)
  except ValueError:count+=1
  else:raise RuntimeError('accepted '+name)
print('PASS_CEILING_CONTROLS',count)
