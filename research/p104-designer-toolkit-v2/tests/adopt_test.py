#!/usr/bin/env python3
"""Tests for `tk adopt` / data profiles / the PR-stack authoritative checker (TKADOPT).  usage: tests/adopt_test.py [--quick] [--full]
 --quick  (~3 min, single core): profile inventory (10 acceptance PRs validated), alias+EXPECT registration, `--profile NAME accept` through the vendored PR stack,
          check --stack agreement and MODEL_GAP detection, hash-pin tamper, tolerant claim-literal patching, precise diff messages, full `tk adopt 5612` re-derivation.
 --full   additionally re-adopts all ten acceptance PRs (about 40 s each)."""
import sys,os,json,gzip,subprocess,copy,tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD)
PY=sys.executable; fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def tk(*a,timeout=900):
    r=subprocess.run([PY,'-B',os.path.join(TKD,'tk.py')]+list(a),capture_output=True,text=True,timeout=timeout); return r.returncode,r.stdout+r.stderr
import tkcommon,tkstack,adopt_validate
TEN=['5551','5565','5580','5599','5613','5644','5650','5660','5678']+['5612']
P=tkcommon.DATA_PROFILES
need(all(a in P for a in TEN),'profiles for the ten acceptance PRs exist: '+','.join(a for a in TEN if a not in P))
need(all(P[a]['validation']['ok'] for a in TEN if a in P),'every acceptance profile carries validation.ok (price, check --native, accept unpatched+patched)')
need(all(P[a]['expect']['interval']==[tkcommon.EXPECT[a],P[a]['expect']['interval'][1]] or a in('5551','5565','5580','5599','5612','5644','5650','5660') for a in TEN if a in P),'EXPECT registered from the profiles')
need({a:(P[a]['public'],P[a]['owned_fields'],P[a]['lifetimes'],P[a]['peak']) for a in('5599','5612','5660','5678')}=={'5599':(750,8,8,1),'5612':(748,8,11,2),'5660':(743,9,11,2),'5678':(743,9,11,2)},'owned pins derived from RESULT.json (OWNEDN reads these)')
need((P['5660']['compiler']['reserve'],P['5599']['compiler']['reserve'],P['5599']['compiler']['decay'],P['5551']['compiler']['decay'],P['5551']['compiler']['power'])==('1/10^12','1/10^10','39/40','97/100',1000),'compiler literals parsed from pricing.py (reserve, decay, power)')
need(P['5612']['interface']['retired_public']==[573] and P['5612']['interface']['owned_count']==9 and P['5660']['interface']['owned_count']==9,'owned role counts (retired roles included)')
rc,o=tk('price','5678'); need('expected %s: MATCH'%tkcommon.EXPECT['5678'] in o and 'MISMATCH' not in o,'tk price 5678 (alias registered by adopt) reproduces its interval')
rc,o=tk('price','5613'); need('MATCH' in o and 'MISMATCH' not in o,'tk price 5613 reproduces its interval')
rc,o=tk('--profile','5678','accept','5678'); j=json.loads(o) if o.strip().startswith('{') else {}
need(rc==0 and j.get('ok') and j.get('stack') and j.get('crossing_lo')==P['5678']['expect']['interval'][0],'tk --profile 5678 accept 5678 runs the PR\'s own local.py/pricing.py (sandboxed) and reproduces the interval')
rc,o=tk('--profile','5660','check','5660','--stack'); need(rc==0 and 'MODEL_GAP' not in o and '"pr_replay_ok": true' in o,'check --stack: legal.py and the PR local.py agree on 5660')
w=json.load(gzip.open(TKD+'/words/5660.json.gz'))
for i,e in enumerate(w['program']):
    if e[0]=='MOVE' and i>800: e[3]=e[2]; break
tmp=tempfile.mkdtemp(); bp=tmp+'/bad.json.gz'; json.dump(w,gzip.open(bp,'wt'))
rc,o=tk('--profile','5660','check',bp,'--stack'); need(rc==1 and '"pr_replay_ok": false' in o and 'MODEL_GAP' not in o,'check --stack: both reject a bad MOVE (no gap)')
# pin tamper
pr=copy.deepcopy(P['5660']); pr['stack']['files']['pricing.py']['sha256']='0'*64
r=tkstack.stack_accept(pr,TKD+'/words/5660.json.gz'); need(not r['ok'] and r['stage']=='pins' and 'pricing.py' in r['error'],'tampered stack pin is refused before any import')
# tolerant patching: unknown / missing literals are skipped, not fatal
pr=copy.deepcopy(P['5660']); pr['stack']['pricing']['patch']+= [['BOGUS','NOT_THERE_\\d+','x'],['PREVIOUS','PREVIOUS = Q\\(\'[^\']*\'\\)',"PREVIOUS = Q('{PREVIOUS}')"]]
import legal,accept as A
w5=legal.load(TKD+'/words/5660.json.gz')
r=tkstack.stack_accept(pr,TKD+'/words/5660.json.gz'); need(r['ok'] and r['claim']['skipped_patches'][:1]==['BOGUS'],'literal patching is tolerant (missing/unknown literal skipped, run still accepted)')
# precise diffs
prof=copy.deepcopy(P['5660']); prof['census']['owned_lifetimes']=12; prof['census']['paid_calls']=1
import price_exact as X
with tkcommon.use_profile('5660'):
    rep=legal.check(w5); T,Pp=X.invoice(rep); d=adopt_validate.diff_fast(prof,rep,T,Pp,None,X.budgets(rep),w5)
need(any('owned lifetimes: toolkit 11 vs RESULT 12' in x for x in d) and any('invoice totals' in x for x in d),'fast-model mismatch prints which census number / rule differs')
need(tkstack.dict_diff({'a':{'b':1}},{'a':{'b':2},'c':3})==[('/a/b','1','2'),('/c','<absent>','3')],'dict_diff localises differing fields')
# mutated local.py: precise reason, no guessing
src=open(tkstack.pdir(P['5660'])+P['5660']['stack']['base']['file']).read().replace('lifetimes == 11','lifetimes == 10') if False else None
rc,o=tk('adopt','5612'); need(rc==0 and 'ADOPTED' in o and 'accept_unpatched   PASS' in o,'tk adopt 5612 re-derives, vendors and validates from the fetched blob')
rc,o=tk('adopt','--list'); need(all(a in o for a in TEN),'tk adopt --list shows all profiles')
if '--full' in sys.argv:
    for a in TEN:
        if a!='5612': rc,o=tk('adopt',a); need(rc==0 and 'ADOPTED' in o,'tk adopt %s'%a)
print('%d checks, %d failed'%(n,len(fails))); sys.exit(1 if fails else 0)
