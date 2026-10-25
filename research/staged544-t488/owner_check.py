"""Portable streaming adapter for the retained PR3734 physical owner audit.
Retained owner audit adapted from credited PR3638 predicates; byte-identical source vendored.
This adapter changes only input location and derives T from order. All predicates and controls remain.
"""
import argparse,gzip,json,hashlib,re,itertools,time
from pathlib import Path
if not __debug__:raise RuntimeError("assertions must be enabled")
def row_stream(path,metadata):
 dec=json.JSONDecoder()
 with gzip.open(path,'rt')as f:
  buf=''
  while True:
   match=re.search(r'"rows"\s*:\s*\[',buf)
   if match:break
   chunk=f.read(65536)
   if not chunk:raise ValueError('missing rows')
   buf+=chunk
  prefix=buf[:match.start()];metadata.update(json.loads(prefix+'"rows":[]}'));buf=buf[match.end():];pos=0;delimiter=False;after_comma=False
  while True:
   while True:
    while pos<len(buf)and buf[pos]in' \r\n\t':pos+=1
    if pos<len(buf):break
    buf=f.read(65536);pos=0
    if not buf:raise ValueError('unterminated rows')
   if delimiter and buf[pos]!=']':
    if buf[pos]!=',':raise ValueError('missing row separator')
    pos+=1;delimiter=False;after_comma=True;continue
   if buf[pos]==']':
    if after_comma:raise ValueError('trailing comma')
    tail=buf[pos+1:]+f.read();final=json.loads(prefix+'"rows":[]'+tail);assert {k:v for k,v in final.items()if k!='rows'}=={k:v for k,v in metadata.items()if k!='rows'};return
   try:row,end=dec.raw_decode(buf,pos)
   except json.JSONDecodeError:
    partial=buf[pos:]
    if len(partial)>1024:raise ValueError('oversized or malformed row')
    chunk=f.read(65536)
    if not chunk:raise ValueError('truncated row')
    buf=partial+chunk;pos=0
    continue
   pos=end;delimiter=True;after_comma=False;yield row
   if pos>65536:buf=buf[pos:];pos=0

class Rows:
 def __init__(self,path,count):
  self.metadata={};self.gen=row_stream(path,self.metadata);self.first=[next(self.gen),next(self.gen)];self.count=count
 def __len__(self):return self.count
 def __getitem__(self,i):return self.first[i]
 def __iter__(self):
  count=0
  for row in itertools.chain(self.first,self.gen):count+=1;yield row
  if count!=self.count:raise ValueError('literal row count differs')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=Path(__file__).parent);parser.add_argument('--output',type=Path);a=parser.parse_args();package=a.package.resolve();supplier=package/'source3734';allocation=package/'inputs';source=supplier/'owner_audit.py';expected='56405eacc7c2dd0f7834ed5d62a4db8303c71657300eb4e4bbe020319552cde1';assert sha(source)==expected,'retained source changed'
 expected_inputs={'PLAN.json.gz': 'd566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e', 'TEMPLATE.json.gz': '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e', 'NATIVE-base.json.gz': 'bfe0cc0badac6c6d18461ceea0b299162c0f280c05f81b63f11fcc06cf9180e6', 'NATIVE-extra.json.gz': 'c5eec94a64cecfd6b83de05619628ad4868e889d62a55b49973f09705cc60448'};supplier_files=[supplier/x for x in expected_inputs]
 for p in supplier_files:assert sha(p)==expected_inputs[p.name],'supplier pin mismatch'
 text=source.read_text();old="D=P/'inputs';T=360;order=read(D/'ORDER.json');dispatch=read(D/'DISPATCH.json');N=9*T";new="D=P/'inputs';order=read(D/'ORDER.json');need(len(order)%9==0,'whole replica order');T=len(order)//9;dispatch=read(D/'DISPATCH.json');N=9*T";assert text.count(old)==1;ns={'__file__':str(source),'__name__':'retained_owner_audit'};exec(compile(text.replace(old,new),str(source),'exec'),ns);ns['P']=supplier;read_original=ns['read']
 def read(path):
  if path.name in('ORDER.json','DISPATCH.json','PROFILE.json'):return read_original(allocation/path.name)
  if path.name=='FILL.json.gz':
   rows=Rows(allocation/path.name,len(read_original(allocation/'ORDER.json'))*408);return {**rows.metadata,'rows':rows}
  return read_original(supplier/path.name)
 ns['read']=read;started=time.monotonic();positive=ns['audit']();controls=ns['controls']();bindings={}
 for prefix,files,root in [('supplier',supplier_files+[source],supplier),('allocation',[allocation/x for x in('ORDER.json','DISPATCH.json','PROFILE.json','FILL.json.gz')],allocation),('checker',[Path(__file__)],Path(__file__).parent)]:
  for p in files:bindings[prefix+'/'+p.relative_to(root).as_posix()]=sha(p)
 out={'positive':positive,'controls':controls,'seconds':time.monotonic()-started,'scope':__doc__,'pins':bindings};
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':positive['status'],'replicas':positive['replicas'],'roles':positive['roles'],'physical':positive['physical'],'controls':controls,'seconds':out['seconds']},sort_keys=True))
if __name__=='__main__':main()
