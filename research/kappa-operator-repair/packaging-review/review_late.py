#!/usr/bin/env python3
"""Source-bound independent static review of the late release conjunction.

The small executed checks authenticate sources, reconstruct the literal claim
adaptation, classify physical event windows, and reject incomplete claim
fixtures. They do not execute a native provider, the full invoice, or a full
conditional release. All reviewed scientific sources are read-only.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
REPO = SCOPE.parents[1]
LATE = SCOPE / 'late-staged-composition'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def literal_adaptations():
    receipt = read(LATE / 'CLAIM-ADAPTATION.json')
    details = {}
    for name, record in receipt['sources'].items():
        parent = REPO / record['parent']
        need(sha(parent) == record['parent_sha256'], 'Exact frozen parent ' + name)
        body = parent.read_text()
        for change in record['literal_changes']:
            need(body.count(change['old']) == change['occurrences'], 'Exact adaptation preimage ' + name)
            body = body.replace(change['old'], change['new'])
        need(body.encode() == (LATE / name).read_bytes(), 'Complete literal adaptation ' + name)
        need(sha(LATE / name) == record['derived_sha256'], 'Adaptation output hash ' + name)
        details[name] = dict(parent_sha256=record['parent_sha256'], derived_sha256=record['derived_sha256'],
                             changes=len(record['literal_changes']))
    return details


def incomplete_claim_controls(invoice, operator):
    # Execute the reviewed validate function alone. The fixtures deliberately
    # omit completed runtime evidence, and every expected failure is checked
    # by its exact message rather than an incidental missing field.
    tree = ast.parse((LATE / 'build_claim.py').read_text())
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'validate')
    isolated = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(isolated)
    env = dict(Q=Q, need=need, LOWER=Q('.001730970419199163702738'),
               UPPER=Q('.001730970419199163702739'), BIT=Q('.001738137188329345368427'),
               OUTER_LOSS=Q(1, 10**46) + Q(1, 10**70))
    exec(compile(isolated, str(LATE / 'build_claim.py'), 'exec'), env)
    baseline = dict(invoice=invoice, operator=operator,
                    runner=dict(profile=invoice['profile'], status='PREPARED_NOT_ADMITTED'),
                    admission=dict(profile=invoice['profile']))
    controls = []
    cases = [
        ('missing_operator', lambda r: r.update(operator=None), 'Missing required full operator gate'),
        ('finite_only_operator', lambda r: r['operator'].update(all_positive_tensor_multiplicities=False),
         'Positive operator admission must cover all characters and tensor multiplicities'),
        ('axis_overlay', lambda r: r['operator'].update(no_axis_transfer_overlay=False),
         'Current supplier cannot silently retain MOVES'),
        ('source_preflight_is_not_release', lambda r: r['runner'].update(status='PASS_ALL_THREE_WORD_REVIEWS_SOURCE_READY_NOT_ADMITTED'),
         'Complete new release execution'),
        ('primary_release_is_not_late_release', lambda r: r['runner'].update(status='PASS_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE'),
         'Complete new release execution'),
    ]
    for name, change, expected in cases:
        records = deepcopy(baseline)
        change(records)
        try:
            env['validate'](records)
        except ValueError as exc:
            need(str(exc) == expected, 'Expected rejection reason ' + name)
        else:
            raise ValueError('Incomplete claim accepted: ' + name)
        controls.append(dict(name=name, accepted=False, reason=expected))
    return controls


def event_windows():
    owner = SCOPE / 'sources/PR4076/research/staged544-triple-entry-fill/owner'
    template = read(owner / 'inputs/TEMPLATE.json.gz')
    order = read(owner / 'inputs/ORDER.json')
    plan = read(owner / 'inputs/PLAN.json.gz')
    pairs = {x['stage']: x['pair'] for x in template['recipe'] if x['kind'] == 'local'}
    clock = {tuple(sr): tick for tick, sr in enumerate(order)}
    need(len(order) == len(clock) == 3240, 'Complete clock')
    need(set(clock) == {(s, r) for s in range(9) for r in range(360)}, 'Every stage/replica')
    # Rebuild timestamped observations directly from the execution schedule.
    # No imported invoice or t360_admission.blocks/touches routine is used.
    windows = []
    for replica in range(360):
        last = [(-1, -1)] * 8
        current_stage, index = None, None
        for event in template['execution_schedule']:
            kind = event['kind']
            if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
                continue
            if kind == 'local_cover_sweep':
                current_stage, index = event['stage'], 0
            else:
                need(current_stage is not None, 'An observation belongs to a local block')
                index += 1
            position = (clock[current_stage, replica], index)
            if kind == 'idle_cover_sweep':
                for side, child in enumerate(event['child_indices']):
                    stream = 2 * event['pair'] + side
                    routed = str(child) in plan['pairs']
                    if routed:
                        need(stream == 2 * plan['pairs'][str(child)] + plan['sides'][str(child)], 'Exact child stream')
                    windows.append((replica, child, stream, last[stream], position, routed))
                observers = ()
            elif kind == 'local_cover_sweep':
                pair = pairs[current_stage]
                observers = (2 * pair, 2 * pair + 1)
            elif kind == 'bridge':
                observers = tuple(2 * pair + side for pair in (event['src'], event['dst']) for side in (0, 1))
            elif kind == 'terminal':
                observers = tuple(range(8))
            else:
                need(kind == 'terminal_Y_translations', 'Known phase-only event')
                observers = ()
            for stream in observers:
                last[stream] = position
    need(len(windows) == 7200 and len({(r, c) for r, c, *_ in windows}) == 7200, 'Every physical child exactly once')
    shared = defaultdict(list)
    nonempty = 0
    for replica, child, stream, lo, hi, routed in windows:
        need(lo < hi, 'Chronological idle endpoint')
        if lo[0] < hi[0]:
            nonempty += 1
            need(not (lo < (lo[0], -1) < hi), 'An observation in the same call cannot be crossed')
            need(lo < (hi[0], -1) < hi, 'Host before the later idle endpoint is legal')
        if routed:
            shared[replica, stream].append((lo, hi))
    for intervals in shared.values():
        ordered = sorted(intervals)
        for previous, following in zip(ordered, ordered[1:]):
            need(previous[1] <= following[0], 'No overlapping active windows of one physical stream')
    payload = json.dumps(windows, separators=(',', ':')).encode()
    return dict(windows=len(windows), routed_windows=sum(w[-1] for w in windows),
                windows_with_at_least_one_whole_call=nonempty,
                timestamped_windows_sha256=hashlib.sha256(payload).hexdigest(),
                full_owner_rows_recounted_by_this_review=False,
                scope='Fresh independent event-window reconstruction and boundary checks; the full 1321920-row recount is source-bound reuse from the reviewed invoice.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, default=LATE / 'release-work/full')
    ap.add_argument('--out', type=Path, default=LATE / 'RELEASE-STATIC-REVIEW.json')
    args = ap.parse_args()
    need(__debug__, 'Assertions enabled')
    work = args.work.resolve()
    invoice = read(LATE / 'invoice/RESULT.json')
    operator = read(LATE / 'T360-OPERATOR-ADMISSION.json')
    need(sha(LATE / 'run_release.py') == '262e914eca3d0e97567786fe94cb25fb1698c52e08785fd4a2581020c4af26dc', 'Reviewed final runner')
    need(sha(LATE / 'invoice/RESULT.json') == 'c9de9aeaa3cf4e11d27d4fc95ef94913301a6bf99fa8f919fb4f643793a7dc47', 'Reviewed invoice')
    need(sha(LATE / 'T360-OPERATOR-ADMISSION.json') == '98d2936c758703c25637cf335e06691f8a55b3717105595e350917782b449b47', 'Reviewed operator receipt')
    all_inputs = dict(invoice['source_pins'])
    for rel, digest in operator['input_files'].items():
        need(rel not in all_inputs or all_inputs[rel] == digest, 'Consistent shared source pin')
        all_inputs[rel] = digest
    for rel, digest in all_inputs.items():
        need(sha(REPO / rel) == digest, 'Exact invoice/operator source ' + rel)
    preflight = read(work / 'PREFLIGHT-RESULT.json')
    need(preflight['status'] == 'PASS_ALL_THREE_WORD_REVIEWS_SOURCE_READY_NOT_ADMITTED', 'Honest source-only preflight')
    need(preflight['runner_sha256'] == sha(LATE / 'run_release.py'), 'Executed preflight runner')
    source_manifest = read(work / 'inputs/source/MANIFEST.json')
    need(len(source_manifest) == 676 and sha(work / 'inputs/source/MANIFEST.json') == '4116ef61479e509811b60b5fd4e84db8811dae079092f2f83bdcc2c80052c0da', 'Exact composed scientific source')
    actual_files = {p.relative_to(work / 'inputs/source').as_posix(): sha(p)
                    for p in sorted((work / 'inputs/source').rglob('*'))
                    if p.is_file() and p.relative_to(work / 'inputs/source').as_posix() != 'MANIFEST.json'}
    need(actual_files == source_manifest, 'Complete unchanged scientific source inventory')
    reviews = preflight['completed_reviews']
    need([s['name'] for s in reviews] == ['independent-terminal-word', 'independent-staged-word', 'independent-receiver-word'], 'All three separate ancestor reviews')
    need(all(s['exit_code'] == 0 and sha(work / (s['name'] + '.log')) == s['log_sha256'] for s in reviews), 'Actual preflight review logs')
    changes = literal_adaptations()
    controls = incomplete_claim_controls(invoice, operator)
    windows = event_windows()
    need(windows['windows'] == operator['owner_child_windows'] and windows['routed_windows'] == invoice['owner_windows'], 'Both active and total window counts')
    # The outer checkers have exactly the already reviewed bytes, including
    # the endpoint-dependent grid, strict margins, and rejecting controls.
    primary_review = read(SCOPE / 'operator-correction/RELEASE-STATIC-REVIEW.json')
    for name in ('check_ledger.py', 'independent_check.py'):
        old = 'research/kappa-operator-repair/composed-supplier/release-work/inputs/source/outer/' + name
        need(sha(work / 'inputs/source/outer' / name) == primary_review['reviewed_files'][old], 'Unchanged reviewed outer checker')
    files = [LATE / name for name in ('run_release.py', 'invoice.py', 'invoice/RESULT.json',
              'T360-OPERATOR-ADMISSION.json', 'collect_release.py', 'build_claim.py', 'CLAIM-ADAPTATION.json',
              'candidate/CONSTRUCTION.json', 'candidate/BORROW-WORD-43base.json.gz', 'candidate/BORROW-WORD-43extra.json.gz')]
    files += [SCOPE / 'operator-correction' / name for name in ('full_operator.py', 't360_admission.py', 'RELEASE-STATIC-REVIEW.json')]
    files += [work / name for name in ('ADAPTER.json', 'COMPOSED-ADMISSION-ADAPTER.json', 'SOURCE-ADAPTATION.json',
              'PREFLIGHT-RESULT.json', 'admit_staged.py', 'admit_composed.py', 'inputs/source/MANIFEST.json',
              'inputs/source/new/borrow/receiver_share.py', 'inputs/source/new/borrow/review_receiver_share.py',
              'inputs/source/new/borrow/staged_entries_review.py', 'inputs/source/new/borrow/terminal_review.py',
              'inputs/source/outer/check_ledger.py', 'inputs/source/outer/independent_check.py')]
    files.append(Path(__file__))
    pins = {p.relative_to(REPO).as_posix(): sha(p) for p in files}
    result = dict(status='PASS_SCOPED_READ_ONLY_RELEASE_AND_INVOICE_REVIEW', acceptance_defects_found=False,
                  reviewed_files=pins, source_modified=False,
                  review_type='Independent static review with fresh source authentication, literal adaptation, event-window and incomplete-claim controls. No native, complete invoice or inherited full release is rerun by this review.',
                  source_inputs_authenticated=len(all_inputs), source_files_authenticated=676,
                  literal_claim_adaptations=changes, incomplete_claim_rejections=controls,
                  independent_event_windows=windows,
                  kappa_formula='0.001730970419199163702738 - 10^-46 - 10^-70',
                  findings=[
                      dict(area='literal ancestry and full dirty words', result='Terminal review still compares to staged3/PRE. Staged-entry review compares to the exact saved receiver parent. The receiver identity and both sign mutations use the literal shifted indices683,684,685. Cleanup is regenerated before the complete arbitrary-column rejection controls.'),
                      dict(area='native and actual owner interface', result='Both complete candidates, all632 native endpoints, 91 owned-zero buffers, allfive executed native stages and their compiler sources are bound. Both directions are recounted. All1321920 helper occurrences have one owner, same-call family injection, productive nonaliasing, exact event windows, compact offsets and disjoint original phase axes. The70876 MOVES records reassign owner roles; they do not move phase axes between children.'),
                      dict(area='all-character operator proof', result='The unchanged exact Z4 quadratic phase normalization is checked for all112 ordered port recipes, yielding10416 identities and the proved signed controller. Hosted factors commute only inside their own physical observer interval and reassemble their original child with its complement. The finite character-polynomial identity covers every Fourier character and positive tensor multiplicity, subject to the explicit native/common-cover embedding interfaces.'),
                      dict(area='isolated runner and preflight', result='The runner authenticates the exact676-source tree, allthree source reviews, runtime adapter and admission adapter. A resume accepts only its own runner/source/adaptation/log pins. Preflight and prepare-only statuses do not assert admission. The final runner requires the exact separately executed invoice/operator bytes and all125 inputs, allfive native stages, ordered widths and profiles, followed by complete inherited release.'),
                      dict(area='collector and claim conjunction', result='Collection requires completed runner/admission/release statuses and exactκ, source/package manifests and logs. It preserves the changed word reviewers and both outer checkers. The late claim uses six ordered runner stages and seven ordered inherited stages, cross-links actual words/native cache/source/operator/invoice, authenticates all retained files, and retains13 full-record rejecting controls. The runtime review paths relocate through the collected release-work/full suffix.'),
                      dict(area='outer convention and target', result='Both outer checkers are byte-identical to their reviewed predecessors. Their actual endpoint-dependent grid and backoff deduct10^-46+10^-70 from the complex endpoint; the sufficient retained outer BIT lower exceeds this complex supplier. The proposed conditional improvement remains below.001745 and retains the withdrawal of the faulty phase-overlay claim.'),
                  ],
                  nonblocking_documentation_observations=['The collector native_mode prose redundantly mentions composed-supplier before the correct late-staged-composition location; all operational native paths and pins select late-staged-composition/native-base and native-extra.'],
                  unverified_or_conditional=['The full late conditional release is not asserted complete by this static review. Its eventual executed result, collection and final claim remain mandatory.',
                      'No second native or1321920-row invoice replay was run by this reviewer; their completed exact receipts and source pins were authenticated.',
                      'Uniform native realization, owner/common-cover embeddings, tape/compiler/precision/recovery, recurrence and outer hypotheses remain explicit conditional interfaces.',
                      'This is neither independent human review nor a formal proof-kernel audit.'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], len(pins), 'reviewed files', len(all_inputs), 'authenticated inputs', len(controls), 'rejecting fixtures', flush=True)


if __name__ == '__main__':
    main()
