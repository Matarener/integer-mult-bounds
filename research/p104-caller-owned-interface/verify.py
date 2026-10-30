#!/usr/bin/env python3
"""Exact independent forward-caller replay with explicit owned inventories.

Prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
Canonical PR5550 and PR5599 source notices remain intact.
"""
from pathlib import Path
import argparse
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import types

HERE=Path(__file__).resolve().parent
CAPSULE='research/p104-caller-independent-audit/capsule'
CHECK=CAPSULE+'/outputs/p104-caller-route-audit-v2-20261025/check.py'
SELECTED='docs/research/pr-intake-evidence/pr5599/caller-check.py'
EXPECTED='research/p104-caller-independent-audit/expected/caller.json.gz'

def need(ok,message):
    if not ok: raise ValueError(message)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module

def authenticate(root):
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            path=root/row['path'];raw=path.read_bytes()
            need(not path.is_symlink() and sha(raw)==row['sha256'],'Canonical source byte '+row['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
                 'Canonical source blob '+row['path'])
    inventory=json.loads((HERE/'PACKAGE-INVENTORY.json').read_text())['files']
    actual={p.relative_to(HERE).as_posix() for folder in ('source','expected','code','evidence')
            for p in (HERE/folder).rglob('*') if p.is_file()}
    need(actual==set(inventory),'Complete frozen package inventory')
    for name,digest in inventory.items():
        path=HERE/name
        need(not path.is_symlink() and sha(path.read_bytes())==digest,'Frozen package byte '+name)
    binding=json.loads((HERE/'source/BINDING.json').read_text())
    need(sha((root/CHECK).read_bytes())==binding['original_checker_sha256'],'Original checker pin')
    need(sha((root/SELECTED).read_bytes())==binding['selected_checker_sha256'],'Selected adapter pin')
    need(sha(gzip.decompress((root/EXPECTED).read_bytes()))==binding['original_output_sha256'],'Original output pin')
    for key in ('interface','adapter'):
        need(sha((HERE/'code'/(key+'.py')).read_bytes())==binding[key+'_sha256'],'Checked adapter source '+key)
    for key,filename in (('word','WORD.json.gz'),('result','RESULT.json')):
        need(sha((HERE/'source'/filename).read_bytes())==binding[key+'_bytes_sha256'],'Candidate source '+key)
    word=json.loads(gzip.decompress((HERE/'source/WORD.json.gz').read_bytes()))
    need(sha(json.dumps(word,sort_keys=True,separators=(',',':')).encode())==binding['word_canonical_sha256'],'Canonical candidate word')
    return binding

def child(root,mode):
    binding=authenticate(root)
    # The frozen output uses UTF-8/LF; Windows stdout otherwise writes CRLF.
    # Configure the stream before executing the unchanged scientific checker.
    sys.stdout.reconfigure(encoding='utf-8',newline='\n')
    # Operational trace portability only; no scientific object is changed.
    try: import resource
    except ImportError:
        sys.modules['resource']=types.SimpleNamespace(RUSAGE_SELF=0,getrusage=lambda _:types.SimpleNamespace(ru_maxrss=None))
    for key in ('P104_WORD','P104_RESULT','P104_TRACE_FILE','P104_CAPSULE_CHECKER'):
        os.environ.pop(key,None)
    namespace=dict(__name__='__main__',__file__=str(root/CHECK))
    if mode=='original':
        source=(root/CHECK).read_text()
    else:
        adapter=load(HERE/'code/adapter.py','p104_checked_caller_adapter')
        load(HERE/'code/interface.py','p104_caller_interface')
        source,_=adapter.adapted((root/SELECTED).read_text())
        need(sha(source.encode())==binding['generated_checker_sha256'],'Exact frozen selected-checker adaptation')
        os.environ.update(P104_WORD=str(HERE/'source/WORD.json.gz'),P104_RESULT=str(HERE/'source/RESULT.json'),P104_CAPSULE_CHECKER=str(root/CHECK))
        namespace.update(source_physical=adapter.source_physical,CANDIDATE_INPUT={k:binding[k] for k in
            ('declared_source_head','word_bytes_sha256','word_canonical_sha256','result_bytes_sha256','selected_checker_sha256','interface_sha256','adapter_sha256')})
    exec(compile(source,str(root/CHECK) if mode=='original' else 'explicit-owned-caller.py','exec'),namespace)

def interface_fixture(root):
    interface=load(HERE/'code/interface.py','p104_fixture_interface')
    word=json.loads(gzip.decompress((HERE/'source/WORD.json.gz').read_bytes()))
    result=json.loads((HERE/'source/RESULT.json').read_text())
    original=interface.audit(word,result)
    # Permute one helper and one owned label. This produces a genuine public
    # hole without changing a linear map, any chart, coefficient or interval.
    helper,owned=573,word['public']
    need(helper in original['helpers'] and owned in original['owned'],'Fixed source relabeling fixture')
    rename=lambda r:owned if r==helper else helper if r==owned else r
    changed=deepcopy(word);changed['public']=word['public']+1
    zero=next(i for i,basis in enumerate(word['frames']) if not basis)
    for side in ('initial','final'):
        changed[side]=[zero]*changed['public']
        for role in original['independent']:changed[side][rename(role)]=word[side][role]
    changed.update(fields=original['fields'],independent_public=[rename(r) for r in original['independent']],
        owned_roles=[rename(r) for r in original['owned']],retired_public=[helper])
    for event in changed['program']:
        event[1]=rename(event[1])
        if event[0] in ('ADD','COPY'):event[2]=rename(event[2])
    hole=interface.audit(changed,result)
    for key in ('helper_count','productive_fields','paid','targets','scalar','routes','lifetime_count','peak'):
        need(hole[key]==original[key],'Pure role permutation preserves '+key)
    controller=json.loads((root/CAPSULE/'outputs/p104-contact-reassessment-20261025/sources/predecessor/CONTROLLER.json').read_text())
    full=[event for event in controller['physical_events'] if event[0]=='LOCAL']
    fields=interface.allocation(hole,full,changed['live'])
    need(all(site['local_to_global'][helper] is None and site['local_to_global'][owned] is not None for site in fields),
         'Retired hole has no productive ID and relocated helper retains one')
    schedule=interface.caller_schedule(hole,controller,fields)
    return dict(status='PASS_EXACT_ROLE_PERMUTATION_PUBLIC_HOLE',retired_public=[helper],
        relocated_helper=owned,public_slots=changed['public'],independent_inputs=len(hole['independent']),
        owned_lifetimes=hole['lifetime_count'],peak=hole['peak'],caller_owned_intervals=len(schedule['intervals']))

def replay(root,mode,temporary,guard):
    out=temporary/(mode+'.json');err=temporary/(mode+'.stderr')
    command=[sys.executable,'-X','pycache_prefix='+str(temporary/'bytecode')]
    if sys.flags.optimize: command.append('-O')
    command+=['-B',str(HERE/'verify.py'),'--canonical-root',str(root),'--child',mode]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE',None)
    start=time.monotonic();peak=0;cause=None
    with out.open('wb') as output,err.open('wb') as errors:
        proc=subprocess.Popen(command,stdout=output,stderr=errors,env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            while proc.poll() is None:
                try: usage=guard.rss(proc)
                except OSError:
                    if proc.poll() is None: raise
                    break
                peak=max(peak,usage)
                if usage>512*1024**2: cause='sampled memory exceeds512 MiB'
                if time.monotonic()-start>120: cause='elapsed time exceeds120 seconds'
                if cause: proc.kill();break
                time.sleep(.1)
            code=proc.wait()
        except BaseException:
            proc.kill();proc.wait();raise
    need(code==0 and cause is None and not err.read_bytes(),
         mode+' child failed: '+str(cause)+' '+err.read_text(errors='replace')[:4000])
    expected=gzip.decompress((root/EXPECTED if mode=='original' else HERE/'expected/candidate.json.gz').read_bytes())
    need(out.read_bytes()==expected,mode+' complete frozen scientific output equality')
    return json.loads(expected),dict(mode=mode,seconds=time.monotonic()-start,sampled_peak_child_rss_bytes=peak,
                                    complete_output_sha256=sha(expected),cap_seconds=120,cap_mib=512)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--canonical-root',type=Path,default=HERE.parents[1],help='Draft replay only; registered replay uses repository root')
    parser.add_argument('--child',choices=('original','candidate'))
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--interface-only',action='store_true')
    args=parser.parse_args();root=args.canonical_root.resolve();authenticate(root)
    if args.child: child(root,args.child);return
    if args.check_only:
        print('PASS_P104_EXPLICIT_OWNED_CALLER_SOURCE_BINDINGS_ONLY');return
    fixture=interface_fixture(root)
    if args.interface_only:
        print(json.dumps(fixture,sort_keys=True));return
    guard=load(HERE/'code/guard.py','p104_scoped_resource_guard')
    with tempfile.TemporaryDirectory(prefix='p104-owned-caller-') as name:
        original,old_run=replay(root,'original',Path(name),guard)
        candidate,new_run=replay(root,'candidate',Path(name),guard)
    need(original['kappa_claim'] is None and candidate['kappa_claim'] is None,'No new bound from caller audit')
    need(len(original['controls'])==10 and len(candidate['controls'])==16,'All retained and interface-specific controls')
    need(candidate['native_checks']['owned_peak']==2 and len(candidate['owned_scratch_fields'])==2,'Explicit simultaneous scratch bound')
    authenticate(root)
    print('PASS_P104_EXPLICIT_OWNED_CALLER_AUDIT')
    print(json.dumps(dict(source_head=candidate['candidate_input']['declared_source_head'],contacts=len(candidate['route_recipes'])*4,
        fresh_helpers=candidate['native_checks']['fresh_helpers'],owned_peak=2,paid_jobs=sum(candidate['paid'].values()),
        productive_fields=sum(candidate['targets'].values()),ordinary_pass_upper=candidate['ordinary']['abstract_address_phase_scalar_pass_upper'],
        controls=len(candidate['controls']),public_hole_fixture=fixture,runs=[old_run,new_run],full_parent_admitted=False,new_kappa=None),sort_keys=True))

if __name__=='__main__': main()
