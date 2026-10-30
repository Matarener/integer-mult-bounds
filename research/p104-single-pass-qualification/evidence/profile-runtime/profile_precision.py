"""Observe only complete function calls; run the frozen qualification unchanged."""
from source import baseline,require
import importlib.util,json,sys,time
from collections import defaultdict
rows=defaultdict(lambda:[0,0.0])
def observe(obj,name,label):
 original=getattr(obj,name)
 def wrapped(*args,**kwargs):
  start=time.perf_counter()
  try:return original(*args,**kwargs)
  finally:
   row=rows[label];row[0]+=1;row[1]+=time.perf_counter()-start
 setattr(obj,name,wrapped)
with baseline() as p:
 spec=importlib.util.spec_from_file_location('precision_profile',p/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 load=v.load
 def observed_load(name,path):
  m=load(name,path)
  if name=='frozen_contract':
   module=m.module
   def observed_module(n,q):
    a=module(n,q)
    if n=='noisy_precision':
     for f in ('ideal','error_trace','reverse_all','reverse_cut','execute'):observe(a,f,'Fraction.contract.'+f)
    return a
   m.module=observed_module;observe(m,'calculate','Fraction.calculate')
  elif name=='frozen_precision':
   for f in ('ideal','error_trace','reverse_all'):observe(m,f,'Fraction.extra.'+f)
  elif name=='integer_backend':
   for f in ('ideal','error_trace','reverse_all'):observe(m.Engine,f,'integer.'+f)
  elif name=='explicit_contract':observe(m,'calculate','integer.calculate')
  return m
 v.load=observed_load
 receipt,seconds=v.run('qualify');require(receipt==json.loads((p/'RESULT.json').read_bytes()),'complete frozen profile receipt')
 print(json.dumps({'receipt':receipt,'seconds':seconds,'inclusive_function_profiles':dict(rows)},sort_keys=True))
