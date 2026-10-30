#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tiny conditional endpoint refinement; unchanged paid supplier. See PROOF.md."""
import argparse,hashlib,json,pathlib,subprocess,sys,tempfile,types
from fractions import Fraction as Q
P=pathlib.Path(__file__).resolve().parent
def load_local(name):
    p=P/(name+'.py');m=types.ModuleType(name);m.__file__=str(p)
    exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
old=load_local('support');binomial=load_local('binomial');moment=binomial.moment;need=old.need
ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=P.parents[1]);ap.add_argument('--output',type=pathlib.Path);args=ap.parse_args()
need(not sys.flags.optimize,'retained validators require enabled assertions')
need(args.output is None or not args.output.exists(),'output must be fresh')
ROOT=args.root.resolve();old.authenticate(ROOT,P)
profile={1:16376940,2:4821840,3:1567431,4:679320,5:147075,8:53280,48:282569}
need(sum(r*n for r,n in profile.items())==65088*740,'complete mass')
C=Q('0.001729777494678597011886903656817803609')
K=C-Q(1,10**62)-Q(1,10**86)
prior=Q(old.read(P/'vendor/PR3361-CLAIM.json')['kappa'])
need(K>prior,'strict comparison')
lo,hi=moment(profile,C,896*740);sl,sh=moment(profile,C+Q(1,10**40),896*740)
need(hi<1<sl,'independent binomial endpoint and successor')
controls=[]
for rank in [1,48]:
    mutant=dict(profile);mutant[rank]+=1
    need(moment(mutant,C,896*740)[0]>1,'unpaid child rejected');controls.append('extra rank'+str(rank))
need(moment(profile,Q(0),896*740)==(Q(65088,65408),Q(65088,65408)),'zero exponent exact control')
need(moment(profile,Q(1,2),896*740)[0]>1,'gross overstated endpoint')
# The two retained engines are comparison checks, not claimed as our new oracle.
engines=[]
for path in [ROOT/'research/rank7-joint-endframes/tools/root.py',ROOT/'research/two-sided-helper-extraction/tools/audit_moment.py']:
    E=old.load(path,'retained_'+str(len(engines)))
    below=E.moment(profile,C,896*740);above=E.moment(profile,C+Q(1,10**40),896*740)
    need(below[1]<1<above[0],'retained engine endpoint/successor')
    engines.append(dict(source=str(path.relative_to(ROOT)),sha256=old.sha(path),below=list(map(str,below)),above=list(map(str,above))))
admission=old.read(old.BASE/'evidence/ADMISSION-RESULT.json')
patch=next(p for p in admission['patches'] if p['path']=='outer/check_ledger.py')
raw=(old.SUPPLIER/'outer/check_ledger.py').read_bytes();need(hashlib.sha256(raw).hexdigest()==patch['before_sha256'],'outer preimage')
text=raw.decode().replace('\r\n','\n')
for before,after in patch['replacements']:
    need(text.count(before)==1,'one recorded patch');text=text.replace(before,after)
need(hashlib.sha256(text.encode()).hexdigest()==patch['after_sha256'],'same admitted checker')
with tempfile.TemporaryDirectory(prefix='steak-binomial40-') as tmp:
    w=pathlib.Path(tmp);(w/'outer').mkdir();(w/'new').mkdir()
    (w/'outer/check_ledger.py').write_bytes(text.encode())
    (w/'outer/independent_check.py').write_bytes((old.SUPPLIER/'outer/independent_check.py').read_bytes())
    old.save(w/'new/SPEC.json',dict(geometry=dict(dimension=73,replicas=740),expected=dict(complex_lower=str(C),kappa=str(prior),global_profile=profile,live=896*740),outer_refinement=dict(endpoint_digits=40)))
    old.save(w/'CLAIM.json',dict(kappa=str(K),scope='Conditional precision refinement only'))
    old.save(w/'outer/B.json',dict(b=str(C-Q(1,10**120)),b_above_endpoint=str(C+Q(1,10**40)),profile=profile,live=896*740))
    for script in ['check_ledger.py','independent_check.py']:
        with (w/(script+'.log')).open('w') as log:
            subprocess.run([sys.executable,'-B','-X','pycache_prefix='+str(w/'bytecode'),str(w/'outer'/script)],check=True,stdout=log,stderr=subprocess.STDOUT)
    ledger=old.read(w/'outer/LEDGER.json');independent=old.read(w/'outer/INDEPENDENT.json')
    row=ledger['rows']['struct_boundary_radix_union']
    need(Q(row['kappa']['rational'])==K,'derived kappa')
    need(len(row['strict_checks'])==63 and all(Q(v['rational'])>0 for v in row['strict_checks'].values()),'all 63 inequalities')
    rejects=ledger['rejecting_controls']['struct_boundary_radix_union']
    need(len(rejects)==17 and all(v and all(Q(x['rational'])<=0 for x in v.values()) for v in rejects.values()),'all 17 controls')
    need(Q(independent['rows']['struct_boundary_radix_union']['kappa'])==K,'independent outer endpoint')
    result=dict(status='PASS_COUPLED_CAP740_BINOMIAL40',kappa=str(K),previous=str(prior),gain=str(K-prior),endpoint=str(C),
                binomial_below=list(map(str,(lo,hi))),binomial_successor=list(map(str,(sl,sh))),controls=controls,
                retained_engines=engines,outer=ledger,independent_outer=independent,bootstrap=old.bootstrap(C),
                scope='Conditional fixed-supplier arithmetic refinement; inherited physical/compiler/all-size/precision/analytic/BIT premises remain.')
    baseline=old.load(old.BASE/'verify_release.py','baseline_release').check()
    result['baseline_release']=baseline
    claim=old.read(P/'CLAIM.json')
    need(claim==dict(kappa=str(K),complex_lower=str(C),previous=str(prior),gain=str(K-prior),endpoint_digits=40),'public claim mismatch')
    need(result==old.read(P/'RESULT.json'),'fresh result differs from frozen certificate')
    if args.output:old.save(args.output,result)
print(result['status'],'gain',result['gain'])
