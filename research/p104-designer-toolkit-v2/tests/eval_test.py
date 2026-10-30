#!/usr/bin/env python3
"""Tests for `tk eval` / `tk accept` (TKBULK).  usage: tests/eval_test.py [--quick] [--heavy] [--out DIR]
 --quick  (default, single core, ~1-2 min warm; the first run on a cold nativepairs cache is ~3.5 min per new word family):
          eval --no-pipeline reproduces the published kappa of 5551 5553 5561 5569 5580, every record accepted by the real price.run (cross-checked
          against the fast exact price), resumability (second call skips), a crashing/illegal word becomes an error/illegal record, summary sorted by kappa,
          tk accept == the cached full real-stack result on the public words (when .cache/real_* exists), pluggable screen registry.
 --heavy  the full pipeline: 5561 climbs to >= .0030818185 via the 706 hand-off; 5569 reaches #5580's .0030818950 (evretime K2/MAXM0); fixed point reached.
          Single-threaded CP-SAT: expect tens of minutes; queued by cpuq/pending/TKBULK_accept.sh."""
import sys,os,json,gzip,subprocess,tempfile,copy,glob
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD)
PY=sys.executable; fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def tk(*a,timeout=7200):
    r=subprocess.run([PY,'-B',os.path.join(TKD,'tk.py')]+list(a),capture_output=True,text=True,timeout=timeout); return r.returncode,r.stdout+r.stderr
A=sys.argv[1:]; heavy='--heavy' in A; quick='--quick' in A or not heavy
out=A[A.index('--out')+1] if '--out' in A else tempfile.mkdtemp()
rec=lambda d,nm:json.load(open('%s/records/%s.json'%(d,nm)))
PUB={'5551':'0.0030415311671','5553':'0.0030428242623','5561':'0.0030814243338','5569':'0.0030818185152','5580':'0.0030818949686','5599':'0.0030983935221'}
if quick:
    d=out+'/q'
    rc,o=tk('eval',*PUB,'--no-pipeline','--out',d)
    need(rc==0,'eval 5551 5553 5561 5569 5580 5599 --no-pipeline exits 0')
    for w,k in PUB.items():
        r=rec(d,w)
        need(r['status']=='done' and r['legal'] and r['kappa_before'].startswith(k) and r.get('expected_match') and r['accepted_before'] and r['initial']['crosscheck'] in (True,None),'%s: legal, kappa_before %s (published), real price.run accepts, interval == fast price'%(w,k))
    rc,o=tk('eval',*PUB,'--no-pipeline','--out',d); need(o.count('skip ')==len(PUB),'resumable: second call skips all finished records')
    s=o[o.index('word '):].splitlines()[1:]; ks=[float(l.split()[5]) for l in s if len(l.split())>5]
    need(ks==sorted(ks,reverse=True) and len(ks)>=len(PUB),'summary table sorted by final kappa (descending)')
    # robustness: illegal word -> illegal record; missing file -> error record; neither aborts the batch
    src=json.load(gzip.open(os.path.join(TKD,'words/5551.json.gz'),'rt')); src['final'][300]=src['initial'][300]
    bad=out+'/bad.json.gz'; json.dump(src,gzip.open(bad,'wt'))
    rc,o=tk('eval',bad,'/nonexistent/word.json.gz','5551','--no-pipeline','--out',d);
    rb=[json.load(open(f)) for f in glob.glob(d+'/records/bad_*.json')]; rn=[json.load(open(f)) for f in glob.glob(d+'/records/word_*.json')]
    need(rc==0 and rb and rb[0]['status']=='illegal' and not rb[0]['legal'] and rb[0]['initial']['violations'],'illegal word -> status illegal with the localised violation, batch continues')
    need(rn and rn[0]['status']=='error' and rn[0]['errors'],'missing word -> status error record (no abort)')
    need(rec(d,'5599')['initial']['profile']=='p5599' and rec(d,'5599')['initial']['side_ok'],'5599: per-word compiler profile (decay 39/40) -> side ok')
    # tk accept == full real stack (cached results of price --real)
    import tkcommon as T
    for w in ('5551','5553','5561','5569','5580','5545'):
        p=T.resolve(w); c,_=T.cache_get('real',p)
        if not c: print('SKIP accept-vs-real %s (no cached real run)'%w); continue
        rc,o=tk('accept',w); a=json.loads(o[o.index('{'):o.rindex('}')+1])
        if 'interval' in c: need(a['ok'] and a['crossing_lo'].rstrip('0')==c['crossing_lo'].rstrip('0') and a['crossing_hi'].rstrip('0')==c['crossing_hi'].rstrip('0'),'accept %s == real stack (crossing %s)'%(w,c['crossing_lo']))
        else: need(not a['ok'] and c['error'].split(': ',1)[1][:40] in a['error'],'accept %s rejects with the real stack message (%s)'%(w,c['error'][:50]))
    # screen registry is pluggable
    import eval as E
    E.register('noop',lambda ctx,cur,base:(None,dict(note='noop'))); need('noop' in E.SCREENS and {'handoff','evretime','retime'}<=set(E.SCREENS),'screen registry: handoff/evretime/retime + user-registered screens')
if heavy:
    d=out+'/h'
    rc,o=tk('eval','5561','5569','5580','--out',d,'--rounds','4','--tl','1800','--ev-threads','2','--jobs','1')
    r1,r2=rec(d,'5561'),rec(d,'5569')
    need(float(r1['kappa_after'])>=0.0030818185 and r1['accepted_after'],'5561 pipeline climbs to >= .0030818185 via the 706 hand-off (got %s)'%r1['kappa_after'])
    need(any(m['screen']=='handoff' for m in r1['moves_applied']),'5561: a hand-off step was applied')
    need(float(r2['kappa_after'])>=0.0030818949 and r2['accepted_after'],'5569 reaches #5580 .0030818950 (got %s)'%r2['kappa_after'])
    need(r1.get('fixed_point') and r2.get('fixed_point'),'both runs reached a fixed point')
print('\n%d checks, %d failed'%(n,len(fails))); sys.exit(1 if fails else 0)
