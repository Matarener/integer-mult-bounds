"""tk adopt PR# [--head SHA] [--pkg research/DIR] [--alias NAME] [--no-accept] [--no-vendor] [--json] [--list]

Automatic verifier adoption.  Fetches the PR head READ-ONLY into $TK_WORK/ext/adopt/g.git (bare, no worktrees; refs/pr/N), locates the package (research/<dir>),
extracts WORD / RESULT.json / pricing.py / every local.py-like module (also inside the retained source tarballs, recursively), and DERIVES the verifier profile
from literals and the RESULT.json census -- nothing is hard-coded per PR:
    public / owned_fields / owned lifetimes / peak (RESULT local + the exit rule of the PR's local.py), retired roles + word interface (the word's own keys),
    compiler decay / log power / reserve / tail constants and the claim-literal patch regexes (pricing.py), event cap (local.py), census pins, published interval.
The authoritative checker is the PR's OWN local.py + pricing.py: candidates are tried in a sandboxed subprocess and the one whose replay / native output equals RESULT.json is
vendored (sha256 + git blob pinned) under toolkit/profiles/<alias>/stack/.  Validation then reproduces the published interval three ways (tk price fast model, check --native,
accept = the vendored stack) and on any mismatch prints which output field / rule the toolkit does not model, instead of guessing.
The profile is DATA: toolkit/profiles/<alias>.json (schema in module docstring); tkcommon registers the alias and selects it for matching words."""
import sys,os,re,json,gzip,io,tarfile,subprocess,hashlib,time,shutil,decimal
from fractions import Fraction as Q
from tkcommon import *
import tkstack
SRC=W+'/ext/adopt/g.git'
ADOPT=W+'/ext/adopt/work'
PROFDIR=HERE+'/profiles'
UPSTREAM=os.environ.get('TK_UPSTREAM','https://github.com/CrocSwap/integer-mult-bounds.git')
def git(*a,text=False,check=True,timeout=280):
    r=subprocess.run(['git','--git-dir='+SRC]+list(a),capture_output=True,timeout=timeout,env=dict(os.environ,GIT_TERMINAL_PROMPT='0'))
    if check and r.returncode: raise SystemExit('tk adopt: git %s failed: %s'%(' '.join(a[:3]),r.stderr.decode()[-300:]))
    return r.stdout.decode() if text else r.stdout
def rev(ref):
    r=subprocess.run(['git','--git-dir='+SRC,'rev-parse','--verify','--quiet',ref+'^{commit}'],capture_output=True,text=True); return r.stdout.strip() or None
def fetch(pr,head=None,refetch=False):
    """-> (ref, commit).  Local refs first (refs/pr/N, refs/heads/prN); otherwise a read-only `git fetch` of pull/N/head (or of --head SHA) from the upstream URL."""
    if head:
        c=rev(head)
        if not c:
            git('fetch','--no-tags',UPSTREAM,'+refs/pull/%d/head:refs/pr/%d'%(pr,pr) if False else head); c=rev(head)
            if not c: raise SystemExit('tk adopt: commit %s not available after fetch'%head)
        return c,c
    if not refetch:
        for ref in ('refs/pr/%d'%pr,'refs/heads/pr%d'%pr):
            c=rev(ref)
            if c: return ref,c
    git('fetch','--no-tags',UPSTREAM,'+refs/pull/%d/head:refs/pr/%d'%(pr,pr))
    c=rev('refs/pr/%d'%pr)
    if not c: raise SystemExit('tk adopt: PR %d not found'%pr)
    return 'refs/pr/%d'%pr,c
def tree(commit,pkg):
    out={}
    for l in git('ls-tree','-r','-l',commit+':'+pkg,text=True).splitlines():
        meta,name=l.split('\t',1); m=meta.split(); out[name]=(m[2],int(m[3]))
    return out
