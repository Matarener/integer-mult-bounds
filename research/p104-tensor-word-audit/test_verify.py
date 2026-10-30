#!/usr/bin/env python3
"""Literal-word semantic controls and source-bound export checks.

Apache-2.0. Separate AI test implementation, not human/formal/native review.
Only authenticated predecessor word builders are objects under review. These
controls exercise the companion arithmetic audit without using its predecessor
execution or invoice routines.
"""
from __future__ import annotations

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
ROOT = HERE.parents[1]
PACKAGE = Path('research/p104-tensor-word-audit')
FIXTURE = Path('research/p104-native-channel/inputs/P104-FIXTURE.json')


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_ino, stat.S_IMODE(p.stat().st_mode),
                                      hashlib.sha256(p.read_bytes()).hexdigest())
            for p in root.rglob('*') if p.is_file()}


def private_fixture(root):
    package = root / PACKAGE
    package.parent.mkdir(parents=True)
    shutil.copytree(HERE, package, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns('__pycache__', '.git'))
    fixture = root / FIXTURE
    fixture.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / FIXTURE, fixture)
    # copytree copies directory metadata even with copyfile. Only these newly
    # created private fixtures become writable; the source export stays intact.
    for directory in [root] + [p for p in root.rglob('*') if p.is_dir()]:
        directory.chmod(0o755)
    return package


def execute(arguments, optimized=False, cwd=None):
    command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else []) + arguments
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=40)


API_DRIVER = r'''
import runpy,sys
v=runpy.run_path(sys.argv[1])
words,b=v['get_words']()
n=104
count=0

def reject(name,key,change,expected):
    global count
    altered=dict(words)
    altered[key]=list(words[key])
    change(altered[key])
    try:
        v['certify'](words=altered)
    except ValueError as error:
        if expected not in str(error):
            raise RuntimeError(name+' failed for an unexpected reason: '+str(error))
    else:
        raise RuntimeError('accepted literal mutation: '+name)
    count+=1

first_add=next(i for i,op in enumerate(words['enc']) if op[0]=='add')
def replace(word,index,operation): word[index]=operation

def flip(word,index):
    op=word[index]
    word[index]=(op[0],op[1],op[2],-op[3])

def orient(word):
    op=word[first_add]
    word[first_add]=(op[0],op[2],op[1],op[3])

def interleave(word):
    word[0],word[first_add]=word[first_add],word[0]

reject('helper_index','enc',lambda w:replace(w,0,('half',2*n*n)), 'global data index')
reject('boolean_index','enc',lambda w:replace(w,0,('half',True)), 'global data index')
reject('wrong_bank','enc',lambda w:replace(w,0,('half',w[0][1]+n*n)), 'bank ownership')
reject('wrong_sign','enc',lambda w:flip(w,first_add), 'exact fiber linear map')
reject('boolean_sign','enc',lambda w:replace(w,first_add,('add',w[first_add][1],w[first_add][2],True)), 'unit sign')
reject('orientation','enc',orient, 'exact fiber linear map')
reject('half_add_interleaving','enc',interleave, 'exact fiber linear map')
# The first transposed sweep has384 additions and twice8 donor scalings.
# Damage the corresponding add only in its second fixed-coordinate instance.
reject('later_cached_fiber','enc',lambda w:flip(w,400+first_add), 'nonuniform fiber program')
reject('omitted_coded_source_restoration','coded',lambda w:w.pop(), 'truncated fiber')
reject('omitted_reference_source_restoration','reference',lambda w:w.pop(), 'truncated fiber')
reject('trailing_unaudited_operation','enc',lambda w:w.append(('double',0)), 'unconsumed encoder/decoder events')
# A literal address in another fixed-coordinate fiber cannot be relocalized silently.
reject('wrong_axis_owner','enc',lambda w:replace(w,0,('half',w[0][1]+n)), 'fiber ownership/axis')
print('PASS_LITERAL_MUTATION_CONTROLS cases='+str(count))
'''


def semantic_controls():
    for optimized in (False, True):
        run = execute(['-c', API_DRIVER, str(HERE / 'verify.py')], optimized, HERE)
        need(run.returncode == 0 and 'PASS_LITERAL_MUTATION_CONTROLS cases=12' in run.stdout,
             'literal semantic controls failed optimized=' + str(optimized) + '\n' + run.stderr)
    return 12


