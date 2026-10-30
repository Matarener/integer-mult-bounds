#!/usr/bin/env python3
"""Bounded follow-up review of the unseeded canonical-output replay fix.

Only the actual copy loop and absence/subset guards execute, against an
in-memory filesystem. No scientific subprocess or real clone is started.
The earlier reviews and all scientific sources remain unchanged.
"""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
LATE = SCOPE / 'late-staged-composition'
OLD = '64786bee1c5c56328ca09c98bd9828af92732a373d49bb95ef56e2d514c60a6c'
NEW = '4b0208d6359227b109fe035b4a893ffda6c5c4994d174dac6e1296d94c298250'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    driver = SCOPE / 'replay_latest.py'
    body = driver.read_text()
    need(sha(driver) == NEW, 'Exact corrected driver')
    old_review = json.loads((HERE / 'LATEST-REVIEW.json').read_text())
    key = driver.relative_to(REPO).as_posix()
    need(old_review['reviewed_files'][key] == OLD, 'Exact earlier independent review')
    for rel, digest in old_review['reviewed_files'].items():
        if rel != key:
            need(sha(REPO / rel) == digest, 'Every other final selection review pin unchanged')
    patches = [
        ("    clone.mkdir(parents=True)\n    for p in paths:\n",
         "    clone.mkdir(parents=True)\n    regenerated = {\n"
         "        LATE / 'candidate/BORROW-WORD-43base.json.gz',\n"
         "        LATE / 'candidate/BORROW-WORD-43extra.json.gz',\n"
         "        LATE / 'candidate/CONSTRUCTION.json',\n"
         "        LATE / 'invoice/RESULT.json',\n"
         "        LATE / 'T360-OPERATOR-ADMISSION.json',\n"
         "        LATE / 'CLAIM.json',\n"
         "    }\n"
         "    need(regenerated.issubset(set(paths)), 'Every regenerated output has authenticated expected evidence')\n"
         "    for p in paths:\n"
         "        # Never seed then delete an expected output: a synchronized filesystem\n"
         "        # can restore the seeded version while the fresh computation runs.\n"
         "        # Expected bytes remain in the authenticated caller tree for comparison.\n"
         "        if p in regenerated:\n"
         "            continue\n"),
        ("    shutil.rmtree(selected / 'candidate')\n",
         "    need(not (selected / 'candidate').exists(), 'Unseeded fresh canonical candidate directory')\n"),
        ("    shutil.rmtree(selected / 'invoice')\n    (selected / 'T360-OPERATOR-ADMISSION.json').unlink()\n",
         "    need(not (selected / 'invoice').exists(), 'Unseeded fresh canonical invoice directory')\n"
         "    need(not (selected / 'T360-OPERATOR-ADMISSION.json').exists(), 'Unseeded fresh operator output')\n"),
        ("    (selected / 'CLAIM.json').unlink()\n",
         "    need(not (selected / 'CLAIM.json').exists(), 'Unseeded fresh claim output')\n"),
    ]
    restored = body
    for old, new in patches:
        need(restored.count(new) == 1, 'Unique complete driver patch')
        restored = restored.replace(new, old)
    need(hashlib.sha256(restored.encode()).hexdigest() == OLD, 'Only the four reviewed source edits differ')
    main_node = next(x for x in ast.parse(body).body if isinstance(x, ast.FunctionDef) and x.name == 'main')
    index = next(i for i, x in enumerate(main_node.body)
                 if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'regenerated' for t in x.targets))
    assignment, subset_guard, copy_loop = main_node.body[index:index + 3]
    need(isinstance(copy_loop, ast.For), 'Actual guarded clone copy loop')
    guards = [x for x in main_node.body if isinstance(x, ast.Expr) and isinstance(x.value, ast.Call)
              and isinstance(x.value.func, ast.Name) and x.value.func.id == 'need'
              and len(x.value.args) > 1 and isinstance(x.value.args[1], ast.Constant)
              and str(x.value.args[1].value).startswith('Unseeded fresh')]
    need(len(guards) == 4, 'All four actual absence guards')

    # Execute the actual clone loop with virtual paths and byte identities.
    # This probes the reported seed/delete failure without filesystem writes
    # or repeated native, owner, invoice, or release computations.
    files, directories, copied = {}, set(), []
    class VirtualPath:
        def __init__(self, path):
            self.path = PurePosixPath(path.path if isinstance(path, VirtualPath) else path)
        def __hash__(self): return hash(self.path)
        def __eq__(self, other): return isinstance(other, VirtualPath) and self.path == other.path
        def __truediv__(self, other): return VirtualPath(self.path / other)
        @property
        def parent(self): return VirtualPath(self.path.parent)
        def relative_to(self, other): return self.path.relative_to(other.path)
        def mkdir(self, **kwargs): directories.add(self.path)
        def exists(self):
            return self.path in directories or self.path in files or any(p.is_relative_to(self.path) for p in files)
    def copyfile(source, destination):
        need(destination.path not in files, 'No previously seeded destination')
        files[destination.path] = files[source.path]
        copied.append(destination.path)
    def virtual_sha(path): return files[path.path]
    manifest = json.loads((SCOPE / 'MANIFEST.json').read_text())
    inputs = []
    for base, field in ((SCOPE, 'files'), (REPO, 'repository_dependencies')):
        for rel, record in manifest[field].items():
            path = base / rel
            inputs.append(VirtualPath(path.as_posix()))
            files[PurePosixPath(path.as_posix())] = record['sha256']
    env = dict(LATE=VirtualPath(LATE.as_posix()), REPO=VirtualPath(REPO.as_posix()),
               clone=VirtualPath('/fresh-owned-clone/integer-mult-bounds'), paths=inputs,
               shutil=SimpleNamespace(copyfile=copyfile), need=need, sha=virtual_sha)
    def execute(nodes):
        module = ast.Module(body=nodes, type_ignores=[])
        ast.fix_missing_locations(module)
        exec(compile(module, str(driver), 'exec'), env)
    execute([assignment, subset_guard, copy_loop])
    regenerated = env['regenerated']
    need(len(regenerated) == 6 and len(copied) == len(inputs) - 6, 'Exactly six authenticated outputs skipped')
    expected = {p.path for p in regenerated}
    groups = {p.path for p in inputs if p.path.is_relative_to(PurePosixPath((LATE / 'candidate').as_posix()))
              or p.path.is_relative_to(PurePosixPath((LATE / 'invoice').as_posix()))
              or p.path in {PurePosixPath((LATE / 'T360-OPERATOR-ADMISSION.json').as_posix()),
                           PurePosixPath((LATE / 'CLAIM.json').as_posix())}}
    need(groups == expected, 'No additional current canonical output can seed either directory')
    env['selected'] = env['clone'] / LATE.relative_to(REPO).as_posix()
    execute(guards)
    controls = []
    baseline_files = dict(files)
    for missing in sorted(regenerated, key=lambda p: str(p.path)):
        env['paths'] = [p for p in inputs if p != missing]
        try:
            execute([subset_guard])
        except ValueError as exc:
            need(str(exc) == 'Every regenerated output has authenticated expected evidence', 'Exact missing-input rejection')
        else:
            raise ValueError('Missing immutable expected output accepted')
        controls.append(dict(kind='missing_authenticated_expected_output', path=str(missing.path.relative_to(REPO)), accepted=False))
    env['paths'] = inputs
    for injected in sorted(regenerated, key=lambda p: str(p.path)):
        files.clear(); files.update(baseline_files)
        destination = env['clone'] / injected.relative_to(env['REPO'])
        files[destination.path] = 'unexpected-existing-output'
        try:
            execute(guards)
        except ValueError as exc:
            need(str(exc).startswith('Unseeded fresh'), 'Exact existing-output rejection')
        else:
            raise ValueError('Preseeded output accepted')
        controls.append(dict(kind='unexpected_existing_clone_output', path=str(injected.path.relative_to(REPO)), accepted=False))
    pins = {p.relative_to(REPO).as_posix(): sha(p) for p in [driver, Path(__file__), HERE / 'LATEST-REVIEW.json',
            HERE / 'PRIMARY-REVIEW.json', LATE / 'RELEASE-STATIC-REVIEW.json']}
    # These six immutable comparison targets are individually authenticated
    # even while the enclosing manifest awaits the driver's new byte pin.
    expected_pins = {}
    for path in sorted(expected):
        actual = Path(path)
        need(sha(actual) == baseline_files[path], 'Immutable expected bytes unchanged')
        expected_pins[actual.relative_to(REPO).as_posix()] = sha(actual)
    result = dict(status='PASS_SCOPED_REPLAY_DIRECTORY_CREATION_REVIEW', acceptance_defects_found=False,
                  reviewed_files=pins, immutable_expected_outputs=expected_pins,
                  supersedes_only=dict(review='packaging-review/LATEST-REVIEW.json', field='reviewed_files.' + key,
                                       previous_sha256=OLD, corrected_sha256=NEW),
                  exact_source_edits=len(patches), virtual_copy_inputs=len(inputs), virtual_copies=len(copied),
                  skipped_authenticated_outputs=6, absence_guards=4, rejecting_controls=controls,
                  findings=[
                      'The driver authenticates every expected output before cloning and explicitly requires all six to appear in the manifest.',
                      'The actual clone copy loop never writes the three candidate files, the invoice result, operator receipt, or claim. Neither canonical output directory is initially created by any other current manifest member.',
                      'All four former deletion points now require absence. Unexpected outputs reject instead of being deleted and later restored by synchronization.',
                      'Comparison targets remain the authenticated original extracted tree. The candidate restore after complete canonical payload and constructor equality is unchanged and performs no deletion.',
                      'Byte-exact reversal of these four edits recovers the previously reviewed driver hash. Scientific scripts, receipt comparators, native/full guards, all12 default stages, all17 default comparisons, and claim selection are unchanged.',
                  ],
                  prior_reviews_modified=False, scientific_sources_modified=False,
                  limitations=['This is a source-delta and in-memory copier review. It does not claim that a background synchronization service was reproduced or that the corrected heavy replay completed.',
                               'Root must refreeze the manifest and run the corrected extracted replay before final package acceptance. Earlier transport/native portability limits remain unchanged.'])
    (HERE / 'REPLAY-DIRECTORY-REVIEW.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], len(inputs), 'virtual inputs', len(controls), 'rejections', flush=True)


if __name__ == '__main__':
    main()
