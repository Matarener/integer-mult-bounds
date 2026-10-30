#!/usr/bin/env python3
"""Read-only signed complex birth replay; write only the requested fresh receipt."""
from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from commute_birth import ROOT, HERE, OLD, F, O, canonical, trace
from exact_rows import replay, expected, repair
from prefix_birth_search import early_schedule


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output
    assert output.is_absolute() and not output.exists(), 'output must be a fresh absolute file'
    output = output.resolve()
    assert not output.is_relative_to(HERE), 'review writes outside the frozen scope'
    pins = {}
    searches = {}
    for name in ('base', 'prefix-early-base', 'writer-all-base', 'observer-all-base'):
        path = HERE / name / 'RESULT.json'
        data = json.loads(path.read_text())
        assert data['new_kappa'] is False and not data['positives']
        for relative, expected_hash in data['source_sha256'].items():
            assert digest(ROOT / relative) == expected_hash, relative
            pins[relative] = expected_hash
        cases = data.get('cases', data.get('candidates', []))
        for case in cases:
            assert case.get('optimized_saving', case.get('saving', 0)) <= 1e-10
            assert not case.get('optimized_delta', case.get('delta', {}))
        pins[str(path.relative_to(ROOT))] = digest(path)
        searches[name] = {'stats': data['stats'], 'positive_candidates': 0,
                          'helpers': [case['helper'] for case in cases]}
    assert searches['base']['stats'] == {'commutable_first_contacts': 204, 'joint_frames_solved': 204}
    assert searches['writer-all-base']['stats']['SOURCE_prefix_rebuilt'] == 25
    assert searches['observer-all-base']['stats']['SOURCE_prefix_rebuilt'] == 7
    assert set(searches['prefix-early-base']['helpers']).issubset(searches['writer-all-base']['helpers'])
    variants = {}
    for variant in ('base', 'extra'):
        source = OLD / f'candidate/BORROW-WORD-43{variant}.json.gz'
        word = F.read(source)
        assert replay(word)[0] == expected(word)
        baseline, _ = trace(word)
        assert dict(baseline) == {1: 2439, 2: 724, 3: 225, 4: 102, 5: 20, 8: 8}
        scheduled, births = early_schedule(word)
        correction = repair(scheduled)
        scheduled, optimization = O.optimize(scheduled)
        assert len(births) == 19 and correction['new_initial_corrections'] == 0
        assert replay(scheduled)[0] == expected(scheduled)
        assert trace(scheduled)[0] == baseline
        assert scheduled['start_extra'] == word['start_extra']
        assert scheduled['helper_final'] == word['helper_final']
        assert scheduled['removed'] == word['removed']
        if variant == 'base':
            for name in ('prefix-early-base', 'writer-all-base', 'observer-all-base'):
                stored = HERE / name / 'SCHEDULED.json.gz'
                assert canonical(F.read(stored)) == canonical(scheduled)
                pins[str(stored.relative_to(ROOT))] = digest(stored)
        variants[variant] = {'source_sha256': digest(source), 'independent_live_inputs': 632,
                             'private_zero_buffers': 91, 'early_births': 19,
                             'profile': dict(baseline), 'rank_mass': sum(r*c for r,c in baseline.items()),
                             'schedule_payload_sha256': sha256(canonical(scheduled)).hexdigest(),
                             'new_initial_corrections': 0, 'exact_free_operator_identity': True,
                             'joint_frame_delta': optimization['delta']}
        pins[str(source.relative_to(ROOT))] = digest(source)
    word = F.read(OLD / 'candidate/BORROW-WORD-43base.json.gz')
    positive = deepcopy(word)
    positive['initial_corrections'].append({'target': 112, 'source': 224,
                                          'operator_word': [], 'coefficient': '1'})
    assert repair(positive)['new_initial_corrections'] == 1
    assert replay(positive)[0] == expected(positive)
    protected = deepcopy(word)
    protected['initial_corrections'].append({'target': 112, 'source': 0,
                                           'operator_word': [], 'coefficient': '1'})
    try:
        repair(protected)
    except ValueError as exc:
        assert exc.args[0][0] == 'protected_input_changed'
    else:
        raise AssertionError('protected SOURCE error was incorrectly admitted')
    changed_output = deepcopy(word)
    changed_output['precondition'].append(['scale', 0, 2, 1, []])
    try:
        repair(changed_output)
    except ValueError as exc:
        assert exc.args[0][0] == 'non_TARGET_output_changed'
    else:
        raise AssertionError('non-TARGET output error was incorrectly admitted')
    for name in ('review.py', 'README.md', 'TASK.json'):
        path = HERE / name
        pins[str(path.relative_to(ROOT))] = digest(path)
    result = {'status': 'PASS_SCOPED_COMPLEX_BIRTH_REVIEW', 'variants': variants,
              'searches': searches, 'search_receipts_source_hash_checked': True,
              'search_optimizations_rerun_by_this_review': False,
              'dirty_correction_controls': {'allowed_helper_corrected': True,
                                            'protected_SOURCE_rejected': True,
                                            'non_TARGET_output_rejected': True},
              'source_sha256': dict(sorted(pins.items())), 'new_kappa': False,
              'native_candidate_admitted': False,
              'scope': 'Fresh exact signed free-warp replay of both retained suppliers and their neutral early-birth schedules; '
                       'full input identity and private-buffer restoration, with source-bound finite search receipts. '
                       'This is not a new native physical caller, a full search rerun, or a universal complex-word obstruction.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'output': str(output), 'new_kappa': False}))


if __name__ == '__main__':
    main()
