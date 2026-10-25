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
    for f in source['files']:
        p=(H/f['path']).resolve();need(p.is_relative_to(H.resolve()),'manifest path scope')
        need(sha(p)==f['sha256'],'registered source pin '+f['path'])
    mode='optimized'if sys.flags.optimize else'normal';runs={};objects={}
    for name,args in [('new_probe',['new_probe.py']),('complete',['caller.py','--scope','complete'])]:
        cmd=[sys.executable,'-X','utf8','-B']+(['-O']if sys.flags.optimize else[])+[str(H/args[0])]+args[1:]
        st=time.time();r=subprocess.run(cmd,capture_output=True,timeout=240)
        (output/(name+'.stdout.json')).write_bytes(r.stdout);(output/(name+'.stderr.txt')).write_bytes(r.stderr)
        runs[name]=dict(command=cmd,exit=r.returncode,wall_seconds=time.time()-st,
            stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
        need(r.returncode==0,'cold '+name+' failed: '+r.stderr.decode('utf-8')[-3000:])
        objects[name]=json.loads(r.stdout)
    need(objects['new_probe']['optimized']==bool(sys.flags.optimize),'actual optimized child replay')
    need(len(objects['new_probe']['negative_controls'])==6,'six live scientific negative controls')
    complete=objects['complete'];need(complete['status']=='PASS_NEW_SOURCE_BOUND_LOGICAL_RECURSIVE_CALLER','completed actual source caller')
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
    need(sum(P.values())==901312 and sum(r*n for r,n in P.items())==1808352,'complete owned query mass')
    price=module('new_registered_price',H/'price.py');root=price.bracket(P)
    public=Q(434407954621501888371,250000000000000000000000)
    need(Q(root['lower'])>public*Q(1001,1000),'fresh baseline preparation guard')
    simple=Q(871,500000);ordinary=price.moment(P,simple)
    need(ordinary[1]<1-Q(1,2400000),'retained convenient induction constant at b.001742')
    for f in source['files']:need(sha(H/f['path'])==f['sha256'],'postreplay source drift '+f['path'])
    report=dict(status='PASS_REGISTERED_INTEGER_MIXED_WIDTH_REHOST',at_utc=datetime.now(timezone.utc).isoformat(),mode=mode,
        source_manifest_sha256=sha(H/'REHOST-MANIFEST.json'),runs=runs,
        owner=objects['new_probe']['actual_owner_checks'],negative_controls=objects['new_probe']['negative_controls'],
        catalogue=complete['catalogue'],literal=complete['literal_binding'],split_bases=complete['split_bases'],
        full_latest_threshold_traces=complete['threshold_probes'],
        complete_profile=dict(sorted(P.items())),root=root,
        exact_public_comparator=str(public),exact_preparation_floor=str(public*Q(1001,1000)),
        convenient_proved_b=str(simple),moment_at_convenient_b=[str(v)for v in ordinary],
        oldWORD_SOURCE_and_DIRTY_unchanged=True,whole_kappa_improvement=False,
        allsize_scope='Latest source-bound logicalp1 caller with originalrootcoupling and compatiblefreshrowstock; no new physicaltape/outer/completion assumptions.',
        wall_seconds=time.time()-started)
    (output/'RESULT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],mode=mode,c=root['decimal_lower'],controls=6,wall_seconds=report['wall_seconds'])))
if __name__=='__main__':main()
