#!/usr/bin/env python3
"""Explicit, bounded Lean replay. Requires the pinned Lean/mathlib environment.

No dependency installation is performed. Every owned module is compiled anew
outside the source tree, then its exported declarations are kernel-replayed.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODULES = ['CompilerAudit.SelectedData', 'CompilerAudit.Visit', 'CompilerAudit.Retention',
           'CompilerAudit.Composition', 'CompilerAudit.Selected', 'CompilerAudit.Result', 'CompilerAudit']
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = ('sorry', 'admit', 'axiom', 'native_decide', 'unsafe', 'implemented_by')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def code_text(path):
    text = path.read_text(encoding='utf-8-sig')
    text = re.sub(r'/\-[\s\S]*?\-/', '', text)
    return re.sub(r'--[^\n]*', '', text)


def theorem_names():
    names = []
    for module in MODULES:
        path = HERE/(module.replace('.', '/')+'.lean')
        text = code_text(path)
        for token in FORBIDDEN:
            need(not re.search(r'\b'+token+r'\b', text), 'forbidden proof token: '+token+' in '+module)
        need('skipKernel' not in text and '#eval' not in text, 'unchecked evaluation in '+module)
        local = re.findall(r'\b(?:theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_\']*)', text)
        if local:
            namespaces = re.findall(r'^namespace\s+([A-Za-z0-9_.]+)\s*$', text, re.M)
            need(len(namespaces) == 1, 'one explicit theorem namespace per module')
            names.extend(namespaces[0]+'.'+name for name in local)
    need(len(names) == len(set(names)) and len(names) >= 20, 'complete, nontrivial theorem inventory')
    return names


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path, help='fresh absolute directory outside the source tree')
    ap.add_argument('--lean', default='lean', help='pinned Lean compiler, usually from lake env')
    ap.add_argument('--leanchecker', default='leanchecker', help='same toolchain kernel replay executable')
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    out = args.output.resolve()
    need(args.output.is_absolute() and not out.exists() and not out.is_relative_to(ROOT), 'fresh external absolute output directory')
    for p in out.parents:
        need(not any((p/n).exists() for n in ('LOCAL-MANIFEST.json', 'EXPORT-MANIFEST.json', '.git')), 'protected output ancestor')
    lean, checker = shutil.which(args.lean), shutil.which(args.leanchecker)
    need(lean is not None and checker is not None, 'install/configure the pinned toolchain before explicit replay')
    files = [HERE/(m.replace('.', '/')+'.lean') for m in MODULES]
    files += [HERE/n for n in ('lean-toolchain', 'lakefile.toml', 'lake-manifest.json',
                               'SelectedCensus.json', 'extract_census.py', 'check.py')]
    pins = {p.relative_to(HERE).as_posix(): digest(p) for p in files}
    need((HERE/'lean-toolchain').read_text().strip() == 'leanprover/lean4:v4.34.1', 'exact toolchain pin')
    manifest = json.loads((HERE/'lake-manifest.json').read_bytes())
    need(next(p['rev'] for p in manifest['packages'] if p['name']=='mathlib') ==
         'd13f23b723b8a846827a245b89c10fc7d3f11612', 'exact mathlib pin')
    names = theorem_names()
    out.mkdir(parents=True, exist_ok=False)
    build = out/'lib';build.mkdir()
    env = os.environ.copy()
    env['LEAN_PATH'] = str(build)+os.pathsep+env.get('LEAN_PATH', '')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    records = []

    def run(label, cmd, expect_false=False, expect_error=None, cwd=HERE):
        start = time.monotonic()
        try:
            p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, timeout=180)
            code, stdout, stderr, timed = p.returncode, p.stdout, p.stderr, False
        except subprocess.TimeoutExpired as e:
            code, stdout, stderr, timed = None, e.stdout or b'', e.stderr or b'', True
        (out/(label+'.stdout')).write_bytes(stdout)
        (out/(label+'.stderr')).write_bytes(stderr)
        text = (stdout+stderr).decode('utf-8', errors='replace')
        if expect_false:
            accepted = not timed and code not in (0, None) and 'Tactic `decide` proved that the proposition' in text and 'is false' in text
        elif expect_error is not None:
            accepted = not timed and code not in (0, None) and expect_error in text
        else:
            accepted = not timed and code == 0
        row = dict(label=label, command=cmd, returncode=code, timed_out=timed,
                   elapsed_seconds=time.monotonic()-start, accepted=accepted,
                   expected_false_proposition=expect_false, expected_error=expect_error)
        records.append(row)
        (out/'RUNS.json').write_bytes((json.dumps(records,indent=2)+'\n').encode())
        need(accepted, 'replay failed (see saved diagnostics): '+label)
        need(expect_false or expect_error is not None or ('sorryAx' not in text and 'warning:' not in text), 'proof warning or incomplete dependency: '+label)
        return text

    version = run('toolchain', [lean, '--version'])
    need('version 4.34.1,' in version and '5045d0056413266e57c625dcd7c365b10e377c52' in version, 'wrong compiler build')
    run('source-certificate', [sys.executable, '-I', '-B', str(HERE/'extract_census.py'), '--check'])
    bad_cert = out/'wrong-certificate.json'
    changed = json.loads((HERE/'SelectedCensus.json').read_bytes())
    changed['groups'][0]['count'] += 1
    bad_cert.write_bytes((json.dumps(changed, indent=2, sort_keys=True)+'\n').encode())
    run('reject-source-certificate', [sys.executable, '-I', '-B', str(HERE/'extract_census.py'),
        '--check', '--json', str(bad_cert)], expect_error='certificate differs from fresh source census')
    bad_data = out/'wrong-order-data.lean'
    original_data = (HERE/'CompilerAudit/SelectedData.lean').read_bytes()
    changed_data = original_data.replace(b'(0, 2920, true, true)', b'(0, 2920, true, false)', 1)
    need(changed_data != original_data, 'defined order mutation')
    bad_data.write_bytes(changed_data)
    run('reject-source-order-data', [sys.executable, '-I', '-B', str(HERE/'extract_census.py'),
        '--check', '--lean', str(bad_data)], expect_error='generated Lean bytes differ')
    flags = ['-j', '1', '-M', '2048', '-DmaxRecDepth=4096', '-DmaxHeartbeats=800000']
    for module in MODULES:
        src = HERE/(module.replace('.', '/')+'.lean')
        obj = build/(module.replace('.', '/')+'.olean');obj.parent.mkdir(parents=True,exist_ok=True)
        run('compile-'+module.replace('.','-'), [lean,*flags,'--root='+str(HERE),'-o',str(obj),str(src)])
        need(obj.is_file(), 'missing newly compiled object: '+module)
    audit = out/'KernelAudit.lean'
    expected_type = '''
example (N : Nat) (blocks : CompilerAudit.Key → Nat) :
    (CompilerAudit.Selected.word N).toFinset.card = 28278 * N ∧
    (CompilerAudit.Retention.retained (CompilerAudit.Result.program N blocks)).card = 904896 * N ∧
    (CompilerAudit.Retention.refs (CompilerAudit.Result.program N blocks)).length =
      1809792 * N + CompilerAudit.Result.blockTotal N blocks :=
  CompilerAudit.Result.selected_compiler_model N blocks
'''
    audit.write_bytes(('import CompilerAudit\n'+expected_type+
        ''.join('#check '+n+'\n#print axioms '+n+'\n' for n in names)).encode())
    text = run('axioms-and-signatures', [lean,*flags,'--root='+str(out),str(audit)])
    found = {}
    for name, empty, listed in re.findall(r"'([^']+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])", text, re.S):
        deps = [] if empty.startswith('does not') else [v.strip() for v in listed.split(',') if v.strip()]
        need(set(deps) <= ALLOWED_AXIOMS, 'non-foundational dependency: '+name+' '+repr(deps))
        found[name] = deps
    need(set(found) == set(names), 'axiom report must cover every exported theorem')
    # Leaf targets are separate serial processes; the prefix form would replay
    # several modules concurrently inside leanchecker.
    for module in MODULES[:-1]:
        run('kernel-replay-'+module.replace('.', '-'), [checker, '--verbose', module])
    controls = {
        'missing-finish': 'example : (CompilerAudit.Retention.refs (CompilerAudit.Retention.emitFrom 0 [0])).length = 1 := by decide\n',
        'wrong-replica-count': 'example : CompilerAudit.SelectedData.replicaCount = 1 := by decide\n',
        'wrong-request-count': 'example : CompilerAudit.SelectedData.requestCount = 28279 := by decide\n',
    }
    for label, body in controls.items():
        src = out/(label.replace('-', '_')+'.lean')
        src.write_bytes(('import CompilerAudit\n'+body).encode())
        run('reject-'+label, [lean,*flags,'--root='+str(out),str(src)], expect_false=True)
    need(pins == {p.relative_to(HERE).as_posix(): digest(p) for p in files}, 'proof sources changed during replay')
    result = dict(status='PASS_LEAN_MODEL_AND_SOURCE_CERTIFICATE', toolchain=version.strip(),
                  lean_binary_sha256=digest(Path(lean)), leanchecker_binary_sha256=digest(Path(checker)),
                  source_sha256=pins, theorem_axioms=found, theorem_count=len(names),
                  no_custom_axioms=True, no_incomplete_proofs=True, main_theorem_expected_type_checked=True,
                  false_propositions_rejected=list(controls), source_certificate_mutants_rejected=2, source_extraction_checked=True,
                  kernel_replay='same Lean kernel, explicit leaf modules in serial, imported library environment trusted',
                  limits='Abstract trace/allocation model and concrete interval data only; no verified Python parser/semantics, GL64 bijection or native/full multiplication theorem.',
                  public_dependency_manifest=manifest, records=records)
    (out/'RESULT.json').write_bytes((json.dumps(result,indent=2,sort_keys=True)+'\n').encode())
    print(json.dumps(dict(status=result['status'],theorems=len(names),axioms=sorted(set().union(*map(set,found.values()))),output=str(out)),indent=2))


if __name__ == '__main__':
    main()