def blob(commit,path): return git('show',commit+':'+path)
def find_package(commit):
    """research/<dir> holding the WORD last touched by the PR head: the shallowest top-level WORD.json[.gz] changed by the newest commit that touches one"""
    c=git('log','-1','--format=%H',commit,'--','research/*/WORD.json.gz','research/*/WORD.json',text=True).strip()
    if not c: raise SystemExit('tk adopt: no research/*/WORD.json[.gz] in history of %s'%commit[:10])
    names=[n for n in git('show','--name-only','--format=',c,text=True).splitlines() if re.fullmatch(r'research/[^/]+/WORD\.json(\.gz)?',n)]
    if not names: raise SystemExit('tk adopt: commit %s changes no top-level package WORD'%c[:10])
    return names[0].rsplit('/',1)[0]
def safe_extract(raw,dest,depth=0,found=None):
    """extract tar(.gz) bytes into dest (regular files only, no absolute / .. paths), recursing into nested archives (depth<=3); -> list of extracted file paths"""
    found=[] if found is None else found
    if raw[:2]==b'\x1f\x8b': raw=gzip.decompress(raw)
    with tarfile.open(fileobj=io.BytesIO(raw)) as t:
        for m in t.getmembers():
            n=m.name
            if not m.isfile() or n.startswith('/') or '..' in n.split('/') or m.size>200_000_000: continue
            p=os.path.join(dest,n); os.makedirs(os.path.dirname(p),exist_ok=True); data=t.extractfile(m).read(); open(p,'wb').write(data); found.append(p)
            if depth<3 and re.search(r'\.(tar|tgz|tar\.gz)$',n):
                try: safe_extract(data,p+'.x',depth+1,found)
                except Exception: pass
    return found
def is_local_like(path):
    b=os.path.basename(path)
    return b.endswith('.py') and ('local' in b)
def find_cost(d,depth=0):
    """the dict that carries the priced receipt (raw_root_interval + productive_fields): RESULT['complete_cost'], RESULT['result'], or the top level -- searched breadth-first"""
    if not isinstance(d,dict) or depth>3: return None
    if 'raw_root_interval' in d and 'productive_fields' in d: return d
    for k in sorted(d,key=lambda k:(k not in('complete_cost','result','price','costs'),k)):
        r=find_cost(d[k],depth+1)
        if r: return r
    return None
def parse_result(commit,pkg,files):
    """-> (file name, RESULT dict, priced-receipt dict).  RESULT.json first, then FULL-RESULT.json / VERIFY-RESULT / any *RESULT*.json at the package top level"""
    names=[n for n in ('RESULT.json','FULL-RESULT.json') if n in files]+sorted(n for n in files if '/' not in n and n.endswith('.json') and 'RESULT' in n and n not in('RESULT.json','FULL-RESULT.json'))
    for n in names:
        d=json.loads(blob(commit,pkg+'/'+n)); cc=find_cost(d)
        if cc: return n,d,cc
    raise SystemExit('tk adopt: no result JSON with a priced receipt (raw_root_interval) in %s; looked at %s'%(pkg,names))
def interval14(raw):
    """published 1e-14 crossing interval (lo,hi) from the exact rationals"""
    D=decimal.Decimal; decimal.getcontext().prec=40
    f=lambda s:(D(Q(s).numerator)/D(Q(s).denominator))
    return ['%.14f'%f(raw[0]),'%.14f'%f(raw[1])]
