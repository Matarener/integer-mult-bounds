"""GENSEARCH regression: spec normalisation/ids are deterministic, L1 kappa_hat of the star and grouped specs equals the known exact kappa, root_flip is kappa-neutral, resume = cache hit."""
import sys,os,json,random,tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.dirname(HERE); sys.path.insert(0,TKD); os.environ['TK_FREE_BOUNDS']='1'
from gensearch import space as S, build as B, run as R
fails=0
def need(c,m):
    global fails
    print(('ok   ' if c else 'FAIL ')+m)
    if not c: fails+=1
a=S.sample(random.Random('x/1')); b=S.sample(random.Random('x/1'))
need(a==b and S.sid(a)==S.sid(b) and S.normalize(dict(a,dil_seed=5,hs_seed=9))['back']==a['back'],'space: sampling deterministic, ids stable, inactive fields normalised')
need(S.sid(dict(back='grouped',helpers='shared'))==S.sid(dict(back='grouped')) and S.sid(dict(back='star'))!=S.sid(dict(back='gray')),'space: grouped ignores helpers; methods distinct')
tmp=tempfile.mkdtemp(); ev=R.Ev('t',path=tmp+'/r.jsonl')
r=ev.L1(dict(back='star',root_flip=0)); r2=ev.L1(dict(back='star',root_flip=0)); f=ev.L1(dict(back='star',root_flip=5))
need(abs(r['kappa_hat']-0.001021199786571)<1e-12 and r['value_ok'] and r2 is r,'L1 star kappa_hat = .001021199786571 (FRONTGEN exact), repeat = cache hit')
need(f['value_ok'] and abs(f['kappa_hat']-r['kappa_hat'])<1e-15 and f['sid']!=r['sid'],'root_flip is a kappa-neutral sign knob (distinct spec id, same invoice)')
ev2=R.Ev('t2',path=tmp+'/r.jsonl'); need(('L1',r['sid']) in ev2.rows,'resume: a new driver reloads the evaluated rows from the jsonl')
d=B.build_dag(S.normalize(dict(back='star')))[0]; z=B.r0(d)
need(abs(z['r0_help']-35838.86)<1 and z['n_help']==5832,'L0 R0 tax of the STAR word = 35.8k over 5832 helpers (GENLEARN R0)')
print('FAILS',fails); sys.exit(1 if fails else 0)
