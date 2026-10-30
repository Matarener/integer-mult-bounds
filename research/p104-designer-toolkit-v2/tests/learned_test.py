"""GENLEARN regression: rule_audit on the lineage, learned modes are exact no-ops on a rule-conformant word, tightness is priced (counterfactual)."""
import sys,os,gzip,json
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.dirname(HERE); sys.path.insert(0,TKD); sys.path.insert(0,TKD+'/synth')
os.environ['TK_FREE_BOUNDS']='1'
from synth import learned as LN
fails=0
def need(c,m):
    global fails
    print(('ok   ' if c else 'FAIL ')+m)
    if not c: fails+=1
for a,tax,li in (('5561',6046.2,0),('5756',5933.0,1)):
    au=LN.rule_audit(json.load(gzip.open(TKD+'/words/%s.json.gz'%a)))
    need(au['loose_final']==0 and au['idle_stops']=={} and au['loose_init']==li and abs(au['helper_tax']-tax)<0.05 and au['d0_but_not_born_at_0']==0,'rule_audit %s: R1 tight endpoints, R2 no idle stops, R3 dim-0 users born at 0, tax %s (%s)'%(a,tax,{k:au[k] for k in('loose_init','loose_final','idle_stops','helper_tax')}))
w=json.load(gzip.open(TKD+'/words/5756.json.gz'))
need(abs(LN.tax([1,7,1])-6.1537)<1e-3 and LN.tax([9])==0 and LN.tax([8,1])<LN.tax([1,7,1]),'tax law: (1,7,1)=6.154, single hop 0')
import subprocess
r=subprocess.run([sys.executable,'-B',TKD+'/tk.py','synth','--learned','2','--anchor','5756','--helpers','learned','--schedule','learned','--seed','3'],capture_output=True,text=True)
need(r.returncode==0 and 'SUMMARY draws 2 legal 2  kappa>=base 2' in r.stdout and 'init_raised\': 0, \'final_lowered\': 0' in r.stdout,'tk synth --learned: modes are exact no-ops on #5756 (already tight), legal')
out=LN.counterfactual('5756')
need(out['both']['legal'] and out['both']['kappa']<out['anchor']['kappa']-1.5e-4 and out['late starters -> zero frame']['kappa']<out['anchor']['kappa']-1e-4,'counterfactual: loosening endpoints costs kappa (late starters -1.08e-4, both -1.84e-4)')
td=LN.tighten_demo('5756')
need(td['legal'] and td['tight']>td['loose']+1.7e-4 and abs(td['tight']-td['anchor'])<2e-6 and td['log']['init_raised']>=90 and td['log']['final_lowered']>=75,'helpers: learned tightens a fully loosened #5756 back to within 2e-6 of the anchor (two rule exceptions: first-use-at-dim-9 helper, idle helper)')
print('FAILS',fails); sys.exit(1 if fails else 0)
