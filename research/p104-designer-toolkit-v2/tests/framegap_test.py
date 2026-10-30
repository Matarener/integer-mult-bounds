"""FRAMEGAP: main-register endpoint frames (X final = full 9-dim space, Y initial = 0-dim; PROOF main progress 2*104*8) are enforced by legal.check, tk check, admit/shipcheck, IncrWord.
triv (BLIND/triv.json.gz, X kept at [q]) must FAIL; swarm #5907/#5827 and our generated words must pass this rule."""
import sys,os,subprocess,json,copy
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); sys.path.insert(0,TK+'/infra')
W=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); WILD=W + '/ext/'
import legal
bad=[]
def need(ok,why):
    print(('ok   ' if ok else 'FAIL ')+why)
    if not ok: bad.append(why)
def rules(w):
    os.environ.pop('TK_VERIFIER_PROFILE',None)
    return [v[1] for v in legal.check(w)['violations']]
import tempfile,gzip
_base=legal.load(os.path.join(TK,'words','5907.json.gz')); triv=copy.deepcopy(_base)
_f1=next(i for i,b in enumerate(triv['frames']) if len(b)==1); triv['final'][triv['live'][0]]=_f1      # synthetic 'triv': X kept at a 1-dim frame
TRIV=os.path.join(tempfile.mkdtemp(),'triv.json.gz'); gzip.open(TRIV,'wt').write(json.dumps(triv))
R=rules(triv); need(any(x.startswith('Main X final') for x in R),'legal.check rejects triv (X final dim 1): %s'%R[:3])
p=subprocess.run([TK+'/tk','check',TRIV],capture_output=True,text=True); need(p.returncode==1 and 'Main X final frame' in p.stdout,'tk check triv exits 1 and names the rule')
import admit as A
try:
    c=A.counts(TRIV); need(c['legal'] is False,'admit.counts (shipcheck/accept front end) reports triv NOT legal')
except Exception as e: need(False,'admit.counts on triv raised %s'%str(e)[:80])
os.environ.pop('TK_VERIFIER_PROFILE',None)      # admit.counts activates a data profile in-process; the CLI legs below must pick their own
for nm,pf in(('5907','5907'),('5827','5827')):
    p=subprocess.run([TK+'/tk','check',nm],capture_output=True,text=True); need(p.returncode==0 and ' LEGAL' in p.stdout and 'Main ' not in p.stdout,'tk check %s still LEGAL (frames spec-conform)'%nm)
sys.exit(1 if bad else 0)
