#!/usr/bin/env python3
"""tk backtest: public P104-line words and moves.   usage: backtest.py A|B|all [--out DIR] [--real]
 A = price/check fidelity per word: fast `tk price` crossing interval vs (i) the PR's published interval/claim (TKAUDIT/src/res/*.json, searched for
     *root_interval*/*crossing*), (ii) with --real the unmodified real stack interval (cached; run via hq, ~4 min/word); `tk check` LEGAL.
     Mutation testing (check vs real verifier) is tests/fuzz_real.py (queued overnight, see TKAUDIT/CPU-RUN.md).
 B = rediscovery: run the matching tk screen on A and test that B's kappa appears.  Each step prints the command, exit code and a PASS/MISS verdict by
     matching the target kappa digits in the screen's output; the raw tail is stored so a human can confirm.  MISS root causes go in TKAUDIT/NOTES.md."""
import sys,os,json,subprocess,re
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..','tk'); W=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RES=W + '/ext/TKAUDIT/src/res'
WORDS=['5545','5551','5553','5561','5565','5569','5580']
TARGET={'5545':'.0030411718','5551':'.0030415311','5553':'.0030428242','5561':'.0030814243','5565':'.0030419514','5569':'.0030818185','5580':'.0030818949'}
STEPS=[('5551->5553 two hand-offs','5551',['handoff','5551','--inline'],'.0030428242'),
       ('5551->5561 retime','5551',['retime','5551','--free','starts,finals','--tl','600','--wait','--name','bt_rt'],'.0030814243'),
       ('5561->5569 hand-off','5561',['handoff','5561','--inline'],'.0030818185'),
       ('5551->5565 commuting-read contact','5551',['evretime','5551','--k','2','--maxm','0','--tl','900','--wait','--name','bt_ev5565'],'.0030419514'),
       ('5569->5580 ADD-chart step','5569',['evretime','5569','--k','2','--maxm','0','--tl','900','--wait','--name','bt_ev5580'],'.0030818949')]
def tk(*a):
    r=subprocess.run([TK]+list(a),capture_output=True,text=True); return r.returncode,r.stdout+r.stderr
def intervals(n):
    import glob
    f=RES+'/%s.json'%n; found=[]
    if not os.path.exists(f): return found
    def walk(o,p=''):
        if isinstance(o,dict):
            for k,v in o.items(): walk(v,p+'/'+k)
        elif isinstance(o,list) and len(o)==2 and ('root_interval' in p or 'crossing' in p) and isinstance(o[0],str): found.append((p,o))
    walk(json.load(open(f))); return found
def partA(real):
    from fractions import Fraction as Q
    rows=[]
    for n in WORDS:
        rc,o=tk('price',n,'--json'); j=json.JSONDecoder().raw_decode(o[o.index('{'):])[0] if '{' in o else {}
        rc2,o2=tk('check',n); lo,hi=j.get('crossing_lo'),j.get('crossing_hi')
        row=dict(word=n,legal=rc2==0,kappa=j.get('kappa'),lo=lo,hi=hi,published=None,price_match=None,real=None)
        for p,iv in intervals(n):
            a,b=Q(iv[0]),Q(iv[1]); row['published']=[float(a),float(b)]
            row['price_match']=bool(row['price_match']) or bool(lo and abs(float(a)-float(lo))<1e-14 and abs(float(b)-float(hi))<1e-14)
        if row['published'] is None: row['price_match']=(j.get('kappa') or '').startswith(TARGET[n][:-1]) if j else False; row['note']='no interval in RESULT.json; compared to headline digits'
        if real:
            rc3,o3=tk('price',n,'--real','--wait'); m=re.search(r'"crossing_lo": "([0-9.]+)"',o3); row['real']=m.group(1) if m else o3[-200:]
            row['real_match']=bool(m) and m.group(1)==lo
        rows.append(row); print(json.dumps(row),flush=True)
    return rows
def partB():
    rows=[]
    for name,a,cmd,tgt in STEPS:
        rc,o=tk(*cmd); ok=tgt in o or tgt[:-1] in o
        row=dict(step=name,cmd=' '.join(cmd),rc=rc,verdict='PASS' if ok else 'MISS',target=tgt,tail=o.strip().splitlines()[-12:]); rows.append(row); print(json.dumps(row),flush=True)
    return rows
if __name__=='__main__':
    A=sys.argv[1:]; what=A[0] if A else 'all'; out=A[A.index('--out')+1] if '--out' in A else W + '/ext/TKAUDIT/backtest'
    os.makedirs(out,exist_ok=True); res={}
    if what in('A','all'): res['A']=partA('--real' in A)
    if what in('B','all'): res['B']=partB()
    json.dump(res,open(out+'/backtest_%s.json'%what,'w'),indent=1)
    bad=[r for r in res.get('A',[]) if not r['legal'] or r['price_match'] is False or r.get('real_match') is False]
    sys.exit(1 if bad else 0)
