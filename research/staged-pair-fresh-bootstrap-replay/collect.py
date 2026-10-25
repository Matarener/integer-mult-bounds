#!/usr/bin/env python3
"""Collect a completed original PR3605 run; never execute or repair its solvers.

The output is a compact transcript. Large source/cache/owner files are hashed
locally and omitted; verifying this transcript alone does not replay them.
roger-sato, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import io
import hashlib
import json
from pathlib import Path
import tarfile

from verify import B, C, HEAD, PARENT, R, check, log_name, need, obj, sha
from historical import WORDS, collect_delta


def tree(root, exclude=()):
    files = {}
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'symlink in authenticated tree: ' + str(path))
        if path.is_file() and path.relative_to(root).as_posix() not in exclude:
            with path.open('rb') as stream:
                files[path.relative_to(root).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return files


def collect(source, work, attempt):
    files = {}
    def add(name, path):
        need(path.is_file() and not path.is_symlink(), 'missing regular artifact: ' + str(path))
        files[name] = path.read_bytes()
    def runtime(path):
        add(R + path, work/path)
    for name in ('RUN.json', 'source-before.json', 'source-after.json', 'stdout.log', 'stderr.log'):
        add('attempt/' + name, attempt/name)
    if (attempt.parent/'run_full_replay.py').is_file():
        add('attempt/record_run.py', attempt.parent/'run_full_replay.py')
    add('original/LICENSE', source/'LICENSE')
    before = obj(files, 'attempt/source-before.json')
    need(before['head'] == HEAD, 'wrong original source head')
    for path, pin in before['files'].items():
        need(sha((source/path).read_bytes()) == pin['sha256'], 'current proof input changed: ' + path)
    for name in ('reproduce.py', 'CLAIM.json', 'FETCH.txt', 'STAGE-SCOPE.json', 'owners/SOURCE-NOTICE', 'owners/SOURCE-CREDITS.md',
                 'vendor/pr3531/vendor/PR3361-NOTICE', 'evidence/FINAL-BINDING.json'):
        path = source/'research/staged-644-660-conditional-release'/name
        if path.is_file():
            add('original/' + name.removeprefix('evidence/'), path)
    directories = ['', 'source-stages/retained/', 'source-stages/retained/retained-parent/',
                   'native/', 'candidate/', 'candidate/release/verify/', 'independent/']
    source_scripts = {pin['sha256']:source/path for path,pin in before['files'].items()
                      if path.endswith('.py')}
    for directory in directories:
        runtime(directory + 'STAGES.json')
        runtime(directory + 'RESULT.json')
        for row in obj(files, R + directory + 'STAGES.json'):
            name = row.get('name', row.get('stage'))
            if 'log_sha256' in row:
                runtime(directory + log_name(name))
                need(sha(files[R + directory + log_name(name)]) == row['log_sha256'], 'changed stage log')
            if 'script_sha256' in row:
                digest = row['script_sha256']
                candidates = [Path(arg) for arg in row.get('command', []) if arg.endswith('.py')]
                candidates += [source_scripts[digest]] if digest in source_scripts else []
                matching = [p for p in candidates if p.is_file() and sha(p.read_bytes()) == digest]
                need(matching, 'missing exact stage script: ' + name)
                add('scripts/' + digest + '.py', matching[0])
    for path in ('source/MANIFEST.json', 'pr3133/MANIFEST.json',
                 'source-stages/pr2833/MANIFEST.json',
                 'source-stages/pr2833/vendor/pr1297/MANIFEST.json',
                 'source-stages/pr2833/vendor/pr1297/CLAIM.json',
                 'source-stages/retained/NATIVE-RECEIPT.json',
                 'source-stages/retained/ENVIRONMENT.json', 'native/ENVIRONMENT.json', 'native/NATIVE-RECEIPT.json',
                 'candidate/release/RELEASE-RECEIPT.json', 'candidate/package/MANIFEST.json',
                 'candidate/package/SPEC.json', 'candidate/package/new/SPEC.json',
                 'candidate/discovery/global/audit/ASYNC-AUDIT.json',
                 'independent/INDEPENDENT-OWNERS.json', 'independent/arithmetic/RESULT.json',
                 'independent/literal/PROFILE.json', 'candidate/package/outer/INDEPENDENT.json',
                 'candidate/package/outer/LEDGER.json', 'candidate/package/code/generated_identity.py'):
        runtime(path)
    parent_prefix = 'source-stages/retained/native-cache/_receipts/' + PARENT + '/'
    for name in ('RESULT.json', 'STAGES.json', 'RECEIPT.json'):
        runtime(parent_prefix + name)
    boot = obj(files, B + 'NATIVE-RECEIPT.json')
    final = obj(files, R + 'native/NATIVE-RECEIPT.json')
    parent = obj(files, R + parent_prefix + 'RECEIPT.json')
    for directory, receipt in (('source-stages/retained/', boot), ('native/', final)):
        cache = work/directory/'native-cache'
        need(tree(cache) == receipt['cache_files'], 'complete native cache drift: ' + directory)
        words = {p['word_sha256'] for p in receipt['providers'].values()} | set(parent['words'].values())
        word_sources = {sha(path.read_bytes()):path for path in
            [(work/('source-stages/pr2833' if directory.startswith('source-stages/') else 'source')
              /'new/borrow/words'/('BORROW-WORD-43'+tag+'.json.gz')) for tag in ('base','extra')]
            + [work/'source-stages/pr2833/vendor/pr1297'/name
               for name in ('gauge44-word.json.gz','extra-word.json.gz')]}
        need(set(word_sources) == words, 'native words not bound to authenticated source')
        for word in words:
            need(json.loads(gzip.decompress((cache/word/'local/FULL-WORD.json.gz').read_bytes()))
                 == json.loads(gzip.decompress(word_sources[word].read_bytes())),
                 'native full-word payload differs from source')
            runtime(directory + 'native-cache/' + word + '/STEPS.json')
            runtime(directory + 'native-cache/' + word + '/CACHE.json')
            for log in sorted((cache/word).glob('*.log')):
                runtime(log.relative_to(work).as_posix())
        for tag in ('base','extra'):
            fast = work/directory/(('fast-' if directory.startswith('source-stages/') else 'fresh-') + tag)
            # Both native preparers preserve the sparse driver's six command logs.
            for name in ('RESULT.json', 'COMMANDS.json'):
                runtime((fast/name).relative_to(work).as_posix())
            for log in sorted(fast.glob('*.log')):
                runtime(log.relative_to(work).as_posix())
    for word in WORDS.values():
        for name in ('CLIFFORD-REVIEW.json', 'CANONICAL-WORD.json.gz', 'CLIFFORD-RECIPES.json'):
            runtime('native/native-cache/' + word + '/local/' + name)
    files['HISTORICAL-COMPARISON.json'] = (json.dumps(collect_delta(files, work/'candidate/package'),
        indent=2, sort_keys=True)+'\n').encode()
    collection = {
        'predecessor':tree(work/'pr3133', ('MANIFEST.json',)),
        'source648':tree(work/'source', ('MANIFEST.json',)),
        'bootstrap541':tree(work/'source-stages/pr2833', ('MANIFEST.json',)),
        'generated_package':tree(work/'candidate/package', ('MANIFEST.json',)),
        'bootstrap_cache':tree(work/'source-stages/retained/native-cache'),
        'final_cache':tree(work/'native/native-cache'),
        'boundary':'Locally checked every listed file byte. Large inputs/outputs are not copied into this transcript.'}
    for key, path in (('predecessor','pr3133/MANIFEST.json'), ('source648','source/MANIFEST.json'),
                      ('bootstrap541','source-stages/pr2833/MANIFEST.json'),
                      ('generated_package','candidate/package/MANIFEST.json')):
        need(collection[key] == obj(files, R + path), 'complete source tree drift: ' + key)
    files['COLLECTION.json'] = (json.dumps(collection,indent=2,sort_keys=True)+'\n').encode()
    check(files)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'work', 'attempt', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'fresh collection output required')
    files = collect(args.source.resolve(), args.work.resolve(), args.attempt.resolve())
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        for name, data in sorted(files.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode, member.mtime = len(data), 0o644, 0
            archive.addfile(member, io.BytesIO(data))
    data = gzip.compress(stream.getvalue(), mtime=0)
    args.out.mkdir(parents=True)
    (args.out/'evidence.tar.gz').write_bytes(data)
    expected = {'archive_sha256':sha(data), 'members':{name:sha(data) for name,data in sorted(files.items())}}
    (args.out/'EXPECTED.json').write_text(json.dumps(expected,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'members':len(files),'archive_bytes':len(data),'archive_sha256':sha(data)}))


if __name__ == '__main__':
    main()
