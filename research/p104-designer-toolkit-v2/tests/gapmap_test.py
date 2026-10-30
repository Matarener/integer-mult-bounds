"""TKHYG2: gapmap default = jump-level cut table; matches the SPLICE/topcost.py numbers (b0 vs 5907 spot values) and band table stays behind --bands."""
import sys,os,subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); sys.dont_write_bytecode=True
import gapmap
A=gapmap.load('5907'); c=gapmap.components(A); t=gapmap.cut_table(c['cutj'])
bad=[]
def need(x,m):
    print(('ok   ' if x else 'FAIL ')+m)
    if not x: bad.append(m)
# 5907 values from SPLICE/topcost.py (published in module docstring): cut 3 H bot 1720 top 3545; cut 7 Y bot 838 top 218
need(int(t[3]['H'][0])==1720 and int(t[3]['H'][1])==3545,'5907 cut3 H bot/top == 1720/3545')
need(int(t[7]['Y'][0])==838 and int(t[7]['Y'][1])==218,'5907 cut7 Y bot/top == 838/218')
for cc in gapmap.CUTS: need(abs(t[cc]['ALL'][0]+t[cc]['ALL'][1]+c['R0']['owned (O)']-c['total'])<1e-6,'cut %d: below+above+owned == total R0'%cc)
o=subprocess.run([sys.executable,'-B',TK+'/gapmap.py','5907','5907','--no-struct'],capture_output=True,text=True).stdout
need('JUMP-LEVEL CUT TABLE' in o and 'MID-DIM' not in o,'default prints cut table only')
o=subprocess.run([sys.executable,'-B',TK+'/gapmap.py','5907','5907','--no-struct','--bands'],capture_output=True,text=True).stdout
need('MID-DIM BAND TABLE' in o and 'NOT a dimension cut' in o,'--bands prints the labelled legacy table')
# ENDANATOMY: owned staging + law reproduces tk price kappa (5e-5 fit on 11 words; test tolerance 2e-4) on the swarm word, our best scratch word and the owned-end milestone
import re
C=os.path.join(TK,'ext')
stage={}
for name,spec,exp in (('5907','5907',40.1524),('r104',C+'/PUREX/r104.json.gz',0.0),('m2',C+'/OWNEDRANK/m2.json.gz',9.5607)):
    if not os.path.exists(spec) and spec!='5907': print('skip',name); continue
    w=gapmap.load(spec); c=gapmap.components(w); st=c['owned']
    need(abs(st['staging']-exp)<1e-3,'%s owned staging %.4f == %.4f'%(name,st['staging'],exp))
    need(abs(c['R0']['owned (O)']-st['staging'])<1e-9,'%s O row == staging'%name)
    o=subprocess.run([sys.executable,'-B',TK+'/tk.py','price',spec],capture_output=True,text=True).stdout
    k=float(re.search(r'kappa = ([0-9.e-]+)',o).group(1)); pk=gapmap.pred_kappa(c['total'],st['paid'])
    need(abs(pk/k-1)<2e-4,'%s law kappa %.9f vs tk price %.9f (rel %.1e)'%(name,pk,k,pk/k-1))
    if name=='5907':   # the legacy O row (per register id) would put the law ~1.8e-3 off on the swarm word; staging is what the law needs
        pl=gapmap.pred_kappa(c['total']-st['staging']+c['owned_legacy_O']); need(abs(pl/k-1)>1e-3,'legacy O row misses (rel %.1e)'%(pl/k-1))
sys.exit(1 if bad else 0)
