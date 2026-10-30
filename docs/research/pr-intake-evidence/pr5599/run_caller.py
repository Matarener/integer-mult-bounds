import os,pathlib,runpy,sys
D=pathlib.Path(__file__).resolve().parent
if sys.argv[1] not in ('control','candidate'): raise ValueError('Choose control or candidate')
for key in ('P104_WORD','P104_RESULT'): os.environ.pop(key,None)
if sys.argv[1]=='candidate':
 os.environ['P104_WORD']=str(D/'source/research/p104-helper-subspace-splits/WORD.json.gz')
 os.environ['P104_RESULT']=str(D/'source/research/p104-helper-subspace-splits/RESULT.json')
os.environ['P104_TRACE_FILE']=str(D/('caller-'+sys.argv[1]+'.jsonl'))
runpy.run_path(str(D/'caller-source/research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'),run_name='__main__')