def parse_pricing(src):
    """literals of the PR's pricing.py -> compiler constants + the claim-literal patch regexes (each must match exactly once)"""
    out={}; notes=[]
    m=re.search(r"reserve,\s*decay\s*=\s*Q\(1,\s*10\*\*(\d+)\),\s*Q\((\d+),\s*(\d+)\)",src)
    if m: out['reserve']='1/10^%s'%m.group(1); out['reserve_f']=10.0**-int(m.group(1)); out['decay']='%s/%s'%(m.group(2),m.group(3)); out['decay_f']=int(m.group(2))/int(m.group(3))
    else: notes.append('reserve/decay literal line not found')
    m=re.search(r"theta,\s*power\s*=\s*Q\((\d+),\s*(\d+)\),\s*(\d+)",src)
    if m: out['theta']='%s/%s'%(m.group(1),m.group(2)); out['power']=int(m.group(3))
    else: notes.append('theta/power literal not found')
    m=re.search(r"t,u,v,c,b\s*=\s*[^,]+,\s*Q\((\d+),(\d+)\),\s*(\d+),\s*(\d+),\s*(\d+)",src)
    if m: out['tail']=dict(u='%s/%s'%(m.group(1),m.group(2)),v=int(m.group(3)),c=int(m.group(4)),b=int(m.group(5)))
    m=re.search(r"local\['real_scalar_allowance'\]\+local_routes\s*<\s*10\*\*(\d+)",src)
    out['scalar_cap']=10**int(m.group(1)) if m else None
    m=re.search(r"local_routes\s*=\s*(\(.*?\)\*1000)",src)
    out['routes']=m.group(1) if m else None
    m=re.search(r"len\(outer\['strict_checks'\]\)\s*==\s*(\d+)\s*and\s*len\(outer\['functional_checks'\]\)\s*==\s*(\d+)",src)
    if m: out['outer']=[int(m.group(1)),int(m.group(2))]
    patch=[]
    for name,pat,tmpl in (('KAPPA_TESTED',r"KAPPA, TESTED = Q\('[^']*'\), Q\('[^']*'\)","KAPPA, TESTED = Q('{KAPPA}'), Q('{TESTED}')"),
                          ('COUNTS',r"sum\(targets.values\(\)\) == \d+ and sum\(paid.values\(\)\) == \d+","sum(targets.values()) == {sumT} and sum(paid.values()) == {sumP}"),
                          ('SURPLUS',r"== 760,","== {surplus},")):
        c=len(re.findall(pat,src))
        if c==1: patch.append([name,pat,tmpl])
        else: notes.append('claim literal %s matches %d times (expected 1): candidate words can only be run unpatched'%(name,c))
    prevs=sorted(re.findall(r"^(\w*PREVIOUS\w*) = Q\('([^']*)'\)",src,re.M),key=lambda t:Q(t[1]))      # every 'previous record' literal, kept in its original order but moved below any candidate's kappa
    for i,(nm,v) in enumerate(prevs): patch.append(['PREV_'+nm,nm+r" = Q\('[^']*'\)",nm+" = Q('{PREV_%d}')"%i])
    if not prevs: notes.append('no PREVIOUS literal found (candidate words run unpatched only)')
    out['patch']=patch; out['notes']=notes
    m=re.search(r"KAPPA, TESTED = Q\('([^']*)'\)",src); out['kappa_literal']=m.group(1) if m else None
    return out
def parse_local_rules(src):
    """exit rule / caps / pins from a PR's local.py (replay module source)"""
    o={}
    m=re.search(r"len\(w\['program'\]\)\s*<\s*(\d+)",src); o['event_cap']=int(m.group(1)) if m else None
    m=re.search(r"0\s*<\s*peak\s*<=\s*(\d+)",src)
    if m: o['peak_rule']='le%s'%m.group(1)
    else:
        m=re.search(r"peak\s*==\s*(\d+)",src); o['peak_rule']='eq%s'%m.group(1) if m else None
    m=re.search(r"lifetimes\s*==\s*(\d+)",src); o['lifetimes_pin']=int(m.group(1)) if m else None
    m=re.search(r"(\d+)\s*<=\s*owned\s*<=\s*(\d+)",src); o['owned_bound']=[int(m.group(1)),int(m.group(2))] if m else None
    m=re.search(r"(\d+)\s*<=\s*public\s*<=\s*(\d+)",src); o['public_bound']=[int(m.group(1)),int(m.group(2))] if m else None
    if not m:
        m=re.search(r"public\s*==\s*(\d+)",src); o['public_bound']=[int(m.group(1))]*2 if m else None
    return o
