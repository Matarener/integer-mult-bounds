"""ADMITGEN: tk shipcheck smoke test (verdict classes, minimal literals, derived-stack patch anchors)."""
import sys,os,json,tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
W=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import shipcheck as S, shipreal as R
bad=[]
def need(ok,why):
    print(('ok   ' if ok else 'FAIL ')+why)
    if not ok: bad.append(why)
a=W + '/ext/K2SEARCH/CANDIDATE-k2s5827-1.json.gz'; g=W + '/ext/GENPIPE/runs/gp2-jf_V0/final.json.gz'
if os.path.exists(a):
    r=S.analyse(a); need(r['verdict'] in ('SHIPPABLE AS-IS','SHIPPABLE, PRECEDENTED'),'frontier-family word is shippable (as-is or precedented literals)')
if os.path.exists(g):
    r=S.analyse(g); L=r['literals']
    need(r['verdict'].startswith('NEEDS BEYOND') and r['admissible_after'],'generated word: admissible after literal changes, caps are beyond precedent')
    need((L['v'],L['power'],L['decay'],L['theta'])==('1024','1024','125/128','63/64'),'v/power/D/theta kept at precedent values')
    need(int(L['event_cap'])==r['counts']['events']+1 and int(L['scalar_cap'])==r['counts']['scalar']+1,'caps are the least the word needs')
    lit=dict(L); 
    for k in('event_cap','scalar_cap','v','power','c','b'): lit[k]=int(lit[k])
    lit['pins']=dict(public=r['counts']['public'],owned_fields=r['owned'],peak=r['peak'])
    d=tempfile.mkdtemp(); p=R.derive('5827',lit,d); need(os.path.exists(d+'/'+p['alias']+'/pricing.py'),'derived stack builds (all literal anchors found)')
sys.exit(1 if bad else 0)