def cli_controls(base):
    names = ('changed_builder', 'missing_builder', 'changed_frozen_proof',
             'changed_fixture', 'missing_fixture', 'undercharged_invoice', 'typed_boolean_invoice')
    independent_runs = 0
    for name in names:
        root = base / name
        package = private_fixture(root)
        if name == 'changed_builder':
            path = package / 'source/verify.py'
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'missing_builder':
            (package / 'source/verify.py').unlink()
        elif name == 'changed_frozen_proof':
            path = package / 'source/PROOF.md'
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'changed_fixture':
            path = root / FIXTURE
            path.write_bytes(path.read_bytes() + b'\n')
        elif name == 'missing_fixture':
            (root / FIXTURE).unlink()
        else:
            path = package / 'CERTIFICATE.json'
            cert = json.loads(path.read_text())
            if name == 'undercharged_invoice':
                cert['invoices']['boundary']['add'] -= 1
            else:
                cert['schema_version'] = True
            path.write_text(json.dumps(cert))
        for optimized in (False, True):
            run = execute([str(package / 'verify.py')], optimized, root)
            need(run.returncode != 0 and
                 ('ValueError' in run.stderr or 'FileNotFoundError' in run.stderr),
                 'damaged actual CLI accepted or crashed unexpectedly: ' + name + '\n' + run.stderr)
            if name in ('changed_fixture', 'missing_fixture'):
                other = execute([str(package / 'independent.py')], optimized, root)
                need(other.returncode != 0 and
                     ('ValueError' in other.stderr or 'FileNotFoundError' in other.stderr),
                     'independent CLI accepted damaged canonical fixture: ' + name)
                independent_runs += 1
    return len(names), independent_runs


def readonly_positive(base):
    root = base / 'readonly'
    package = private_fixture(root)
    files = [p for p in root.rglob('*') if p.is_file()]
    directories = [root] + [p for p in root.rglob('*') if p.is_dir()]
    for path in files:
        original = (HERE / path.relative_to(package)) if path.is_relative_to(package) else ROOT / path.relative_to(root)
        need(path.stat().st_ino != original.stat().st_ino, 'shared read-only fixture inode')
        path.chmod(0o444)
    for path in directories:
        path.chmod(0o555)
    before = snapshot(root)
    try:
        for optimized in (False, True):
            run = execute([str(package / 'verify.py')], optimized, root)
            need(run.returncode == 0 and run.stdout.startswith('PASS_P104_TENSOR_WORD_AUDIT '),
                 'full readonly actual104 CLI failed: ' + run.stderr)
            result = json.loads(run.stdout.split(' ', 1)[1])
            need(result['ports'] == 104 and result['data_degrees'] == 21632
                 and result['audited_literal_operations'] == 763392
                 and result['fiber_instances'] == 1056 and result['distinct_exact_local_maps'] == 8,
                 'positive literal coverage changed')
        need(snapshot(root) == before, 'read-only export changed')
    finally:
        for path in sorted(directories, key=lambda p:len(p.parts)):
            path.chmod(0o755)
    return len(files)


def main():
    started = time.monotonic()
    original = snapshot(HERE)
    original_fixture = (ROOT / FIXTURE).read_bytes()
    api = semantic_controls()
    with tempfile.TemporaryDirectory(prefix='p104-tensor-word-controls-') as temporary:
        base = Path(temporary)
        cli, independent_runs = cli_controls(base)
        readonly_files = readonly_positive(base)
    need(snapshot(HERE) == original and (ROOT / FIXTURE).read_bytes() == original_fixture,
         'source package or canonical fixture changed')
    print('PASS_P104_TENSOR_WORD_CONTROLS semantic_cases=' + str(api)
          + ' cli_cases=' + str(cli) + ' negative_runs=' + str(2*(api+cli))
          + ' independent_source_negative_runs=' + str(independent_runs)
          + ' actual104_normal_optimized=PASS readonly_git_free_files=' + str(readonly_files)
          + ' source_unchanged=PASS elapsed_seconds=' + format(time.monotonic()-started,'.3f'))


if __name__ == '__main__':
    main()
