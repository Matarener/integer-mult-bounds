"""Bound the four regenerated provenance differences against PR3605's inventory.

Collection reads the actual large PLAN. The bounded checker cannot authenticate
that omitted file; it directly restores the other three retained JSON files.
roger-sato, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
import math

BINDING_SHA = '9b76c0d007a43dee2d3dd24da4e99e7700544ece87eef70ad34caab06502481a'
NORMALIZER_SHA = 'c8af22719c0f3097a991a3f6ccac8f090afd2faba554745733d9ea88f2c25708'
WORDS = {'gauge44':'735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653',
         'extra':'886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f'}
PATHS = ['new/PLAN.json', 'new/SPEC.json', 'outer/INDEPENDENT.json', 'outer/LEDGER.json']
ROOT = 'runtime/candidate/package/'


def need(value, message):
    if not value:
        raise ValueError('historical comparison: ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def restored_digest(lines, replacements):
    digest = hashlib.sha256()
    counts = {new:0 for new in replacements}
    for line in lines:
        for new, old in replacements.items():
            counts[new] += line.count(new.encode())
            line = line.replace(new.encode(), old.encode())
        digest.update(line)
    need(all(n == 1 for n in counts.values()), 'each replacement occurs exactly once')
    return digest.hexdigest()


def specification(files):
    binding = files['original/FINAL-BINDING.json']
    need(sha(binding) == BINDING_SHA, 'original public inventory')
    original = json.loads(binding)['source_sha256']
    prefix = 'staged-pair-release/candidate/package/'
    old = {path[len(prefix):]:value for path,value in original.items() if path.startswith(prefix)}
    current = json.loads(files[ROOT+'MANIFEST.json'])
    need(set(old) == set(current) | {'MANIFEST.json'}, 'complete historical package inventory')
    need({path for path,value in current.items() if old[path] != value} == set(PATHS),
         'exactly four generated JSON differences')
    need(len(current) == 652, '652 generated files')
    module = 'code/generated_identity.py'
    need(sha(files[ROOT+module]) == old[module] == current[module] == NORMALIZER_SHA,
         'original normalization implementation')
    spec = json.loads(files[ROOT+'new/SPEC.json'])
    phases = []
    plan_replacements = {}
    for tag, word in WORDS.items():
        prefix = 'runtime/native/native-cache/' + word + '/local/'
        historical = 'staged-pair-release/native/native-cache/' + word + '/local/'
        phase = files[prefix+'CLIFFORD-REVIEW.json']
        value = json.loads(phase)
        new_phase, old_phase = sha(phase), original[historical+'CLIFFORD-REVIEW.json']
        need(new_phase != old_phase, 'changed phase raw identity')
        plan_replacements[new_phase] = old_phase
        for field,name in [('canonical_word_sha256','CANONICAL-WORD.json.gz'),
                           ('recipe_sha256','CLIFFORD-RECIPES.json')]:
            need(value[field] == sha(files[prefix+name]) == original[historical+name],
                 'unchanged phase referenced bytes')
        seconds = value.pop('seconds')
        need(type(seconds) in (int,float) and math.isfinite(seconds) and seconds >= 0,
             'finite nonnegative phase timing')
        value['canonical_word_sha256'] = sha(gzip.decompress(files[prefix+'CANONICAL-WORD.json.gz']))
        value['recipe_sha256'] = sha(canonical(json.loads(files[prefix+'CLIFFORD-RECIPES.json'])))
        semantic = sha(canonical(value))
        need(semantic == spec['providers'][tag]['semantic_phase_sha256'], 'unchanged semantic phase')
        phases.append({'provider':tag, 'historical_raw_sha256':old_phase,
                       'current_raw_sha256':new_phase, 'unchanged_semantic_sha256':semantic})
    replacements = {'new/PLAN.json':plan_replacements,
        'new/SPEC.json':{current['new/PLAN.json']:old['new/PLAN.json']},
        'outer/INDEPENDENT.json':{current['new/SPEC.json']:old['new/SPEC.json']},
        'outer/LEDGER.json':{current['new/SPEC.json']:old['new/SPEC.json']}}
    return old, current, phases, replacements


def collect_delta(files, package):
    old, current, phases, replacements = specification(files)
    checks = []
    for path, changes in replacements.items():
        with (package/path).open('rb') as stream:
            need(hashlib.file_digest(stream, 'sha256').hexdigest() == current[path], 'actual current bytes')
        with (package/path).open('rb') as stream:
            restored = restored_digest(stream, changes)
        need(restored == old[path], 'actual historical JSON reconstruction: ' + path)
        checks.append({'path':path, 'current_sha256':current[path],
            'historical_sha256':old[path], 'restored_sha256':restored, 'replacements':changes})
    return {'status':'PASS_EXACT_HISTORICAL_GENERATED_JSON_DELTA',
        'historical_binding_sha256':BINDING_SHA, 'historical_package_manifest_sha256':old['MANIFEST.json'],
        'current_package_manifest_sha256':sha(files[ROOT+'MANIFEST.json']),
        'same_file_count':648, 'changed_file_count':4, 'phase_changes':phases,
        'reconstruction':checks, 'normalization_module_sha256':NORMALIZER_SHA,
        'scope':'Collector reconstructed all four historical hashes from actual run bytes. '
                'Bounded checker directly reconstructs three retained JSONs; PLAN is omitted.'}


def check_delta(files):
    old, current, phases, replacements = specification(files)
    report = json.loads(files['HISTORICAL-COMPARISON.json'])
    need(report['status'] == 'PASS_EXACT_HISTORICAL_GENERATED_JSON_DELTA'
         and report['historical_binding_sha256'] == BINDING_SHA
         and report['historical_package_manifest_sha256'] == old['MANIFEST.json']
         and report['current_package_manifest_sha256'] == sha(files[ROOT+'MANIFEST.json'])
         and report['normalization_module_sha256'] == NORMALIZER_SHA
         and report['same_file_count'] == 648 and report['changed_file_count'] == 4
         and report['phase_changes'] == phases, 'recorded comparison identities')
    expected = []
    for path, changes in replacements.items():
        if path != 'new/PLAN.json':
            data = files[ROOT+path]
            need(sha(data) == current[path], 'retained generated bytes')
            need(restored_digest(data.splitlines(keepends=True), changes) == old[path],
                 'retained historical JSON reconstruction: ' + path)
        expected.append({'path':path, 'current_sha256':current[path],
            'historical_sha256':old[path], 'restored_sha256':old[path], 'replacements':changes})
    need(report['reconstruction'] == expected, 'exact recorded replacement edges')
