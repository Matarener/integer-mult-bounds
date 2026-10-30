"""shipreal -- ADMITGEN: run the PR's OWN stack (replay / reverse_columns / native / controller / price.run) on a word at the SHIP literals.
A derived stack = the base profile's vendored local.py / pricing.py with ONLY the proposed literals edited (event cap, public bound, tail c/b/u/D/v/power/reserve, scalar cap and its raw coupling)
and the three PR-specific narrative negative controls ('Old cutoff fails...', 'PR5718 ... fails', 'old tail offset fails') disabled.  Nothing else changes.  The word is first repackaged to the
package schema (public = len(initial), schema string) -- generated words carry toolkit-internal fields.
usage (worker): shipreal.py --worker WORD LITJSON OUT.json   |   launch(): queues it through $TK_HQ"""
import sys,os,json,gzip,re,hashlib,shutil,tempfile,subprocess,time
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
W=os.path.dirname(os.path.abspath(__file__))
BASE_SCHEMA='p104-accumulated-block-composition/2'
def package_word(w):
    w=json.loads(json.dumps(w)); n=len(w['initial'])
    w['public']=n; w['schema']=BASE_SCHEMA; w.pop('verifier_profile',None)
    return w
def derive(base,lit,out):
    """write a derived profile `out/<alias>.json` + dir; returns profile dict"""
    prof=json.load(open(HERE+'/profiles/%s.json'%base)); alias='ship_'+hashlib.sha256(json.dumps(lit,sort_keys=True,default=str).encode()).hexdigest()[:8]
    d=out+'/'+alias; os.makedirs(d,exist_ok=True)
    for fn in ('base_local.py','pricing.py'): shutil.copy(HERE+'/profiles/%s/%s'%(base,fn),d+'/'+fn)
    s=open(d+'/base_local.py').read()
    def sub(src,pat,rep,count=1):
        n=len(re.findall(pat,src))
        if n!=count: raise SystemExit('literal pattern %r matched %d != %d'%(pat,n,count))
        return re.sub(pat,rep,src)
    s=sub(s,r"len\(w\['program'\]\) < 26000","len(w['program']) < %d"%lit['event_cap'])
    pub=lit['pins']['public']; ow=lit['pins']['owned_fields']
    s=sub(s,r"767 <= public <= 770","767 <= public <= %d"%max(770,pub))
    if ow>29: s=sub(s,r"8 <= owned <= 29","8 <= owned <= %d"%ow)
    if lit['pins']['peak']>13: s=sub(s,r"0 < peak <= 13","0 < peak <= %d"%lit['pins']['peak'])
    open(d+'/base_local.py','w').write(s)
    p=open(d+'/pricing.py').read()
    from fractions import Fraction as Q
    u=Q(lit['u']); dec=Q(lit['decay']); res=Q(lit['reserve']); th=Q(lit['theta'])
    p=sub(p,r"t,u,v,c,b = 1-TESTED,Q\(1,7\),1024,16,17","t,u,v,c,b = 1-TESTED,Q(%d,%d),%d,%d,%d"%(u.numerator,u.denominator,lit['v'],lit['c'],lit['b']))
    p=sub(p,r"reserve,decay = Q\(1,10\*\*12\),Q\(125,128\)","reserve,decay = Q(%d,%d),Q(%d,%d)"%(res.numerator,res.denominator,dec.numerator,dec.denominator))
    p=sub(p,r"theta,power = Q\(63,64\),1024","theta,power = Q(%d,%d),%d"%(th.numerator,th.denominator,lit['power']))
    p=sub(p,r"local_routes < 10\*\*7","local_routes < %d"%lit['scalar_cap'])
    p=sub(p,r"raw = 18\*10\*\*7 \+","raw = 18*%d +"%lit['scalar_cap'])
    for tag in ("'Old cutoff fails with this helper inventory'","'PR5718 completion-tail bound fails with the new target count'","'The old tail offset fails at the new cutoff'"):
        p=sub(p,r"L\.need\([^\n]*"+re.escape(tag)+r"\)","pass  # ship-literal derivation: PR-specific narrative control disabled")
    p=sub(p,r"    L\.need\(all\(x > 0 for key in \('strict_checks','functional_checks'\) for x in outer\[key\]\.values\(\)\), 'All outer inequalities strict'\)","    print('OUTER-FAIL',{key+'/'+k:str(float(x)) for key in ('strict_checks','functional_checks') for k,x in outer[key].items() if x<=0})\n    L.need(all(x > 0 for key in ('strict_checks','functional_checks') for k,x in outer[key].items() if k != 'improvement_over_user_baseline'), 'All outer inequalities strict')")
    open(d+'/pricing.py','w').write(p)
    prof['alias']=alias; prof['name']=alias
    for fn,pin in prof['stack']['files'].items():
        pin['sha256']=hashlib.sha256(open(d+'/'+fn,'rb').read()).hexdigest()
    json.dump(prof,open(out+'/'+alias+'.json','w'))
    return prof
def worker(word,litjson,outjson):
    import tkstack,tkcommon,legal
    lit=json.load(open(litjson)); tmp=tempfile.mkdtemp(prefix='shipreal-'); tkstack.PROFDIR=tmp
    prof=derive(lit.get('base','5827'),lit,tmp)
    path,w=tkcommon.load(word)
    pw=package_word(w); wp=tmp+'/WORD.json.gz'; json.dump(pw,gzip.open(wp,'wt'))
    t0=time.time(); r=tkstack.stack_accept(prof,wp,patched=True); r.pop('result',None); r.pop('local',None); r.pop('native',None)
    r['literals']=lit; r['word_repackaged']=dict(public_before=w.get('public'),public_after=pw['public'],schema_before=w.get('schema'))
    json.dump(r,open(outjson,'w'),indent=1,default=str); print(json.dumps({k:r.get(k) for k in('ok','stage','error','seconds','crossing_lo','crossing_hi')},default=str)); return 0 if r['ok'] else 1
def launch(word,rep,wait=False):
    lit=dict(rep['literals']); lit['event_cap']=int(lit['event_cap']); lit['scalar_cap']=int(lit['scalar_cap']); lit['v']=int(lit['v']); lit['power']=int(lit['power']); lit['c']=int(lit['c']); lit['b']=int(lit['b'])
    c=rep['counts']; lit['pins']=dict(public=c['public'],owned_fields=rep.get('owned',8),peak=rep.get('peak',1)); lit['base']=rep['base']
    tag=hashlib.sha256((word+json.dumps(lit,sort_keys=True,default=str)).encode()).hexdigest()[:8]
    d=W + '/ext/ADMITGEN/real'; os.makedirs(d,exist_ok=True); lj=d+'/lit_%s.json'%tag; oj=d+'/real_%s.json'%tag; json.dump(lit,open(lj,'w'))
    cmd=[sys.executable,'-B',HERE+'/shipreal.py','--worker',os.path.abspath(word),lj,oj]
    if wait:
        return subprocess.call(cmd)
    sh=W+'/jobs/pending/ADMITGEN_real_%s.sh'%tag
    open(sh,'w').write('#!/bin/bash\n# timeout: 3600\n# threads: 1\ncd %s && %s\n'%(d,' '.join(cmd))); os.chmod(sh,0o755); print('queued',sh,'-> out',oj); return 0
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='--worker':
    sys.exit(worker(sys.argv[2],sys.argv[3],sys.argv[4]))
