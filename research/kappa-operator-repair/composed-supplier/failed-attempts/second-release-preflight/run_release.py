#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose two literal word derivations and run the retained full admission.

PR3945's terminal recipe and every predecessor review remain executable.
The receiver identity is appended, both changed native providers are bound
byte for byte, and the complete owner/resource/precision/outer pipeline runs.
Only the new source identity, data-derived control counts (PR3945), and the
previously tested allocation-only runtime adapter change admission plumbing.
No scientific gate is removed. Substantial OpenAI assistance.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = REPO / 'research/kappa-adaptive-continuation'
P3945 = HERE.parent / 'sources/PR3945/research/staged544-terminal-gap-fill'
LABEL = 'terminal-width5-and-receiver-share-20261019'
LOWER = Q('0.001730824595303184580890')
UPPER = Q('0.001730824595303184580891')
LOCAL = {'1':2481,'2':711,'3':219,'4':109,'5':20,'8':8}
GLOBAL = {'1':8038440,'2':2303640,'3':732888,'4':353160,'5':69120,'8':25920,'48':137952}
TERMINAL_MANIFEST = '3d2ee0175b0cd8aec80c12fef82c2da3a3a54785ca9113140762fd5c41979608'
WHEELS = {
    'sympy-1.14.0-py3-none-any.whl':'e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5',
    'mpmath-1.3.0-py3-none-any.whl':'a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c',
}

def need(ok, why):
    if not ok:
        raise ValueError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)

def write(p, obj):
    p.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')

