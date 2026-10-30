#!/usr/bin/env python3
"""Source-bound high-rank/private native qualification; scope in CONTRACT.md.

New independent checks: Chris R/Clear1nsight with OpenAI Codex assistance.
Apache-2.0; retained source/compiler/native interpreter credit remains intact.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
import os
import resource
import sys
import time

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
START = time.monotonic()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def checkpoint(stage, **counts):
    name = os.environ.get('P104_NATIVE_TRACE')
    if name:
        with open(name, 'a') as stream:
            stream.write(json.dumps({'stage':stage, 'elapsed_seconds':time.monotonic()-START,
                                     'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                     **counts}, sort_keys=True)+'\n')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(raw, expected):
    need(sha(raw) == expected, 'source authentication before scientific import')


def reject(work):
    try:
        work()
    except ValueError as e:
        return str(e)
    raise ValueError('deliberate native fault was accepted')


def main():
    checkpoint('authenticate_begin')
    pins = json.loads((B/'INPUTS.json').read_text())
    for name, expected in pins['files'].items():
        authenticate((ROOT/name).read_bytes(), expected)
    nomination = json.loads((B/'NOMINATION.json').read_text())
    raw_inventory = (B/'INVENTORY.json').read_bytes()
    authenticate(raw_inventory, nomination['inventory_sha256'])
    previous = json.loads((ROOT/pins['caller_result']).read_text())
    contact_result = json.loads((ROOT/pins['contact_result']).read_text())
    for path in ('outputs/p104-native-contact-audit-20261025/sources/clifford_exact.py',
                 'outputs/p104-native-contact-audit-20261025/sources/native_verify.py'):
        need(previous['sources'][path] == contact_result['source_hashes'][path] == pins['files'][path],
             'inherited receipts bind the exact compiler/literal definitions')
    need(sha((ROOT/pins['caller_result']).read_bytes()) == 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009', 'published PR5550 complete receipt')
    need(sha((ROOT/pins['contact_result']).read_bytes()) == '34299df26387b69f1a89cc52d52cae3add51f4e12c0715e0de38d42fab302c9f', 'published PR5548 complete receipt')
    for stem, receipt_path, result_path in [
        ('caller', 'outputs/p104-caller-route-audit-v2-20261025/PAIR-RECEIPT.json', pins['caller_result']),
        ('contact', 'outputs/p104-native-contact-audit-20261025/PAIR-RECEIPT.json', pins['contact_result'])]:
        receipt = json.loads((ROOT/receipt_path).read_text())
        need(receipt['complete_output_equal'] and receipt['scientific_fields_excluded'] == 0, 'complete previous '+stem+' receipt')
        authenticate((ROOT/result_path).read_bytes(), receipt['result_sha256'])
    native_request = json.loads((B/'REQUEST.json').read_text())
    authenticate((B/'inventory.py').read_bytes(), native_request['inventory_code_sha256'])
    I = load(B/'inventory.py', 'p104_paid_pair_inventory')
    rebuilt = I.inventory(pins)
    need(encoded(rebuilt)+b'\n' == raw_inventory, 'complete frozen structural inventory equality')
    selected = [r for r in rebuilt['maps'] if not r['coverage'] and (r['rank'] >= 4 or r['private'])]
    need([[r['old_frame'],r['new_frame']] for r in selected] == nomination['selected_pairs'], 'exact nominated map set')
    need(len(selected) == nomination['selected_pair_count'] == 182 <= nomination['max_maps'], 'bounded182-map subset')
    need(sum(len(r['paid_events']) for r in selected) == nomination['paid_occurrences'] == 246, 'complete selected occurrence census')
    need(sum(bool(r['private']) for r in selected) == nomination['private_pairs'] == 11, 'all eleven private returns included')
    word = json.loads(gzip.decompress((ROOT/pins['word']).read_bytes()))
    C = load(ROOT/'outputs/p104-native-contact-audit-20261025/sources/clifford_exact.py', 'paid_native_compiler')
    V = load(ROOT/'outputs/p104-native-contact-audit-20261025/sources/native_verify.py', 'paid_native_literal')
    D = load(ROOT/'outputs/p104-native-contact-audit-20261025/check.py', 'paid_native_dense')
    checkpoint('native_begin', maps=len(selected))

    @lru_cache(None)
    def chart(index):
        return C.canonical_frame(9, tuple(word['frames'][index]))

    @lru_cache(None)
    def literal_frame(index):
        return V.frame(word['frames'][index], 9)

    def compare(actual, expected, label):
        actual_tableau, expected_tableau = V.tableau(actual), V.tableau(expected)
        need(actual_tableau == expected_tableau, label+' all eighteen signed Pauli images')
        left = D.dense_column(D.compile_circuit(actual), 0)
        right = D.dense_column(D.compile_circuit(expected), 0)
        need(left == right, label+' independent exact absolute phase anchor')
        real, imag, denominator = left
        need(sum(x*x for x in real)+sum(x*x for x in imag) == 1 << (2*denominator), label+' exact nonzero unit column')
        return expected_tableau, left

    records, representatives = [], {}
    selected_profile = Counter()
    for index, row in enumerate(selected):
        a, b, rank = row['old_frame'], row['new_frame'], row['rank']
        rec, _ = C.lower_child(chart(a).adjoint().then(chart(b)))
        actual = V.recipe(rec)
        literal = V.adjoint(literal_frame(a))+literal_frame(b)
        tableau, column = compare(actual, literal, 'frame '+str((a,b)))
        independent_rank = I.rank([x for x, z, phase in tableau[9:]])
        need(rec['rank'] == rank == independent_rank == abs(len(word['frames'][b])-len(word['frames'][a])), 'independent literal B-block/geometry/charged rank')
        need(sum(g[0] == 'C' for g in actual) == rank and all(g[2] == 1 for g in actual if g[0] == 'C'), 'positive standard Gaussian child with actual monomial boundaries')
        for at in row['paid_events']:
            event = word['program'][at]
            need(event[0] == 'MOVE' and event[2:4] == [a,b], 'recipe attached to every literal paid event')
        selected_profile[rank] += len(row['paid_events'])
        role = 'private' if row['private'] else 'public'
        if role not in representatives:
            representatives[role] = (row, rec, actual, literal)
        records.append({'old_frame':a, 'new_frame':b, 'rank':rank,
                        'paid_events':row['paid_events'], 'paid_owners':row['paid_owners'],
                        'private_occurrences':row['private'], 'public_occurrences':row['public'],
                        'recipe':rec, 'signed_Pauli_images':tableau, 'phase_anchor_column':0,
                        'phase_anchor_sha256':sha(encoded(column)), 'phase_anchor_dyadic_denominator':column[2],
                        'actual_gate_count':len(actual), 'literal_gate_count':len(literal)})
        if index % 20 == 0 or index == len(selected)-1:
            checkpoint('native_progress', completed=index+1)
    need(dict(selected_profile) == {int(k):v for k,v in nomination['selected_paid_profile'].items()}, 'complete selected paid profile')
    controls = {}
    for role, (row, rec, actual, literal) in representatives.items():
        wrong_phase = actual+(('phase',1),)
        need(V.tableau(wrong_phase) == V.tableau(actual), 'phase fault invisible to Pauli images')
        controls[role+'_global_phase'] = reject(lambda: compare(wrong_phase, literal, 'global phase fault'))
        inverse = list(actual)
        at = next(i for i,g in enumerate(inverse) if g[0] == 'C')
        inverse[at] = ('C', inverse[at][1], -inverse[at][2])
        controls[role+'_inverse_child'] = reject(lambda: compare(tuple(inverse), literal, 'inverse child fault'))
        bad = deepcopy(rec)
        bad['left']['offset'] ^= 1
        controls[role+'_wrong_boundary'] = reject(lambda: compare(V.recipe(bad), literal, 'monomial boundary fault'))
        a, b = row['old_frame'], row['new_frame']
        reverse = V.adjoint(literal_frame(b))+literal_frame(a)
        controls[role+'_reverse_orientation'] = reject(lambda: compare(actual, reverse, 'reverse frame orientation fault'))
        controls[role+'_wrong_rank'] = reject(lambda: need(rec['rank']+1 == row['rank'], 'wrong declared Gaussian rank'))
    first = selected[0]['paid_events'][0]
    expected_occurrences = sorted(at for row in selected for at in row['paid_events'])
    controls['lost_paid_occurrence'] = reject(lambda: need([at for at in expected_occurrences if at != first] == expected_occurrences, 'lost selected paid occurrence'))
    for label, path in [('compiler','outputs/p104-native-contact-audit-20261025/sources/clifford_exact.py'),
                        ('literal','outputs/p104-native-contact-audit-20261025/sources/native_verify.py')]:
        controls[label+'_source_corruption'] = reject(lambda: authenticate((ROOT/path).read_bytes()+b'\nFAULT', pins['files'][path]))
    inherited = {tuple((row['old_frame'],row['new_frame'])) for row in rebuilt['maps'] if row['coverage']}
    qualified = inherited | {(row['old_frame'],row['new_frame']) for row in selected}
    remaining = [row for row in rebuilt['maps'] if (row['old_frame'],row['new_frame']) not in qualified]
    need(len(qualified) == 224 and len(remaining) == nomination['remaining_uncovered_pairs'] == 2757, 'exact combined coverage partition')
    need(all(row['rank'] < 4 and not row['private'] for row in remaining), 'all high-rank and private maps covered; residual public low ranks explicit')
    complete_local = Counter(rebuilt['summary']['paid_profile'])
    # Reassemble the complete source invoice using unchanged external jobs.
    author = json.loads((ROOT/pins['author_result']).read_text())
    need({str(k):v for k,v in complete_local.items()} == author['local']['paid'], 'unchanged full local paid profile')
    need(sum(previous['paid'].values()) == 69912 and sum(previous['targets'].values()) == 12814, 'inherited complete caller bill unchanged')
    result = {'schema':'p104-high-rank-private-native-audit/v1', 'status':'PASS_SCOPED_HIGH_RANK_AND_PRIVATE_NATIVE_MAPS',
              'reviewed_head':pins['reviewed_head'], 'canonical_main':pins['canonical_main'],
              'input_hashes':pins['files'], 'inventory_sha256':sha(raw_inventory),
              'maps':records, 'controls':controls, 'selected_paid_profile':dict(sorted(selected_profile.items())),
              'coverage':{'required_pairs':2981, 'previously_covered_pairs':42, 'newly_checked_pairs':len(records),
                          'combined_covered_pairs':len(qualified), 'remaining_pairs':len(remaining),
                          'new_paid_occurrences':sum(selected_profile.values()), 'combined_paid_occurrences':254,
                          'remaining_paid_occurrences':sum(len(row['paid_events']) for row in remaining),
                          'private_return_pairs_checked':11, 'all_rank_ge4_paid_maps_covered':True,
                          'remaining_rank_pairs':dict(sorted(Counter(row['rank'] for row in remaining).items())),
                          'remaining_pairs_list':[[row['old_frame'],row['new_frame']] for row in remaining]},
              'complete_local_paid_profile':dict(sorted(complete_local.items())),
              'complete_caller_paid_jobs':69912, 'complete_productive_fields':12814,
              'limits':['Remaining2757 public low-rank native maps are not newly checked.',
                        'Retained all-input/all-width native and owned-erasure framework assumptions remain.',
                        'No new precision/tape/storage, compiler/outer conjunction, raw-dual or human/formal admission.',
                        'No changed physical word, paid/target profile, scoped economic ceiling or kappa.'],
              'kappa_claim':None, 'stop':True}
    checkpoint('qualification_complete', maps=len(records), remaining=len(remaining))
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
