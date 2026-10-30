import os,pathlib,runpy,sys
D=pathlib.Path(__file__).resolve().parent
mode=sys.argv[1]
if mode not in ('control','candidate'): raise ValueError('mode')
for key in ('P104_WORD','P104_RESULT'): os.environ.pop(key,None)
if mode=='candidate':
 for key,file in [('P104_WORD','WORD.json.gz'),('P104_RESULT','RESULT.json')]:
  os.environ[key]=str(D/'source/research/p104-helper470-twin-rung-removal'/file)
os.environ['P104_TRACE_FILE']=str(D/('caller-'+mode+'.jsonl'))
runpy.run_path(str(D/'source/research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'),run_name='__main__')