def tree(p, exclude=()):
    return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*'))
            if f.is_file() and f.relative_to(p).as_posix() not in exclude}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--prepared-terminal', action='store_true',
                    help='Accept only the exact untouched PR3945 prepare-only source state.')
    ap.add_argument('--reuse-native-root', type=Path, default=HERE)
    ap.add_argument('--prepare-only', action='store_true')
    a = ap.parse_args()
    need(__debug__, 'Assertions must remain enabled')
    work = a.work.resolve()
    need(work.is_relative_to(HERE.parent) and not work.is_relative_to(P3945), 'New scoped work directory')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               AUDIT_RUNTIME_CONTROLS='fork' if hasattr(os, 'fork') else 'pickle')
    env.pop('PYTHONOPTIMIZE', None)
    stages = []
    protected_source = None
    protected_tree = None
    def run(name, command):
        if protected_source is not None:
            need(tree(protected_source,('MANIFEST.json',))==protected_tree,
                 'Scientific source changed before '+name)
        start = time.monotonic()
        log = work / (name + '.log')
        with log.open('w') as f:
            result = subprocess.run(command, env=env, stdout=f, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL)
        stages.append(dict(name=name, command=command, exit_code=result.returncode,
                           seconds=time.monotonic()-start, log_sha256=sha(log)))
        write(work/'STAGES.json', stages)
        if protected_source is not None:
            current_tree = tree(protected_source,('MANIFEST.json',))
            if current_tree != protected_tree:
                write(work/('SOURCE-CHANGES-AFTER-'+name+'.json'),
                      {p:dict(before=protected_tree.get(p),after=current_tree.get(p))
                       for p in set(protected_tree)|set(current_tree)
                       if protected_tree.get(p)!=current_tree.get(p)})
            need(current_tree==protected_tree,'Scientific source changed during '+name)
        need(result.returncode == 0, 'Failed '+name+'; inspect retained log '+str(log))
        print('PASS', name, flush=True)
    if not a.prepared_terminal:
        need(not work.exists(), 'Fresh work directory')
        command = [sys.executable, '-B', str(P3945/'admission/full_replay.py'),
                   '--work', str(work), '--archive', str(OLD/'sources/PR3815/research/staged544-producer-return/REPLAY-INPUTS.tar.gz'),
                   '--prepare-only']
        result = subprocess.run(command, env=env, stdin=subprocess.DEVNULL)
        need(result.returncode == 0, 'Exact terminal preparation')
    prepared = read(work/'PREPARED.json')
    need(prepared['status'] == 'PASS_TERMINAL_SOURCE_RECONSTRUCTION'
         and prepared['new_source_manifest_sha256'] == TERMINAL_MANIFEST, 'Exact terminal prepared receipt')
    need(not (work/'SOURCE-ADAPTATION.json').exists(), 'No already-mutated prepared source')
    source = work/'inputs/source'
    before = tree(source, ('MANIFEST.json',))
    need(len(before) == 666 and sha(source/'MANIFEST.json') == TERMINAL_MANIFEST
         and before == read(source/'MANIFEST.json'), 'Exact 666 terminal scientific source files')
    need(sha(work/'ADAPTER.json') == prepared['admission_adapter_sha256'], 'Terminal admission adaptation receipt')
    need(sha(work/'admit_terminal.py') == read(work/'ADAPTER.json')['effective_engine_sha256'], 'Terminal admission engine')
    borrow = source/'new/borrow'
    parents = borrow/'receiver-share-parent'
    parents.mkdir()
    patches = []
    def patch(path, old, new):
        before_sha = sha(path)
        body = path.read_text()
        need(body.count(old) == 1, 'Exact literal preimage '+str(path))
        path.write_text(body.replace(old, new))
        patches.append(dict(path=path.relative_to(work).as_posix(), before_sha256=before_sha,
                            after_sha256=sha(path), old=old, new=new))
    for name in ('receiver_share.py', 'review_receiver_share.py'):
        shutil.copy2(OLD/'admission'/name, borrow/name)
    patch(borrow/'receiver_share.py',
          'PROFILE = {1: 2439, 2: 724, 3: 225, 4: 102, 5: 20, 8: 8}',
          'PROFILE = {1: 2481, 2: 711, 3: 219, 4: 109, 5: 20, 8: 8}')
    patch(borrow/'receiver_share.py',
          "'1': 2440, '2': 725, '3': 224, '4': 102, '5': 20, '8': 8",
          "'1': 2482, '2': 712, '3': 218, '4': 109, '5': 20, '8': 8")
    patch(borrow/'review_receiver_share.py',
          '{4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}',
          '{5: 28, 6: 18, 7: 53, 8: 96, 9: 213}')
    sys.path.insert(0, str(borrow))
    spec = importlib.util.spec_from_file_location('composed_release_receiver', borrow/'receiver_share.py')
    edit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(edit)
    words = {}
    for tag in ('base','extra'):
        name = 'BORROW-WORD-43'+tag+'.json.gz'
        destination = borrow/'words'/name
        shutil.copy2(destination, parents/name)
        candidate = HERE/'candidate'/name
        generated = edit.apply(read(destination))
        need(generated == read(candidate), 'Exact composed word reconstruction '+tag)
        need(json.dumps(generated, sort_keys=True, separators=(',',':')).encode()
             == gzip.decompress(candidate.read_bytes()), 'Canonical candidate bytes '+tag)
        shutil.copy2(candidate, destination)
        words[tag] = dict(parent_sha256=sha(parents/name), word_sha256=sha(destination))
    patch(source/'new/rebuild_borrow.py',
          '    final=json.loads(gzip.decompress(shipped.read_bytes()))',
          "    import receiver_share\n"
          "    assert chain[-1]==json.loads(gzip.decompress((D/'receiver-share-parent'/f'BORROW-WORD-43{wt}.json.gz').read_bytes()))\n"
          "    chain.append(receiver_share.apply(chain[-1]));steps.append('terminal-plus-receiver-share')\n"
          '    final=json.loads(gzip.decompress(shipped.read_bytes()))')
    patch(borrow/'terminal_review.py',
          "(P/'words'/f'BORROW-WORD-43{tag}.json.gz')",
          "(P/'receiver-share-parent'/f'BORROW-WORD-43{tag}.json.gz')")
    patch(source/'verify.py',
          "run('terminal-width5-independent-word-review',P/'new/borrow/terminal_review.py')",
          "run('terminal-width5-independent-word-review',P/'new/borrow/terminal_review.py')\n"
          "run('receiver-sharing-independent-word-review',P/'new/borrow/review_receiver_share.py')")
    registry = read(source/'new/BORROW-PROVIDERS.json')
    receipt = read(work/'inputs/NATIVE-RECEIPT.json')
    cache = work/'inputs/native-cache'
    need(tree(cache) == receipt['cache_files'], 'All retained native cache files')
    native_receipts = {}
    for tag, pid in [('base','gauge44'),('extra','extra')]:
        native = a.reuse_native_root.resolve()/('native-'+tag)
        result = read(native/'RESULT.json')
        word = borrow/'words'/('BORROW-WORD-43'+tag+'.json.gz')
        need(result['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY'
             and result['word_sha256'] == sha(word), 'Exact freshly executed native word '+tag)
        need(result['source_sha256'] == tree(source/'new/fastnative/vendor')
             and result['source_sha256'] == tree(native/'source'), 'All native compiler sources '+tag)
        need([r['step'] for r in result['steps']] == ['native','ledgers','local-replay','wrappers','phases']
             and all(r['exit_code']==0 for r in result['steps']), 'Five completed native stages '+tag)
        need(read(native/'native/local/FULL-WORD.json.gz') == read(word), 'Native complete word '+tag)
        entry = cache/sha(word)
        need(not entry.exists(), 'Fresh cache entry '+tag)
        shutil.copytree(native/'native', entry)
        write(entry/'CACHE.json', dict(word_sha256=sha(word), files=tree(entry)))
        receipt['providers'][tag] = dict(word_sha256=sha(word), complete_native_files=tree(entry,('CACHE.json',)))
        canonical = read(entry/'local/CANONICAL-WORD.json.gz')
        widths = [len(canonical['frames'][canonical['final'][r]])-len(canonical['frames'][canonical['start'][r]])
                  for r in range(224,632)]
        need(widths == registry[pid]['widths'], 'Complete ordered helper widths '+tag)
        checks = read(entry/'local/LOCAL-CHECKS.json')
        need(all(checks[d]['paid_profile']==LOCAL for d in ['forward','backward']), 'Actual native local price '+tag)
        registry[pid]['actual_paid_profile'] = LOCAL
        native_receipts[tag] = dict(result_sha256=sha(native/'RESULT.json'), word_sha256=sha(word),
                                    native_files=tree(native/'native'), scientific_sources=result['source_sha256'])
    write(source/'new/BORROW-PROVIDERS.json', registry)
    write(work/'ACTUAL-NATIVE-SOURCES.json', native_receipts)
    runtime = OLD/'runtime-repair/audit_fast.py'
    fixtures = read(OLD/'runtime-repair/FIXTURES.json')
    need(sha(source/'audit_fast.py') == '26950da76589b13cd9c452fdee1b0c354806977f881299bd94073f00e4646fcd', 'Runtime predecessor')
    need(sha(runtime) == fixtures['adapter_sha256'] == '30a39a3612efde96a0db189c14053afe5e012e56de1a89863596a078a8b64381'
         and fixtures['status']=='PASS_RUNTIME_ADAPTER_FAILURE_MODES' and len(fixtures['checks'])==19, 'Tested allocation-only runtime adapter')
    runtime_before = sha(source/'audit_fast.py')
    shutil.copy2(runtime, source/'audit_fast.py')
    after = tree(source, ('MANIFEST.json',))
    need(set(before) <= set(after) and len(after)==670, 'Complete extended scientific source inventory')
    write(source/'MANIFEST.json', after)
    manifest = sha(source/'MANIFEST.json')
    receipt.update(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',
                   source_commit=LABEL, manifest_sha256=manifest, cache_files=tree(cache))
    write(work/'NATIVE-RECEIPT.json', receipt)
    write(work/'SOURCE-ADAPTATION.json', dict(status='PASS_LITERAL_TERMINAL_AND_RECEIVER_DERIVATIONS',
          predecessor_manifest_sha256=TERMINAL_MANIFEST, current_manifest_sha256=manifest,
          source_file_count=len(after), source_label=LABEL, words=words, exact_patches=patches,
          changed_files={p:dict(before=before.get(p),after=after[p]) for p in after if before.get(p)!=after[p]},
          runtime=dict(before_sha256=runtime_before,after_sha256=sha(runtime),fixtures_sha256=sha(OLD/'runtime-repair/FIXTURES.json')),
          scope='Both predecessor word reviews remain bound to their exact parents. All new semantics, native, owner, resource, precision and outer gates remain executed.'))
    adapter = work/'admit_composed.py'
    shutil.copy2(work/'admit_terminal.py', adapter)
    admission_patches = []
    for old,new in [("commit='terminal-width5-20261019'",f"commit='{LABEL}'"),
                    ("manifest='"+TERMINAL_MANIFEST+"'","manifest='"+manifest+"'"),
                    ('helpers=408,source_file_count=666','helpers=408,source_file_count=670')]:
        body = adapter.read_text()
        need(body.count(old)==1, 'Exact composed admission profile preimage')
        adapter.write_text(body.replace(old,new))
        admission_patches.append([old,new])
    compile(adapter.read_text(),str(adapter),'exec')
    write(work/'COMPOSED-ADMISSION-ADAPTER.json',dict(original_sha256=sha(work/'admit_terminal.py'),
          adapted_sha256=sha(adapter), exact_replacements=admission_patches,
          scope='Only exact current source identity and file count change after the retained PR3945 data-derived control-count adaptation.'))
    protected_source, protected_tree = source, after
    wheel_dir = OLD/'replay-support/wheels'
    for name,digest in WHEELS.items():
        need(sha(wheel_dir/name)==digest,'Pinned outer dependency wheel')
    run('install-outer-dependencies',[sys.executable,'-B','-m','pip','install','--disable-pip-version-check',
        '--root-user-action=ignore','--no-compile','--no-index','--no-deps','--target',str(work/'python-deps'),
        *[str(wheel_dir/name) for name in sorted(WHEELS)]])
    env['PYTHONPATH']=str(work/'python-deps')+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    run('dependencies',[sys.executable,'-B','-c',
        "import json,numpy,scipy,sympy,mpmath;assert sympy.__version__=='1.14.0';assert mpmath.__version__=='1.3.0';print(json.dumps({x:globals()[x].__version__ for x in ['numpy','scipy','sympy','mpmath']},sort_keys=True))"])
    write(work/'DEPENDENCIES.json',dict(wheels=WHEELS,versions=json.loads((work/'dependencies.log').read_text())))
    run('independent-terminal-word',[sys.executable,'-B',str(borrow/'terminal_review.py')])
    run('independent-receiver-word',[sys.executable,'-B',str(borrow/'review_receiver_share.py')])
    args={'source':source,'fill':P3945/'owner/FILL.json.gz','order':P3945/'owner/inputs/ORDER.json',
          'dispatch':P3945/'owner/inputs/DISPATCH.json','native-cache':cache,'native-receipt':work/'NATIVE-RECEIPT.json',
          'work':work/'admission','replica-helper-dir':work/'inputs/helpers',
          'reconstructor':work/'inputs/helpers/reconstruct_replica.py',
          'comparison-claim':P3945/'admission/PR3682-CLAIM.json','blocknorm-checker':work/'inputs/extension_blocknorm.py'}
    command=[sys.executable,'-B',str(adapter)]
    for k,v in args.items():
        command+=['--'+k,str(v)]
    command+=['--source-profile','staged544','--comparison-profile','pr3682','--jobs','1']
    if a.prepare_only:
        command+=['--prepare-only']
    run('complete-admission' if not a.prepare_only else 'prepare-admission',command)
    result=read(work/'admission/RESULT.json')
    if a.prepare_only:
        need(result['status']=='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED','Prepared only status')
        return
    expected=LOWER-Q(1,10**46)-Q(1,10**70)
    need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and Q(result['complex_lower'])==LOWER and Q(result['kappa'])==expected
         and result['profile']==GLOBAL,'Exact current complete release headline and profile')
    need(tree(source,('MANIFEST.json',))==after,'Scientific source unchanged by replay')
    write(work/'RESULT.json',dict(status='PASS_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE',
          kappa_rational=str(expected),complex_lower=str(LOWER),complex_upper=str(UPPER),profile=GLOBAL,
          source_manifest_sha256=manifest,source_file_count=len(after),runner_sha256=sha(Path(__file__)),
          stages=stages,native_receipt_sha256=sha(work/'NATIVE-RECEIPT.json'),
          release_result_sha256=sha(work/'admission/RESULT.json'),release_receipt_sha256=result['release_receipt_sha256'],
          scope='Complete inherited conditional release for literal combined supplier. Full global operator guard is a separate additional obligation; uniform physical realization and outer hypotheses remain conditional.'))
    print('PASS_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE',flush=True)

if __name__=='__main__':
    main()
