"""Literal mutation controls through the inherited arbitrary-input transport."""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,os,subprocess,sys,tempfile
from delay_release import build
from sources.staged_pair import cleanup
P=Path(__file__).parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--transport',type=Path,required=True);a=ap.parse_args();rows=[]
 with tempfile.TemporaryDirectory(prefix='four-lead1-controls-') as td:
  t=Path(td)
  for provider in ('base','extra'):
   old=json.load(gzip.open(P/'sources'/f'STAGED644-660-{provider}.json.gz'));x,_=build(old)
   for name in ('valid','omit-release-644','wrong-sign-644','omit-release-660','wrong-sign-660'):
    y=copy.deepcopy(x)
    if name!='valid':
     h=644 if name.endswith('644') else 660;d,q=(640,2) if h==644 else (656,-1)
     idx=next(i for i,g in enumerate(y['B']) if g[:5]==['add',d,h,q,1])
     if name.startswith('wrong-sign'):y['B'][idx][3]*=-1
     else:
      y['B'].pop(idx)
      for rec in y['warps']:
       if rec[0]>idx:rec[0]-=1
     y['cleanup']=cleanup(y)
    word=t/f'{provider}-{name}.json.gz';word.write_bytes(gzip.compress(json.dumps(y,separators=(',',':')).encode(),mtime=0));out=t/f'{provider}-{name}'
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    r=subprocess.run([sys.executable,'-B',str(a.transport.resolve()),str(word),str(out)],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    text=r.stdout.decode();assert (r.returncode==0)==(name=='valid'),(name,text)
    if name!='valid':assert 'arbitrary-input endpoint' in text,(name,text)
    rows.append(dict(provider=provider,control=name,exit_code=r.returncode,endpoint_rejected=name!='valid',log_sha256=hashlib.sha256(r.stdout).hexdigest()))
 print(json.dumps(dict(status='PASS_SOURCE_BOUND_ENDPOINT_CONTROLS',transport_sha256=hashlib.sha256(a.transport.read_bytes()).hexdigest(),checks=rows),indent=2))
if __name__=='__main__':main()
