#!/usr/bin/env python3
"""Phase-tag semantic, typed-boundary and damaged-source controls.

Apache-2.0. Separate AI test implementation; no human/kernel review claimed.
No predecessor executable is imported. Private fixtures copy file bytes and
explicitly restore writable directory modes, including from read-only exports.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_ino, stat.S_IMODE(p.stat().st_mode),
                                      hashlib.sha256(p.read_bytes()).hexdigest())
            for p in root.rglob('*') if p.is_file()}


def private_fixture(destination):
    shutil.copytree(HERE, destination, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns('__pycache__', '.git'))
    for directory in [destination] + [p for p in destination.rglob('*') if p.is_dir()]:
        directory.chmod(0o755)


def execute(arguments, optimized=False, cwd=None):
    command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + arguments
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=25)


API_DRIVER = r'''
import copy,itertools,runpy,sys
v=runpy.run_path(sys.argv[1])
G=(1,2,8,32,44,128,59,66,489)
Gi=v['inverse'](G)
I=tuple(1<<i for i in range(9))
count=0

def need(ok,message):
    if not ok: raise RuntimeError(message)

def reject(name,call):
    global count
    try: call()
    except ValueError: pass
    else: raise RuntimeError('accepted damaged boundary: '+name)
    count+=1

# Direct bit-column application and Hamming phases specify the convention
# independently of elimination, quadratic forms and the word recurrence.
def image(columns,x):
    answer=0
    for j,column in enumerate(columns):
        if x&(1<<j): answer^=column
    return answer

need(v['tag'](G)==144 and v['tag'](Gi)==68, 'credited tag witness')
need(v['compose'](Gi,G)==I, 'binary inverse')
missing_tag=wrong_section_sign=wrong_adjoint=0
for x in range(512):
    section=(image(G,x).bit_count()-x.bit_count())%4
    need(v['apply'](G,x)==image(G,x) and v['section_phase'](G,x)==section,
         'binary application or D P D-adjoint orientation')
    canonical=v['canonical_phase'](G,x)
    need(canonical==(section+2*((144&x).bit_count()%2))%4, 'section correction')
    missing_tag+=canonical!=section
    wrong_section_sign+=section!=(-section)%4
    need(v['gate_phase'](G,x,-1)==(-v['canonical_phase'](G,image(Gi,x)))%4,
         'adjoint input must be inverse-permuted')
    wrong_adjoint+=v['gate_phase'](G,x,-1)!=v['canonical_phase'](Gi,x)
need(missing_tag==256 and wrong_adjoint==256 and wrong_section_sign>0,
     'phase/sign controls did not distinguish wrong conventions')

positive=v['word_certificate']([G,Gi])
adjoint=v['word_certificate']([G,G],[1,-1])
need(positive=={'product':list(I),'tag':256,'section_tag':256}, 'canonical inverse-pair defect')
need(adjoint=={'product':list(I),'tag':0,'section_tag':0}, 'actual adjoint must cancel')
# A genuine covector pullback differs from applying G to the tag vector.
expected=sum((((G[j]&v['tag'](Gi)).bit_count())%2)<<j for j in range(9))
need(v['pullback'](G,v['tag'](Gi))==expected, 'transpose pullback')
wrong_transpose=copy.deepcopy(positive)
wrong_transpose['tag']=v['tag'](G)^image(G,v['tag'](Gi))
need(wrong_transpose['tag']!=positive['tag'], 'transpose control is ineffective')
missing=copy.deepcopy(positive);missing['tag']=0
wrong_type=copy.deepcopy(positive);wrong_type['product'][0]=True
actual=v['actual_maps']()
first,second=next((a,b) for a,b in itertools.product(actual,repeat=2)
                  if v['compose'](b,a)!=v['compose'](a,b))
reverse=v['word_certificate']([second,first])
reject('singular_map',lambda:v['inverse']((1,1)))
reject('width_mismatch',lambda:v['compose']((1,2),(1,2,4)))
reject('boolean_column',lambda:v['tag']((True,2)))
reject('boolean_input',lambda:v['apply'](G,True))
reject('tag_out_of_domain',lambda:v['pullback'](G,512))
reject('zero_gate_sign',lambda:v['gate_phase'](G,0,0))
reject('boolean_word_sign',lambda:v['word_certificate']([G],[True]))
reject('canonical_inverse_is_not_adjoint',lambda:v['check_word']([G,G],positive,[1,-1]))
reject('forward_map_is_not_pullback',lambda:v['check_word']([G,Gi],wrong_transpose))
reject('reversed_word_order',lambda:v['check_word']([first,second],reverse))
reject('omitted_phase_tag',lambda:v['check_word']([G,Gi],missing))
reject('boolean_word_certificate',lambda:v['check_word']([G,Gi],wrong_type))

# Exact Gaussian numerators for Z C Z = i C-adjoint when dot(t,u)=1.
alpha,beta=(1,1),(1,-1)
times_i=lambda pair:(-pair[1],pair[0])
neg=lambda pair:tuple(-x for x in pair)
for x in range(2):
    zcz={x:alpha,x^1:neg(beta)}
    i_adjoint={x:times_i(beta),x^1:times_i(alpha)}
    omitted_i={x:beta,x^1:alpha}
    need(zcz==i_adjoint and zcz!=omitted_i, 'mandatory central-C global i')
print('PASS_NATIVE_LIFT_TAG_API_CONTROLS cases='+str(count)
      +' missing_tag_states='+str(missing_tag)+' wrong_adjoint_states='+str(wrong_adjoint)
      +' wrong_section_sign_states='+str(wrong_section_sign)+' global_i_states=2')
'''


def api_controls():
    for optimized in (False, True):
        run = execute(['-c', API_DRIVER, str(HERE / 'verify.py')], optimized, HERE)
        need(run.returncode == 0 and 'PASS_NATIVE_LIFT_TAG_API_CONTROLS cases=12' in run.stdout,
             'API semantic controls failed optimized=' + str(optimized) + '\n' + run.stderr)
    return 12


def cli_controls(base):
    names = ('changed_phase_source', 'missing_recipes', 'changed_source_readme',
             'omitted_word_tag', 'undercharged_global_phase', 'omitted_map',
             'typed_boolean_receipt', 'duplicate_receipt_key')
    independent_runs = 0
    for name in names:
        folder = base / name
        private_fixture(folder)
        certificate = folder / 'CERTIFICATE.json'
        if name == 'changed_phase_source':
            path = folder / 'source/exact_phase.py'
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'missing_recipes':
            (folder / 'source/RECIPES.json').unlink()
        elif name == 'changed_source_readme':
            path = folder / 'source/README.md'
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'duplicate_receipt_key':
            certificate.write_text(certificate.read_text().replace('{','{"width":9,',1))
        else:
            value = json.loads(certificate.read_text())
            if name == 'omitted_word_tag':
                value['signed_word']['certificate']['tag'] = 0
            elif name == 'undercharged_global_phase':
                value['frame_rebinding']['required_global_i'] = False
            elif name == 'omitted_map':
                value['maps'].pop()
            else:
                value['schema_version'] = True
            certificate.write_text(json.dumps(value))
        for optimized in (False, True):
            run = execute([str(folder / 'verify.py')], optimized, folder)
            need(run.returncode != 0 and
                 ('ValueError' in run.stderr or 'FileNotFoundError' in run.stderr),
                 'actual damaged CLI accepted or crashed unexpectedly: ' + name + '\n' + run.stderr)
            if name in ('changed_phase_source','missing_recipes','changed_source_readme'):
                other = execute([str(folder / 'independent.py')], optimized, folder)
                need(other.returncode != 0 and
                     ('ValueError' in other.stderr or 'FileNotFoundError' in other.stderr),
                     'independent CLI accepted damaged source: ' + name)
                independent_runs += 1
    return len(names), independent_runs


def readonly_positive(base):
    folder = base / 'readonly'
    private_fixture(folder)
    files = [p for p in folder.rglob('*') if p.is_file()]
    directories = [folder] + [p for p in folder.rglob('*') if p.is_dir()]
    for path in files:
        need(path.stat().st_ino != (HERE / path.relative_to(folder)).stat().st_ino,
             'shared read-only export inode')
        path.chmod(0o444)
    for path in directories:
        path.chmod(0o555)
    before = snapshot(folder)
    try:
        for optimized in (False, True):
            run = execute([str(folder / 'verify.py')], optimized, folder)
            need(run.returncode == 0 and run.stdout.startswith('PASS_NATIVE_LIFT_PHASE_TAGS '),
                 'read-only Git-free actual-map replay failed: ' + run.stderr)
            receipt = json.loads(run.stdout.split(' ',1)[1])
            need(receipt['actual_maps']==4 and receipt['actual_pair_checks']==8192
                 and receipt['signed_word_states']==512 and not receipt['native_tariff_proved'],
                 'actual-map coverage or scope changed')
        need(snapshot(folder)==before, 'read-only export changed')
    finally:
        for path in sorted(directories,key=lambda p:len(p.parts)):
            path.chmod(0o755)
    return len(files)


def main():
    started = time.monotonic()
    paths = [HERE / name for name in ('verify.py','CERTIFICATE.json','test_verify.py')]
    paths += [p for p in (HERE / 'source').rglob('*') if p.is_file()]
    def science_snapshot():
        return {str(p.relative_to(HERE)):(p.stat().st_ino,stat.S_IMODE(p.stat().st_mode),
                                         hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths}
    before = science_snapshot()
    api = api_controls()
    with tempfile.TemporaryDirectory(prefix='native-lift-phase-tag-controls-') as temporary:
        base = Path(temporary)
        cli, independent_runs = cli_controls(base)
        readonly_files = readonly_positive(base)
    need(science_snapshot()==before, 'source inputs or scientific executables changed')
    print('PASS_NATIVE_LIFT_PHASE_TAG_CONTROLS api_cases='+str(api)+' cli_cases='+str(cli)
          +' negative_runs='+str(2*(api+cli))+' independent_source_negative_runs='+str(independent_runs)
          +' normal_optimized=PASS readonly_git_free_files='+str(readonly_files)
          +' source_unchanged=PASS elapsed_seconds='+format(time.monotonic()-started,'.3f'))


if __name__=='__main__':
    main()
