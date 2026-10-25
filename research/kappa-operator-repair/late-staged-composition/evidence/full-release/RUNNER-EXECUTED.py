#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Full isolated release of PR4076 staged entries plus receiver sharing.

The exact PR4076 preparation, terminal review, staged-entry review, receiver
review, five native stages and complete inherited release remain mandatory.
Only literal receiver indices/profile, exact source identity and file counts
are adapted. The previously tested allocation-only audit adapter is retained.
Based on composed-supplier/run_release.py and PR4076/PR3945 full_replay.py.
Substantial OpenAI assistance; all predecessor credits remain in their files.
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
OLD = REPO/'research/kappa-adaptive-continuation'
P4076 = HERE.parent/'sources/PR4076/research/staged544-triple-entry-fill'
LABEL = 'triple-staged-entry-and-receiver-share-20261019'
LOWER = Q('0.001730970419199163702738')
UPPER = Q('0.001730970419199163702739')
LOCAL = {'1':2487,'2':713,'3':224,'4':102,'5':20,'8':8}
GLOBAL = {'1':8057880,'2':2310120,'3':748602,'4':330480,'5':66690,'8':25920,'48':138438}
STAGED_MANIFEST = '189cd6d85ce16f7eb840f3cedffe6041ac82281fdfd69df2390c0ff90bf74f78'
STAGED_ADAPTER = 'dd62c572925b3cfde07c4ddd2a257b46242f7555d91466efb72035cf6023afb7'
COMPOSED_MANIFEST = '4116ef61479e509811b60b5fd4e84db8811dae079092f2f83bdcc2c80052c0da'
FINITE_INVOICE_SHA256 = 'c9de9aeaa3cf4e11d27d4fc95ef94913301a6bf99fa8f919fb4f643793a7dc47'
OPERATOR_ADMISSION_SHA256 = '98d2936c758703c25637cf335e06691f8a55b3717105595e350917782b449b47'
CANDIDATES = {
    'base':'df31495cff95a1e512da398f52841c6b5ade29067869b3d68b89d756a5641112',
    'extra':'9a28f7ef91938c0866e408eb06e03eb5f8e727a00b44eb936ddd5ed48704bd4c',
}
WHEELS = {
    'sympy-1.14.0-py3-none-any.whl':'e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5',
    'mpmath-1.3.0-py3-none-any.whl':'a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def write(path, value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def tree(path, exclude=()):
    return {f.relative_to(path).as_posix():sha(f) for f in sorted(path.rglob('*'))
            if f.is_file() and f.relative_to(path).as_posix() not in exclude}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work',type=Path,required=True)
    source_mode = ap.add_mutually_exclusive_group()
    source_mode.add_argument('--prepared-staged',action='store_true',help='Use only the exact untouched PR4076 prepare-only state.')
    source_mode.add_argument('--resume-preflight',action='store_true',help='Resume this runner\'s exact checked source-only preflight.')
    ap.add_argument('--preflight-only',action='store_true',help='Prepare and check all three word reviews; do not require native receipts or run admission.')
    ap.add_argument('--reuse-native-root',type=Path,default=HERE)
    ap.add_argument('--prepare-only',action='store_true',help='After native binding, run the inherited admission preparation without full release.')
    args = ap.parse_args()
    need(__debug__,'Assertions must remain enabled')
    work = args.work.resolve()
    need(work.is_relative_to(HERE) and 'release-work' in work.relative_to(HERE).parts,
         'Runtime work must be isolated within this scope under a release-work directory')
    need(not (args.preflight_only and args.prepare_only),'Choose source preflight or admission preparation')
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
               AUDIT_RUNTIME_CONTROLS='fork' if hasattr(os,'fork') else 'pickle')
    env.pop('PYTHONOPTIMIZE',None)
    for tag,digest in CANDIDATES.items():
        need(sha(HERE/'candidate'/f'BORROW-WORD-43{tag}.json.gz')==digest,'Exact composed candidate '+tag)
    source = work/'inputs/source'
    borrow = source/'new/borrow'
    cache = work/'inputs/native-cache'
    stages = read(work/'STAGES.json') if args.resume_preflight else []
    protected_tree = None

    def run(name, command):
        if protected_tree is not None:
            need(tree(source,('MANIFEST.json',))==protected_tree,'Scientific source changed before '+name)
        start = time.monotonic()
        log = work/(name+'.log')
        with log.open('w') as stream:
            result = subprocess.run(command,env=env,stdout=stream,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        stages.append(dict(name=name,command=command,exit_code=result.returncode,
                           seconds=time.monotonic()-start,log_sha256=sha(log)))
        write(work/'STAGES.json',stages)
        if protected_tree is not None:
            current = tree(source,('MANIFEST.json',))
            if current != protected_tree:
                write(work/('SOURCE-CHANGES-AFTER-'+name+'.json'),
                      {p:dict(before=protected_tree.get(p),after=current.get(p))
                       for p in set(protected_tree)|set(current) if protected_tree.get(p)!=current.get(p)})
            need(current==protected_tree,'Scientific source changed during '+name)
        need(result.returncode==0,'Failed '+name+'; inspect '+str(log))
        print('PASS',name,flush=True)

    if not args.resume_preflight:
        if not args.prepared_staged:
            need(not work.exists(),'Fresh work directory')
            command = [sys.executable,'-B',str(P4076/'admission/full_replay.py'),'--work',str(work),
                       '--archive',str(OLD/'sources/PR3815/research/staged544-producer-return/REPLAY-INPUTS.tar.gz'),
                       '--prepare-only']
            result = subprocess.run(command,env=env,stdin=subprocess.DEVNULL)
            need(result.returncode==0,'Exact PR4076 source preparation')
        prepared = read(work/'PREPARED.json')
        need(prepared['status']=='PASS_STAGED_ENTRY_SOURCE_RECONSTRUCTION'
             and prepared['source_manifest_sha256']==STAGED_MANIFEST
             and prepared['source_files']==672,'Exact PR4076 source receipt')
        need(sha(work/'ADAPTER.json')==prepared['admission_adapter_sha256']==STAGED_ADAPTER,
             'Exact PR4076 inherited admission adaptation')
        need(sha(work/'admit_staged.py')==read(work/'ADAPTER.json')['effective_engine_sha256'],
             'Exact PR4076 effective admission engine')
        need(not (work/'SOURCE-ADAPTATION.json').exists(),'Unmodified prepared source')
        before = tree(source,('MANIFEST.json',))
        need(len(before)==672 and sha(source/'MANIFEST.json')==STAGED_MANIFEST
             and before==read(source/'MANIFEST.json'),'Exact 672-file source closure')
        parents = borrow/'receiver-share-parent'
        parents.mkdir()
        patches = []

        def patch(path, old, new, count=1):
            digest = sha(path)
            body = path.read_text()
            need(body.count(old)==count,'Exact literal patch preimage '+str(path)+' '+repr(old))
            path.write_text(body.replace(old,new))
            patches.append(dict(path=path.relative_to(work).as_posix(),before_sha256=digest,
                                after_sha256=sha(path),old=old,new=new,occurrences=count))

        for name in ('receiver_share.py','review_receiver_share.py'):
            shutil.copy2(OLD/'admission'/name,borrow/name)
        patch(borrow/'receiver_share.py','PROFILE = {1: 2439, 2: 724, 3: 225, 4: 102, 5: 20, 8: 8}',
              'PROFILE = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}')
        patch(borrow/'receiver_share.py',"'1': 2440, '2': 725, '3': 224, '4': 102, '5': 20, '8': 8",
              "'1': 2488, '2': 714, '3': 223, '4': 102, '5': 20, '8': 8")
        patch(borrow/'receiver_share.py','[692:694]','[683:685]',count=2)
        patch(borrow/'receiver_share.py','warp[0] >= 694','warp[0] >= 685')
        patch(borrow/'review_receiver_share.py','{4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}',
              '{5: 28, 6: 18, 7: 56, 8: 93, 9: 213}')
        patch(borrow/'review_receiver_share.py',"parent['B'][692:694] == R.OLD and word['B'][692:695] == R.NEW",
              "parent['B'][683:685] == R.OLD and word['B'][683:686] == R.NEW")
        patch(borrow/'review_receiver_share.py',"mutant['B'][694][3]","mutant['B'][685][3]")
        patch(borrow/'review_receiver_share.py',"mutant['B'][692][3]","mutant['B'][683][3]",count=2)
        sys.path.insert(0,str(borrow))
        edit = load(borrow/'receiver_share.py','late_release_receiver')
        words = {}
        registry = read(source/'new/BORROW-PROVIDERS.json')
        for tag,pid in [('base','gauge44'),('extra','extra')]:
            name = f'BORROW-WORD-43{tag}.json.gz'
            destination = borrow/'words'/name
            need(destination.read_bytes()==(P4076/'inputs'/f'NEW-{tag}.json.gz').read_bytes(),
                 'Exact staged parent '+tag)
            shutil.copy2(destination,parents/name)
            candidate = HERE/'candidate'/name
            generated = edit.apply(read(destination))
            need(generated==read(candidate),'Exact receiver composition '+tag)
            need(json.dumps(generated,sort_keys=True,separators=(',',':')).encode()
                 ==gzip.decompress(candidate.read_bytes()),'Canonical composed word bytes '+tag)
            destination.write_bytes(candidate.read_bytes())
            need(registry[pid]['actual_paid_profile']=={'1':2488,'2':714,'3':223,'4':102,'5':20,'8':8},
                 'Staged provider profile '+tag)
            registry[pid]['actual_paid_profile']=LOCAL
            words[tag]=dict(parent_sha256=sha(parents/name),word_sha256=sha(destination))
        write(source/'new/BORROW-PROVIDERS.json',registry)
        patch(source/'new/rebuild_borrow.py','    final=json.loads(gzip.decompress(shipped.read_bytes()))',
              "    import receiver_share\n"
              "    assert chain[-1]==json.loads(gzip.decompress((D/'receiver-share-parent'/f'BORROW-WORD-43{wt}.json.gz').read_bytes()))\n"
              "    chain.append(receiver_share.apply(chain[-1]));steps.append('triple-staged-plus-receiver-share')\n"
              '    final=json.loads(gzip.decompress(shipped.read_bytes()))')
        patch(borrow/'staged_entries_review.py',"P / 'words' / f'BORROW-WORD-43{tag}.json.gz'",
              "P / 'receiver-share-parent' / f'BORROW-WORD-43{tag}.json.gz'")
        patch(source/'verify.py',"run('staged-entries-independent-word-review',P/'new/borrow/staged_entries_review.py')",
              "run('staged-entries-independent-word-review',P/'new/borrow/staged_entries_review.py')\n"
              "run('receiver-sharing-independent-word-review',P/'new/borrow/review_receiver_share.py')")
        runtime = OLD/'runtime-repair/audit_fast.py'
        fixtures = read(OLD/'runtime-repair/FIXTURES.json')
        need(sha(source/'audit_fast.py')=='26950da76589b13cd9c452fdee1b0c354806977f881299bd94073f00e4646fcd',
             'Retained runtime adapter preimage')
        need(sha(runtime)==fixtures['adapter_sha256']=='30a39a3612efde96a0db189c14053afe5e012e56de1a89863596a078a8b64381'
             and fixtures['status']=='PASS_RUNTIME_ADAPTER_FAILURE_MODES' and len(fixtures['checks'])==19,
             'Tested allocation-only runtime adapter')
        runtime_before = sha(source/'audit_fast.py')
        (source/'audit_fast.py').write_bytes(runtime.read_bytes())
        after = tree(source,('MANIFEST.json',))
        need(set(before)<=set(after) and len(after)==676,'Complete 676-file extended source inventory')
        write(source/'MANIFEST.json',after)
        manifest = sha(source/'MANIFEST.json')
        need(manifest==COMPOSED_MANIFEST,'Exact independently prepared composed source manifest')
        write(work/'SOURCE-ADAPTATION.json',dict(status='PASS_LITERAL_PR4076_AND_RECEIVER_DERIVATIONS',
              predecessor_manifest_sha256=STAGED_MANIFEST,current_manifest_sha256=manifest,
              source_file_count=len(after),source_label=LABEL,words=words,exact_patches=patches,
              changed_files={p:dict(before=before.get(p),after=after[p]) for p in after if before.get(p)!=after[p]},
              runtime=dict(before_sha256=runtime_before,after_sha256=sha(runtime),fixtures_sha256=sha(OLD/'runtime-repair/FIXTURES.json')),
              scope='Terminal and staged-entry reviews stay bound to their exact parents. Receiver controls use the exact shifted event indices. No scientific predicate is removed.'))
        adapter = work/'admit_composed.py'
        shutil.copy2(work/'admit_staged.py',adapter)
        admission_patches = []
        for old,new in [("commit='staged-entries-608-609-600-20261019'",f"commit='{LABEL}'"),
                        ("manifest='"+STAGED_MANIFEST+"'","manifest='"+manifest+"'"),
                        ('helpers=408,source_file_count=672','helpers=408,source_file_count=676')]:
            body = adapter.read_text()
            need(body.count(old)==1,'Exact late admission profile preimage')
            adapter.write_text(body.replace(old,new))
            admission_patches.append([old,new])
        compile(adapter.read_text(),str(adapter),'exec')
        write(work/'COMPOSED-ADMISSION-ADAPTER.json',dict(original_sha256=sha(work/'admit_staged.py'),
              adapted_sha256=sha(adapter),exact_replacements=admission_patches,
              scope='Only the exact source commit, manifest and file count change after the inherited frozen-SPEC control-count adaptation.'))
        protected_tree = after
        run('independent-terminal-word',[sys.executable,'-B',str(borrow/'terminal_review.py')])
        run('independent-staged-word',[sys.executable,'-B',str(borrow/'staged_entries_review.py')])
        run('independent-receiver-word',[sys.executable,'-B',str(borrow/'review_receiver_share.py')])
        write(work/'PREFLIGHT-RESULT.json',dict(status='PASS_ALL_THREE_WORD_REVIEWS_SOURCE_READY_NOT_ADMITTED',
              runner_sha256=sha(Path(__file__)),source_manifest_sha256=manifest,source_files=676,
              source_adaptation_sha256=sha(work/'SOURCE-ADAPTATION.json'),
              admission_adapter_receipt_sha256=sha(work/'COMPOSED-ADMISSION-ADAPTER.json'),
              admission_engine_sha256=sha(adapter),candidate_gzip_sha256=CANDIDATES,
              completed_reviews=stages))
    else:
        preflight = read(work/'PREFLIGHT-RESULT.json')
        need(preflight['status']=='PASS_ALL_THREE_WORD_REVIEWS_SOURCE_READY_NOT_ADMITTED'
             and preflight['runner_sha256']==sha(Path(__file__)),'Exact source-preflight runner')
        need(preflight['candidate_gzip_sha256']==CANDIDATES,'Preflight candidate pins')
        need(sha(work/'SOURCE-ADAPTATION.json')==preflight['source_adaptation_sha256']
             and sha(work/'COMPOSED-ADMISSION-ADAPTER.json')==preflight['admission_adapter_receipt_sha256'],
             'Exact source and admission adaptations')
        adapter = work/'admit_composed.py'
        need(sha(adapter)==preflight['admission_engine_sha256'],'Exact checked admission engine')
        after = tree(source,('MANIFEST.json',))
        manifest = sha(source/'MANIFEST.json')
        need(manifest==preflight['source_manifest_sha256']==COMPOSED_MANIFEST and len(after)==676
             and after==read(source/'MANIFEST.json'),'Exact resumed 676-file scientific source')
        need([s['name'] for s in stages]==['independent-terminal-word','independent-staged-word','independent-receiver-word']
             and stages==preflight['completed_reviews'] and all(s['exit_code']==0 and sha(work/(s['name']+'.log'))==s['log_sha256'] for s in stages),
             'All three completed review stages and exact logs')
        protected_tree = after
    if args.preflight_only:
        print('PASS_ALL_THREE_WORD_REVIEWS_SOURCE_READY_NOT_ADMITTED',manifest,flush=True)
        return

    # Native receipt reuse means byte-identical outputs of five freshly executed
    # stages; a provider name or a headline alone cannot satisfy this gate.
    need(sha(HERE/'invoice/RESULT.json')==FINITE_INVOICE_SHA256,'Exact independently executed finite invoice receipt')
    finite_invoice = read(HERE/'invoice/RESULT.json')
    need(finite_invoice['status']=='PASS_FRESH_NATIVE_LITERAL_OWNERS_AND_THREE_ENGINE_COMPLEX_INVOICE'
         and finite_invoice['profile']==GLOBAL
         and Q(finite_invoice['root']['rational'][0])==LOWER
         and Q(finite_invoice['root']['rational'][1])==UPPER,'Exact complete finite late invoice')
    for relative,digest in finite_invoice['source_pins'].items():
        need(sha(REPO/relative)==digest,'Exact finite invoice dependency '+relative)
    need(sha(HERE/'T360-OPERATOR-ADMISSION.json')==OPERATOR_ADMISSION_SHA256,'Exact independently executed full-operator receipt')
    operator = read(HERE/'T360-OPERATOR-ADMISSION.json')
    need(operator['status']=='PASS_ACTUAL_T360_ALL_CHARACTER_OPERATOR_ADMISSION'
         and operator['complete_owner_invoice_sha256']==FINITE_INVOICE_SHA256
         and operator['all_Fourier_characters'] is True and operator['all_positive_tensor_multiplicities'] is True
         and operator['no_axis_transfer_overlay'] is True
         and operator['actual_calls']==3240 and operator['actual_hosted_rows']==1321920
         and operator['exact_phase_identities']==10416
         and operator['actual_residual_profile']=={'3':22842,'5':1890,'48':138438},'Full late operator and owner binding')
    for relative,digest in operator['input_files'].items():
        need(sha(REPO/relative)==digest,'Exact operator dependency '+relative)
    for tag in ('base','extra'):
        native = args.reuse_native_root.resolve()/('native-'+tag)
        binding = operator['actual_provider_bindings'][tag]
        need(binding['candidate_sha256']==CANDIDATES[tag]
             and binding['native_receipt_sha256']==sha(native/'RESULT.json')
             and binding['canonical_native_sha256']==sha(native/'native/local/CANONICAL-WORD.json.gz'),
             'Exact operator/provider source linkage '+tag)
    registry = read(source/'new/BORROW-PROVIDERS.json')
    receipt = read(work/'inputs/NATIVE-RECEIPT.json')
    need(tree(cache)==receipt['cache_files'],'All retained native cache files')
    native_receipts = {}
    for tag,pid in [('base','gauge44'),('extra','extra')]:
        native = args.reuse_native_root.resolve()/('native-'+tag)
        result = read(native/'RESULT.json')
        word = borrow/'words'/f'BORROW-WORD-43{tag}.json.gz'
        need(result['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and result['word_sha256']==sha(word)==CANDIDATES[tag],
             'Exact freshly executed native word '+tag)
        need(result['source_sha256']==tree(source/'new/fastnative/vendor')
             and result['source_sha256']==tree(native/'source'),'All native compiler sources '+tag)
        need([r['step'] for r in result['steps']]==['native','ledgers','local-replay','wrappers','phases']
             and all(r['exit_code']==0 for r in result['steps']),'Five completed native stages '+tag)
        need(read(native/'native/local/FULL-WORD.json.gz')==read(word),'Native complete word '+tag)
        entry = cache/sha(word)
        need(not entry.exists(),'Fresh native cache entry '+tag)
        shutil.copytree(native/'native',entry)
        write(entry/'CACHE.json',dict(word_sha256=sha(word),files=tree(entry)))
        receipt['providers'][tag]=dict(word_sha256=sha(word),complete_native_files=tree(entry,('CACHE.json',)))
        canonical = read(entry/'local/CANONICAL-WORD.json.gz')
        widths = [len(canonical['frames'][canonical['final'][r]])-len(canonical['frames'][canonical['start'][r]]) for r in range(224,632)]
        need(widths==registry[pid]['widths'],'Complete ordered helper widths '+tag)
        checks = read(entry/'local/LOCAL-CHECKS.json')
        need(all(checks[d]['paid_profile']==LOCAL for d in ('forward','backward'))
             and registry[pid]['actual_paid_profile']==LOCAL,'Actual native local profile '+tag)
        native_receipts[tag]=dict(result_sha256=sha(native/'RESULT.json'),word_sha256=sha(word),
                                  native_files=tree(native/'native'),scientific_sources=result['source_sha256'])
    write(work/'ACTUAL-NATIVE-SOURCES.json',native_receipts)
    receipt.update(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',source_commit=LABEL,
                   manifest_sha256=manifest,cache_files=tree(cache))
    write(work/'NATIVE-RECEIPT.json',receipt)
    need(tree(source,('MANIFEST.json',))==protected_tree,'Scientific source unchanged during native binding')
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
    arguments = {'source':source,'fill':P4076/'owner/FILL.json.gz','order':P4076/'owner/inputs/ORDER.json',
                 'dispatch':P4076/'owner/inputs/DISPATCH.json','native-cache':cache,'native-receipt':work/'NATIVE-RECEIPT.json',
                 'work':work/'admission','replica-helper-dir':work/'inputs/helpers',
                 'reconstructor':work/'inputs/helpers/reconstruct_replica.py',
                 'comparison-claim':P4076/'admission/pr3945/PR3682-CLAIM.json','blocknorm-checker':work/'inputs/extension_blocknorm.py'}
    command = [sys.executable,'-B',str(adapter)]
    for key,value in arguments.items():
        command += ['--'+key,str(value)]
    command += ['--source-profile','staged544','--comparison-profile','pr3682','--jobs','1']
    if args.prepare_only:
        command += ['--prepare-only']
    run('prepare-admission' if args.prepare_only else 'complete-admission',command)
    result = read(work/'admission/RESULT.json')
    if args.prepare_only:
        need(result['status']=='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED','Prepared-only admission status')
        return
    expected = LOWER-Q(1,10**46)-Q(1,10**70)
    need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and Q(result['complex_lower'])==LOWER and Q(result['kappa'])==expected
         and result['profile']==GLOBAL,'Exact complete late release headline and profile')
    need(tree(source,('MANIFEST.json',))==protected_tree,'Scientific source unchanged by full replay')
    write(work/'RESULT.json',dict(status='PASS_STAGED_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE',
          kappa_rational=str(expected),complex_lower=str(LOWER),complex_upper=str(UPPER),profile=GLOBAL,
          source_manifest_sha256=manifest,source_file_count=len(protected_tree),runner_sha256=sha(Path(__file__)),
          stages=stages,native_receipt_sha256=sha(work/'NATIVE-RECEIPT.json'),
          finite_invoice_sha256=sha(HERE/'invoice/RESULT.json'),operator_admission_sha256=sha(HERE/'T360-OPERATOR-ADMISSION.json'),
          release_result_sha256=sha(work/'admission/RESULT.json'),release_receipt_sha256=result['release_receipt_sha256'],
          scope='Complete inherited conditional release of the literal PR4076 and receiver composition. The separate full global operator gate and all inherited uniform physical/outer hypotheses remain required.'))
    print('PASS_STAGED_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE',flush=True)


if __name__=='__main__':
    main()
