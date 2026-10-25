"""Complete native/global/outer replay for the staged-entry derivative (helpers 608, 609, 600) of PR3945's words.

Reconstructs PR3945's 666-file source closure exactly as PR3945's own admission/full_replay.py does (pinned
predecessor archive, PR3945 terminal-width5 generator, its three literal source patches), then adds the staged-entry
generator on top: literal records from PR3945's NEW words to ours, a generalized PR3734-style applier, an independent
review with rejection controls, the rebuild-chain step, the provider registry, and our literal T360 owner fill.
The inherited admission engine runs with only the source-profile/file-count and frozen-SPEC count adaptations
that PR3945 already made.  Requires Python 3.12, numpy, scipy, sympy==1.14.0, mpmath==1.3.0.
Prepared by Rohan Arun with Anthropic Claude assistance; structure and engine adaptation follow Dugongue's PR3945
(OpenAI Codex assisted).  Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, tarfile, urllib.request
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
PR3945 = HERE / 'pr3945'                     # byte-identical copies of PR3945 admission inputs (see pr3945/SOURCES.json)
HEAD = 'fa041037a3374eaa08feeca0b26a5d6893194147'
ARCHIVE_URL = 'https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/' + HEAD + '/research/staged544-producer-return/REPLAY-INPUTS.tar.gz'
PR3945_SOURCE_MANIFEST = '3d2ee0175b0cd8aec80c12fef82c2da3a3a54785ca9113140762fd5c41979608'
COMMIT = 'staged-entries-608-609-600-20261019'


def need(ok, msg):
    if not ok: raise ValueError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def write(p, x): p.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n', encoding='utf8', newline='\n')
def tree(p, exclude=()): return {f.relative_to(p).as_posix(): sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.relative_to(p).as_posix() not in exclude}
def patch_text(path, old, new):
    body = path.read_text(encoding='utf8'); need(body.count(old) == 1, 'literal patch preimage ' + str(path))
    path.write_text(body.replace(old, new), encoding='utf8', newline='\n'); return [old, new]


def reconstruct_pr3945(work, archive):
    """Exactly PR3945 admission/full_replay.py up to its 666-file closure."""
    pins = read(PR3945 / 'PREDECESSOR.json'); need(sha(archive) == pins['archive_sha256'], 'pinned predecessor archive digest')
    inputs = work / 'inputs'; inputs.mkdir(); seen = set()
    with tarfile.open(archive) as t:
        for m in t:
            need(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.name not in seen and m.name in pins['files'], 'safe declared predecessor member')
            raw = t.extractfile(m).read(); need(hashlib.sha256(raw).hexdigest() == pins['files'][m.name], 'predecessor member digest')
            seen.add(m.name); out = inputs / m.name; out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(raw)
    need(seen == set(pins['files']), 'complete 756-file retained input inventory')
    source = inputs / 'source'
    need(sha(source / 'MANIFEST.json') == '4c4f7067b1b5404b59213f480e9d91c96ffc79b5458e2736b159f5a522ed2dc3', 'retained 660-source manifest')
    need(tree(source, ('MANIFEST.json',)) == read(source / 'MANIFEST.json'), 'retained source file hashes')
    borrow = source / 'new/borrow'; terminal = borrow / 'terminal'; terminal.mkdir(); registry = read(source / 'new/BORROW-PROVIDERS.json')
    shutil.copy2(PR3945 / 'terminal_applier.py', borrow / 'terminal_applier.py'); shutil.copy2(PR3945 / 'terminal_review.py', borrow / 'terminal_review.py')
    sys.path.insert(0, str(borrow)); import terminal_applier as T
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        name = 'BORROW-WORD-43' + tag + '.json.gz'; old = borrow / 'words' / name; before = read(old)
        final = PR3945 / ('NEW-' + tag + '.json.gz'); new = read(final)
        shutil.copy2(old, terminal / ('PRE-' + tag + '.json.gz')); old.write_bytes(final.read_bytes())
        record = {'source_canonical_sha256': T.canonical(before), 'candidate_canonical_sha256': T.canonical(new), 'new_fields': {k: v for k, v in new.items() if before[k] != v},
                  'source_attribution': 'PR3734 dataisfire and retained lineage; terminal derivative Dugongue/OpenAI Codex'}
        write(terminal / ('RECORD-' + tag + '.json'), record); need(T.apply(before, record) == new, 'declared terminal generator')
        origin = read(PR3945 / ('old-NATIVE-' + tag + '.json.gz'))['helper_origin']; need(len(origin) == 408, 'retained native helper order')
        registry[pid] = {'widths': [len(new['helper_final'].get(str(r), [1 << i for i in range(9)])) - len(new['start_extra'].get(str(r), [])) for r in origin],
                         'actual_paid_profile': new['report']['local_profile']}
    write(source / 'new/BORROW-PROVIDERS.json', registry)
    for patch in read(PR3945 / 'SOURCE-PATCHES.json'):
        out = source / patch['path']; need(sha(out) == patch['before_sha256'], 'generator patch source hash')
        body = out.read_text(encoding='utf8'); need(body.count(patch['old']) == 1, 'generator patch literal preimage')
        out.write_text(body.replace(patch['old'], patch['new']), encoding='utf8', newline='\n'); need(sha(out) == patch['after_sha256'], 'generator patch output hash')
    write(source / 'MANIFEST.json', tree(source, ('MANIFEST.json',)))
    need(len(read(source / 'MANIFEST.json')) == 666 and sha(source / 'MANIFEST.json') == PR3945_SOURCE_MANIFEST, 'exact PR3945 666-file source closure')
    return inputs, source, registry


def add_staged(source, registry):
    """Our additive staged-entry generator on top of PR3945's closure."""
    borrow = source / 'new/borrow'; staged = borrow / 'staged3'; staged.mkdir()
    for name in ('staged_entries_applier.py', 'staged_entries_review.py'): shutil.copy2(PACKAGE / 'recipe' / name, borrow / name)
    sys.path.insert(0, str(borrow)); import staged_entries_applier as S
    log = []
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        word = borrow / 'words' / ('BORROW-WORD-43' + tag + '.json.gz')
        need(word.read_bytes() == (PACKAGE / 'inputs' / ('OLD-' + tag + '.json.gz')).read_bytes(), 'PR3945 terminal word is our source word')
        shutil.copy2(word, staged / ('PRE-' + tag + '.json.gz'))
        shutil.copy2(PACKAGE / 'recipe' / ('RECORD-' + tag + '.json'), staged / ('RECORD-' + tag + '.json'))
        new = read(PACKAGE / 'inputs' / ('NEW-' + tag + '.json.gz'))
        need(S.apply(read(word), read(staged / ('RECORD-' + tag + '.json'))) == new, 'declared staged-entry generator')
        word.write_bytes((PACKAGE / 'inputs' / ('NEW-' + tag + '.json.gz')).read_bytes())
        origin = read(PR3945 / ('old-NATIVE-' + tag + '.json.gz'))['helper_origin']
        registry[pid] = {'widths': [len(new['helper_final'].get(str(r), [1 << i for i in range(9)])) - len(new['start_extra'].get(str(r), [])) for r in origin],
                         'actual_paid_profile': new['report']['local_profile']}
    write(source / 'new/BORROW-PROVIDERS.json', registry)
    log.append(patch_text(source / 'new/rebuild_borrow.py',
        "steps.append('terminal-width5')\n",
        "steps.append('terminal-width5')\n    import staged_entries_applier\n    chain.append(staged_entries_applier.apply(chain[-1],json.loads((D/'staged3'/f'RECORD-{wt}.json').read_text())));steps.append('staged-entries-608-609-600')\n"))
    log.append(patch_text(borrow / 'terminal_review.py', "(P/'words'/f'BORROW-WORD-43{tag}.json.gz')", "(P/'staged3'/f'PRE-{tag}.json.gz')"))
    log.append(patch_text(source / 'verify.py',
        "run('terminal-width5-independent-word-review',P/'new/borrow/terminal_review.py')\n",
        "run('terminal-width5-independent-word-review',P/'new/borrow/terminal_review.py')\nrun('staged-entries-independent-word-review',P/'new/borrow/staged_entries_review.py')\n"))
    write(source / 'MANIFEST.json', tree(source, ('MANIFEST.json',)))
    return log


