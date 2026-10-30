#!/usr/bin/env python3
"""Read-only structural inventory; no native compiler or scientific replay.

New inventory: Chris R/Clear1nsight with OpenAI Codex assistance, Apache-2.0.
Construction and previous audits retain their source notices and credit.
"""
from pathlib import Path
from collections import Counter, defaultdict
import gzip
import hashlib
import json

B = Path(__file__).resolve().parent
ROOT = B.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length()-1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def inventory(manifest):
    for path, sha in manifest['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, 'source pin '+path)
    word = json.loads(gzip.decompress((ROOT/manifest['word']).read_bytes()))
    caller = json.loads((ROOT/manifest['caller_result']).read_text())
    contact = json.loads((ROOT/manifest['contact_result']).read_text())
    author = json.loads((ROOT/manifest['author_result']).read_text())
    need(caller['reviewed_head'] == contact['reviewed_head'] == manifest['reviewed_head'], 'previous audits bind same source head')
    need(caller['sources'][manifest['word']] == manifest['files'][manifest['word']], 'previous caller binds exact current word')
    for basis in word['frames']:
        need(all(type(v) is int and 0 < v < 512 for v in basis) and rank(basis) == len(basis), 'independent literal nine-axis frame')
    rows = defaultdict(lambda: {'paid_events':[], 'paid_owners':set(), 'private':0, 'public':0, 'helper_fields':[], 'coverage':[]})
    paid_profile = Counter()
    for at, event in enumerate(word['program']):
        if event[0] != 'MOVE':
            continue
        _, owner, a, b, private = event
        da, db = len(word['frames'][a]), len(word['frames'][b])
        need((db < da) if private else (da < db), 'strict legal paid frame direction')
        need(rank(word['frames'][a]+word['frames'][b]) == max(da, db), 'actual nested paid frames')
        rec = rows[a, b]
        rec['paid_events'].append(at)
        rec['paid_owners'].add(owner)
        rec['private' if private else 'public'] += 1
        paid_profile[abs(db-da)] += 1
    mains = set(word['live']) | {i+112 for i in word['live']}
    helpers = [i for i in range(735) if i not in mains]
    old_helpers = {r['local_field']:r for r in caller['helper_normalizers']}
    need(set(old_helpers) == set(helpers), 'all previous helper owners preserved')
    for h in helpers:
        a, b = word['initial'][h], word['final'][h]
        need((a, b) == (old_helpers[h]['initial'], old_helpers[h]['final']), 'exact previous helper frame pair')
        rows[a, b]['helper_fields'].append(h)
        if 'PR5550_helper_endpoint' not in rows[a, b]['coverage']:
            rows[a, b]['coverage'].append('PR5550_helper_endpoint')
    for label, record in contact['maps'].items():
        key = record['old_frame'], record['new_frame']
        if key in rows:
            rows[key]['coverage'].append('PR5548_full_matrix_'+label)
    records = []
    for (a, b), rec in sorted(rows.items()):
        r = abs(len(word['frames'][b])-len(word['frames'][a]))
        need(r > 0, 'positive required Gaussian rank')
        records.append({'old_frame':a, 'new_frame':b, 'rank':r,
                        **{k:sorted(v) if isinstance(v, set) else v for k, v in rec.items()}})
    need(len(records) == author['native']['distinct_maps'] == 2981, 'exact author native pair census reconciled')
    need(paid_profile == Counter({int(k):v for k,v in author['local']['paid'].items()}), 'complete paid histogram reconciled')
    covered = [r for r in records if r['coverage']]
    uncovered = [r for r in records if not r['coverage']]
    need(all(r['paid_events'] and not r['helper_fields'] for r in uncovered), 'all uncovered pairs are actually paid and not inherited helper endpoints')
    private = [r for r in uncovered if r['private']]
    high = [r for r in uncovered if r['rank'] >= 4]
    low = [r for r in uncovered if r['rank'] <= 3]
    summary = {'required_pairs':len(records), 'paid_pairs':sum(bool(r['paid_events']) for r in records),
               'helper_pairs':sum(bool(r['helper_fields']) for r in records), 'covered_pairs':len(covered),
               'uncovered_pairs':len(uncovered), 'covered_paid_occurrences':sum(len(r['paid_events']) for r in covered),
               'uncovered_paid_occurrences':sum(len(r['paid_events']) for r in uncovered),
               'private_uncovered_pairs':len(private), 'private_uncovered_occurrences':sum(r['private'] for r in private),
               'high_rank_uncovered_pairs':len(high), 'high_rank_uncovered_occurrences':sum(len(r['paid_events']) for r in high),
               'low_rank_uncovered_pairs':len(low),
               'uncovered_rank_pairs':dict(sorted(Counter(r['rank'] for r in uncovered).items())),
               'uncovered_rank_occurrences':dict(sorted(Counter({k:sum(len(r['paid_events']) for r in uncovered if r['rank'] == k) for k in range(1,10)}).items())),
               'paid_profile':dict(sorted(paid_profile.items())), 'paid_occurrences':sum(paid_profile.values()),
               'main_adapters_separate':len(caller['intrinsic_main_adapters'])}
    return {'schema':'p104-native-pair-inventory/v1', 'reviewed_head':manifest['reviewed_head'],
            'summary':summary, 'maps':records, 'compiler_executed':False,
            'native_maps_newly_validated':0, 'kappa_claim':None}


if __name__ == '__main__':
    print(json.dumps(inventory(json.loads((B/'INPUTS.json').read_text())), sort_keys=True, separators=(',', ':')))