def word_interface(w):
    return dict(retired_public=list(w.get('retired_public') or []),owned_roles=w.get('owned_roles'),fields=w.get('fields'),
                independent_public=len(w['independent_public']) if w.get('independent_public') else None,schema=w.get('schema'))
NATIVE_KEYS=('distinct_maps','main_adapters','helper_normalizers','helpers')
def adopt(pr,head=None,pkg=None,alias=None,vendor=True,do_accept=True,refetch=False,say=print):
    t0=time.time(); alias=alias or str(pr); rec=dict(alias=alias,pr=pr,steps={},unmodelled=[])
    ref,commit=fetch(pr,head,refetch); say('fetched %s -> %s'%(ref,commit[:12]))
    pkg=pkg or find_package(commit); say('package %s'%pkg)
    files=tree(commit,pkg); wname='WORD.json.gz' if 'WORD.json.gz' in files else 'WORD.json'
    rname,res,cc=parse_result(commit,pkg,files)
    wraw=blob(commit,pkg+'/'+wname); wpath=ADOPT+'/%s/%s'%(alias,wname); os.makedirs(os.path.dirname(wpath),exist_ok=True); open(wpath,'wb').write(wraw)
    w=json.load(gzip.open(wpath)) if wname.endswith('.gz') else json.load(open(wpath))
    wsha=hashlib.sha256(wraw).hexdigest()
    pricing_src=blob(commit,pkg+'/pricing.py').decode()
    # ---- candidate verifier modules: package files + every nested retained archive
    cands={}      # sha -> (path, origin)
    base=ADOPT+'/%s/pkg'%alias; shutil.rmtree(base,ignore_errors=True)
    # package pool: this package, then every sibling research/p104-* package its verify/sources/construct text names (a PR may import its parent's retained sources), breadth-first, <=6 packages
    allpk=set(git('ls-tree','--name-only',commit+':research/',text=True).split())
    pool=[(pkg,0)]; seen={pkg.split('/')[-1]}
    for q,dq in pool:
        if len(pool)>=6: break
        ft=files if q==pkg else tree(commit,q)
        txt=''.join(blob(commit,q+'/'+n).decode('utf8','replace') for n in ('verify.py','sources.py','common.py') if n in ft)
        for nm in re.findall(r"p104-[a-z0-9-]+",txt):
            if nm in allpk and nm not in seen and len(pool)<6: seen.add(nm); pool.append(('research/'+nm,dq+1))
    for q,dq in pool:
        ft=files if q==pkg else tree(commit,q)
        for n,(bid,sz) in ft.items():
            if '/' in n and not n.startswith('inputs/'): continue
            if n.endswith('.py') or re.search(r'\.(tar|tgz|tar\.gz)$',n):
                p=base+'/%d/%s/%s'%(dq,q.split('/')[-1],n); os.makedirs(os.path.dirname(p),exist_ok=True); data=blob(commit,q+'/'+n); open(p,'wb').write(data)
                if re.search(r'\.(tar|tgz|tar\.gz)$',n):
                    for qq in safe_extract(data,p+'.x'):
                        if is_local_like(qq): cands.setdefault(hashlib.sha256(open(qq,'rb').read()).hexdigest(),(qq,'archive %s/%s :: %s'%(q.split('/')[-1],n,os.path.relpath(qq,p+'.x'))))
                elif is_local_like(p): cands.setdefault(hashlib.sha256(data).hexdigest(),(p,'package %s/%s'%(q.split('/')[-1],n)))
    rec['candidates']=[(o,s[:10]) for s,(p,o) in cands.items()]
    # the capsule local.py of the workspace closure (n-patched) as the last resort for the PR5551..5580 family (their archive/closure supplies it)
    import real as R
    if not any('productive-controller' in p for p,o in cands.values()):
        cl=closure_root()+'/research/p104-productive-controller/local.py'
        if os.path.exists(cl): cands.setdefault(hashlib.sha256(open(cl,'rb').read()).hexdigest(),(cl,'workspace closure (PR5545 capsule)'))
    rl=res['local']; rn=res.get('native',{})
    rl_n=tkstack.norm(rl)
    rep_pick=None; base_pick=None; edits=[]; probes={}
    want_edits=['retired_helper'] if 'retired_helper' in rn else []
    pwords=wpath
    for sha_,(p,o) in sorted(cands.items(),key=lambda kv:(int(re.search(r'/pkg/(\d+)/',kv[1][0]).group(1)) if '/pkg/' in kv[1][0] else 9,kv[1][0].count('.x/'),'productive-controller' in kv[1][0],kv[1][0])):     # package files first, then shallower archives; the 5545 capsule last
        if base_pick and rep_pick: break
        pr_=tkstack.run_probe(p,pwords,want_edits); probes[o]=pr_
        if pr_.get('error') : continue
        if pr_.get('replay')==rl_n and not rep_pick: rep_pick=(p,o,sha_)
        nat=pr_.get('native')
        if nat is not None and not base_pick:
            exp={k:tkstack.norm(rn[k]) for k in NATIVE_KEYS if k in rn}
            if want_edits: exp['retired_helper']=rn['retired_helper']
            if all(nat.get(k)==v for k,v in exp.items()): base_pick=(p,o,sha_); edits=want_edits
    rec['steps']['probe']={o:{k:(v if k in('replay_error','native_error','error') else 'ok') for k,v in pr_.items() if k.endswith('error') or k in('replay','native')} for o,pr_ in probes.items()}
    if not rep_pick:
        rec['unmodelled'].append('no candidate local.py reproduces RESULT.json local; per-candidate diff: '+'; '.join('%s: %s'%(o,(pr_.get('error') or pr_.get('replay_error') or str(tkstack.dict_diff(pr_.get('replay',{}),rl_n))[:300])) for o,pr_ in probes.items()))
    if not base_pick:
        diffs='; '.join('%s: %s'%(o,(pr_.get('error') or pr_.get('native_error') or str(tkstack.dict_diff(pr_.get('native',{}),{k:tkstack.norm(rn[k]) for k in NATIVE_KEYS if k in rn}))[:300])) for o,pr_ in probes.items())
        rec['unmodelled'].append('no candidate native() reproduces RESULT.json native (%s)'%diffs)
    # ---- literals
    lit=parse_pricing(pricing_src); rec['unmodelled']+=lit.pop('notes')
    rules=parse_local_rules(open(rep_pick[0]).read()) if rep_pick else {}
    owned_fields=rl.get('owned_fields',w.get('owned_fields',8)); retired=list(w.get('retired_public') or [])
    prof=dict(schema='tk-profile/1',name=alias,alias=alias,pr=pr,head=commit,ref=ref,package=pkg,
        public=len(w['initial']),owned_fields=owned_fields,lifetimes=rl.get('owned_lifetimes'),peak=rl.get('peak_owned_fields'),
        family=dict(public=len(w['initial']),owned_fields=owned_fields,retired_public=retired,schema=w.get('schema'),has_owned_fields_key='owned_fields' in w),
        interface=dict(word_interface(w),peak_rule=rules.get('peak_rule'),owned_count=owned_fields+len(retired),lifetimes_pin=rules.get('lifetimes_pin'),owned_bound=rules.get('owned_bound'),public_bound=rules.get('public_bound')),
        compiler=dict(decay=lit.get('decay'),decay_f=lit.get('decay_f'),power=lit.get('power'),reserve=lit.get('reserve'),reserve_f=lit.get('reserve_f'),theta=lit.get('theta'),tail=lit.get('tail'),
                      event_cap=rules.get('event_cap'),scalar_cap=lit.get('scalar_cap'),routes=lit.get('routes'),outer=lit.get('outer')),
        census=dict(paid=tkstack.norm(cc.get('paid')),targets=tkstack.norm(cc.get('targets')),helpers=tkstack.norm(rl.get('helpers')),paid_calls=cc.get('paid_calls'),productive_fields=cc.get('productive_fields'),
                    rank_mass_surplus=cc.get('rank_mass_surplus'),owned_lifetimes=rl.get('owned_lifetimes'),peak_owned_fields=rl.get('peak_owned_fields'),public_inputs=rl.get('public_inputs'),
                    main_adapters=rn.get('main_adapters'),helper_normalizers=rn.get('helper_normalizers'),distinct_maps=rn.get('distinct_maps'),events=len(w['program']),
                    local_routes=cc.get('nonrecursive',{}).get('local_routes'),real_scalar_allowance=rl.get('real_scalar_allowance')),
        expect=dict(kappa_decimal=cc.get('kappa_decimal'),interval=interval14(cc['raw_root_interval']),raw_root_interval=cc['raw_root_interval'],word_sha256=wsha,result_file=rname),
        stack=None,fast=dict(),provenance=dict(date=time.strftime('%Y-%m-%d'),upstream=UPSTREAM,note='derived by tk adopt; no hand-typed constants'))
    # ---- vendor the authoritative stack (pinned)
    if vendor and rep_pick and base_pick:
        sd=PROFDIR+'/'+alias; shutil.rmtree(sd,ignore_errors=True); os.makedirs(sd)
        files_pin={}
        def put(src,name):
            shutil.copy(src,sd+'/'+name); data=open(src,'rb').read()
            files_pin[name]=dict(sha256=hashlib.sha256(data).hexdigest(),git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),origin=[o for p,o in cands.values() if p==src][0] if any(p==src for p,o in cands.values()) else 'package')
        bn='base_local.py'; put(base_pick[0],bn)
        if rep_pick[0]==base_pick[0]: rn_='base_local.py'
        else: rn_='replay_local.py'; put(rep_pick[0],rn_)
        open(sd+'/pricing.py','w').write(pricing_src)
        pdata=pricing_src.encode(); files_pin['pricing.py']=dict(sha256=hashlib.sha256(pdata).hexdigest(),git_blob=hashlib.sha1(b'blob '+str(len(pdata)).encode()+b'\0'+pdata).hexdigest(),origin='package pricing.py')
        prof['stack']=dict(base=dict(file=bn),replay=dict(file=rn_),native=dict(edits=edits,mode='light'),pricing=dict(file='pricing.py',patch=lit['patch']),files=files_pin,
                           root='closure',caller_root='closure')
        prof['provenance']['blobs']={n:b for n,(b,s) in files.items() if n in('pricing.py','verify.py','RESULT.json',wname,'local.py')}
    os.makedirs(PROFDIR,exist_ok=True)
    wdst=HERE+'/words/%s.json.gz'%alias
    if not os.path.exists(wdst): shutil.copy(wpath,wdst) if wname.endswith('.gz') else json.dump(w,gzip.open(wdst,'wt'))
    rec['profile']=prof; rec['seconds']=round(time.time()-t0,1); rec['word']=wpath
    return rec
def write_profile(prof):
    json.dump(prof,open(PROFDIR+'/%s.json'%prof['alias'],'w'),indent=1,sort_keys=False,default=str)
def main(a):
    if a.list:
        for f in sorted(os.listdir(PROFDIR)):
            if f.endswith('.json'): p=json.load(open(PROFDIR+'/'+f)); print('%-6s PR%-5s public %d owned %s lifetimes %s peak %s decay %s power %s reserve %s kappa %s'%(p['alias'],p['pr'],p['public'],p['owned_fields'],p['lifetimes'],p['peak'],p['compiler']['decay'],p['compiler']['power'],p['compiler']['reserve'],p['expect']['kappa_decimal']))
        return 0
    rec=adopt(a.pr,a.head,a.pkg,a.alias,vendor=not a.no_vendor,do_accept=not a.no_accept,refetch=a.refetch)
    import adopt_validate
    return adopt_validate.finish(rec,a)