def adapt_admission(original, admit, manifest, nfiles):
    need(sha(original) == '76f1b45793abb32a902a8d3cd353b39a018a35a277bb4e223e7508226b71eb6e', 'retained admission engine hash')
    body = original.read_text(encoding='utf8')
    old = "'staged544': dict(commit='staged544-literal-v1',manifest='4c4f7067b1b5404b59213f480e9d91c96ffc79b5458e2736b159f5a522ed2dc3'"
    new = f"'staged544': dict(commit='{COMMIT}',manifest='{manifest}'"
    need(body.count(old) == 1 and body.count('helpers=408,source_file_count=660') == 1, 'exact admission profile preimages')
    body = body.replace(old, new).replace('helpers=408,source_file_count=660', f'helpers=408,source_file_count={nfiles}')
    patch_log = [[old, new], ['helpers=408,source_file_count=660', f'helpers=408,source_file_count={nfiles}']]
    for old_count, new_count in [("len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==139", "len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==rd(spec)['expected']['assembly_controls_rejected']"),
                                 ("controls=dict(admission=139,bit=12,controller=15,independent_owner=8,geometry=6)", "controls=dict(admission=rd(P/'new/SPEC.json')['expected']['assembly_controls_rejected'],bit=12,controller=15,independent_owner=8,geometry=6)")]:
        variants = [(q + old_count.replace('\\', '\\\\').replace(q, '\\' + q) + q, q + new_count.replace('\\', '\\\\').replace(q, '\\' + q) + q) for q in [chr(39), chr(34)]]
        hits = [pair for pair in variants if body.count(pair[0]) == 1]; need(len(hits) == 1, 'exact inherited count patch destination')
        body = body.replace(*hits[0]); patch_log.append(list(hits[0]))
    admit.write_text(body, encoding='utf8', newline='\n'); compile(body, str(admit), 'exec')
    write(admit.with_name('ADAPTER.json'), {'original_engine_sha256': sha(original), 'effective_engine_sha256': sha(admit), 'literal_patches': patch_log,
                                           'scope': 'Same adaptation as PR3945: source-profile commit/manifest/file-count and frozen-spec mutation-count closure/report bindings only; scientific predicates unchanged.'})


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--archive', type=Path)
    ap.add_argument('--prepare-only', action='store_true'); ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()
    need(__debug__ and a.jobs > 0, 'assertions and positive jobs required'); work = a.work.resolve()
    need(not work.exists() and not work.is_relative_to(PACKAGE), 'fresh external work directory required'); work.mkdir(parents=True)
    archive = a.archive.resolve() if a.archive else work / 'predecessor.tar.gz'
    if a.archive is None:
        with urllib.request.urlopen(ARCHIVE_URL) as src, archive.open('wb') as dst: shutil.copyfileobj(src, dst)
    inputs, source, registry = reconstruct_pr3945(work, archive)
    patches = add_staged(source, registry)
    manifest = sha(source / 'MANIFEST.json'); nfiles = len(read(source / 'MANIFEST.json'))
    need(nfiles == 672, 'exact 672-file staged-entry source closure (PR3945 666 + six additive files)')
    adapt_admission(inputs / 'admit544.py', work / 'admit_staged.py', manifest, nfiles)
    write(work / 'PREPARED.json', {'status': 'PASS_STAGED_ENTRY_SOURCE_RECONSTRUCTION', 'predecessor_head': HEAD, 'pr3945_source_manifest_sha256': PR3945_SOURCE_MANIFEST,
                                   'source_manifest_sha256': manifest, 'source_files': nfiles, 'staged_source_patches': patches, 'admission_adapter_sha256': sha(work / 'ADAPTER.json')})
    if a.prepare_only: print('PASS_STAGED_ENTRY_SOURCE_RECONSTRUCTION', manifest, flush=True); return
    import numpy, scipy, sympy, mpmath
    need(sympy.__version__ == '1.14.0' and mpmath.__version__ == '1.3.0', 'exact symbolic dependency versions required')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'); env.pop('PYTHONOPTIMIZE', None)
    def run(name, command):
        with (work / (name + '.log')).open('w', encoding='utf8', newline='\n') as log:
            r = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        need(r.returncode == 0, 'failed ' + name + '; retained scoped log'); print('PASS', name, flush=True)
    receipt = read(inputs / 'NATIVE-RECEIPT.json'); cache = inputs / 'native-cache'; borrow = source / 'new/borrow'
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        word = borrow / 'words' / ('BORROW-WORD-43' + tag + '.json.gz'); native = work / ('native-' + tag)
        run('native-' + tag, [sys.executable, '-B', str(source / 'new/fastnative/run_native.py'), str(word), str(native)])
        nr = read(native / 'RESULT.json'); need(nr['source_sha256'] == tree(source / 'new/fastnative/vendor'), 'complete native scientific source closure')
        need(nr['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY' and nr['word_sha256'] == sha(word), 'exact fresh native word binding')
        need([z['step'] for z in nr['steps']] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(z['exit_code'] == 0 for z in nr['steps']), 'five-stage native coverage')
        need(read(native / 'native/local/FULL-WORD.json.gz') == read(word), 'native complete word equality')
        entry = cache / sha(word); need(not entry.exists(), 'fresh changed native cache entry'); shutil.copytree(native / 'native', entry)
        write(entry / 'CACHE.json', {'word_sha256': sha(word), 'files': tree(entry)})
        receipt['providers'][tag] = {'word_sha256': sha(word), 'complete_native_files': tree(entry, ('CACHE.json',))}
        canonical = read(entry / 'local/CANONICAL-WORD.json.gz')
        widths = [len(canonical['frames'][canonical['final'][r]]) - len(canonical['frames'][canonical['start'][r]]) for r in range(224, 632)]
        need(widths == registry[pid]['widths'] and read(entry / 'local/LOCAL-CHECKS.json')['forward']['paid_profile'] == registry[pid]['actual_paid_profile'], 'native metadata equality')
    receipt.update(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE', source_commit=COMMIT, manifest_sha256=manifest, cache_files=tree(cache))
    write(work / 'NATIVE-RECEIPT.json', receipt)
    arguments = {'source': source, 'fill': PACKAGE / 'owner/FILL.json.gz', 'order': PACKAGE / 'owner/inputs/ORDER.json', 'dispatch': PACKAGE / 'owner/inputs/DISPATCH.json',
                 'native-cache': cache, 'native-receipt': work / 'NATIVE-RECEIPT.json', 'work': work / 'admission', 'replica-helper-dir': inputs / 'helpers',
                 'reconstructor': inputs / 'helpers/reconstruct_replica.py', 'comparison-claim': PR3945 / 'PR3682-CLAIM.json', 'blocknorm-checker': inputs / 'extension_blocknorm.py'}
    command = [sys.executable, '-B', str(work / 'admit_staged.py')]
    for k, v in arguments.items(): command += ['--' + k, str(v)]
    command += ['--source-profile', 'staged544', '--comparison-profile', 'pr3682', '--jobs', str(a.jobs)]
    run('complete-admission', command)
    result = read(work / 'admission/RESULT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete release status')
    need(result['profile'] == read(PACKAGE / 'owner/PROFILE.json'), 'exact complete paid profile')
    expected = Q(read(PACKAGE / 'RESULT.json')['conditional_kappa'])
    need(Q(result['kappa']) == expected, 'exact new complete headline')
    write(work / 'RESULT.json', {'status': 'PASS_STAGED_ENTRIES_COMPLETE_CONDITIONAL_RELEASE', 'kappa': str(expected), 'source_manifest_sha256': manifest,
                                 'retained_ancestry_reused': True, 'new_native_fresh': True, 'release_receipt_sha256': sha(work / 'admission/release/RELEASE-RECEIPT.json')})
    print('PASS_STAGED_ENTRIES_COMPLETE_CONDITIONAL_RELEASE', flush=True)


if __name__ == '__main__':
    main()
