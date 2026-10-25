"""Registered cold replay, identical scientific guards in normal and-O modes."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from datetime import datetime,timezone
import argparse,hashlib,json,gzip,subprocess,sys,time,importlib.util
H=Path(__file__).resolve().parent
def need(value,why):
    if not value:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    output=a.output.resolve();output.mkdir(parents=True,exist_ok=True);started=time.time()
    source=json.loads((H/'REHOST-MANIFEST.json').read_bytes())
    canonical=json.loads((H/'MANIFEST.json').read_bytes())['files']
    actual={str(p.relative_to(H)).replace('\\','/')for p in H.rglob('*')if p.is_file()and'__pycache__'not in p.parts and'control-work'not in p.parts and p.name not in('MANIFEST.json','REHOST-MANIFEST.json')}
    # OnlythetwoTOPLEVEL manifests areexcluded. Historical manifests are
    # included belowanddescriptiveonly; nooriginalsourceclaimisrelabeled.
    actual={str(p.relative_to(H)).replace('\\','/')for p in H.rglob('*')if p.is_file()and'__pycache__'not in p.parts and'control-work'not in p.parts and p not in(H/'MANIFEST.json',H/'REHOST-MANIFEST.json')}
    need(actual==set(canonical),'exact activecanonical fileinventory')
    for name,pin in canonical.items():need(sha(H/name)==pin,'activecanonical sourcepin '+name)
    for f in source['files']:
        p=(H/f['path']).resolve();need(p.is_relative_to(H.resolve()),'manifest path scope')
        need(sha(p)==f['sha256'],'registered source pin '+f['path'])
    mode='optimized'if sys.flags.optimize else'normal';runs={};objects={}
    for name,args in [('new_probe',['new_probe.py']),('native_controls',['native_controls.py']),('complete',['caller.py','--scope','complete'])]:
        cmd=[sys.executable,'-X','utf8','-B']+(['-O']if sys.flags.optimize else[])+[str(H/args[0])]+args[1:]
        st=time.time();r=subprocess.run(cmd,capture_output=True,timeout=240)
        (output/(name+'.stdout.json')).write_bytes(r.stdout);(output/(name+'.stderr.txt')).write_bytes(r.stderr)
        runs[name]=dict(command=cmd,exit=r.returncode,wall_seconds=time.time()-st,
            stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
        need(r.returncode==0,'cold '+name+' failed: '+r.stderr.decode('utf-8')[-3000:])
        objects[name]=json.loads(r.stdout)
    need(objects['new_probe']['optimized']==bool(sys.flags.optimize),'actual optimized child replay')
    need(len(objects['new_probe']['negative_controls'])==6,'six live scientific negative controls')
    need(objects['native_controls']['status']=='PASS_ACTIVE658_NATIVE_AND_MUTANTS','freshnative andmutants');complete=objects['complete'];need(complete['status']=='PASS_NEW_SOURCE_BOUND_LOGICAL_RECURSIVE_CALLER','completed actual source caller')
    native=module('new_price_native',H/'native.py');w=json.loads(gzip.decompress((H/'inputs/WORD.json.gz').read_bytes()))
    events=native.candidate(w['records']);need(native.digest(events)==native.WORD_HASHES['candidate'],'literal candidate word identity')
    local=Counter()
    for z in events:
        if z[0]==0:local[z[4]]+=1
        elif z[0]==2:local[7]+=1
    P=Counter({r:288*n for r,n in local.items()})
    factors=json.loads(gzip.decompress((H/'new-owners/REMAINDERS.json.gz').read_bytes()))
    for child,cp,axes in factors:
        if axes:P[len(axes)]+=32
    need(dict(P)=={int(r):n for r,n in complete['catalogue']['rank_histogram'].items()},'actual caller price census')
    need(sum(P.values())==900416 and sum(r*n for r,n in P.items())==1808352,'complete owned query mass')
    price=module('new_registered_price',H/'price.py');root=price.bracket(P)
    public=Q(1743059363170060183941,10**24)
    need(Q(root['lower'])>public*Q(1001,1000),'fresh baseline preparation guard')
    simple=Q(174481,100000000);ordinary=price.moment(P,simple)
    need(ordinary[1]<1-Q(1,10000000),'retained convenient induction constant at b.00174481')
    for f in source['files']:need(sha(H/f['path'])==f['sha256'],'postreplay source drift '+f['path'])
    report=dict(status='PASS_REGISTERED_ACTIVE658_COMPACT_GL_DEADROLE_REHOST',at_utc=datetime.now(timezone.utc).isoformat(),mode=mode,
        source_manifest_sha256=sha(H/'REHOST-MANIFEST.json'),runs=runs,
        native=objects['native_controls'],owner=objects['new_probe']['actual_owner_checks'],negative_controls=objects['new_probe']['negative_controls'],
        catalogue=complete['catalogue'],literal=complete['literal_binding'],split_bases=complete['split_bases'],
        full_latest_threshold_traces=complete['threshold_probes'],
        complete_profile=dict(sorted(P.items())),root=root,
        exact_public_comparator=str(public),exact_preparation_floor=str(public*Q(1001,1000)),
        convenient_proved_b=str(simple),moment_at_convenient_b=[str(v)for v in ordinary],
        oldWORD_SOURCE_and_DIRTY_unchanged=False, new658_allRAW_signed_literal_verified=True,whole_kappa_improvement=False,
        allsize_scope='Latest source-bound logicalp1 caller with originalrootcoupling and compatiblefreshrowstock; no new physicaltape/outer/completion assumptions.',
        wall_seconds=time.time()-started)
    (output/'RESULT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],mode=mode,c=root['decimal_lower'],controls=6,wall_seconds=report['wall_seconds'])))
if __name__=='__main__':main()
