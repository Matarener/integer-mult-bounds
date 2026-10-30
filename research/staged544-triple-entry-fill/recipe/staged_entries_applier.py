"""Literal pinned staged-entry edits on PR3945's terminal-width5 words; no optimizer is needed to replay them.

Generalizes dataisfire's PR3734 stage544_applier (helper 544) to the three staged helpers 608, 609 and 600:
ordered literal slice edits of the scalar sections, explicit entrance (start_extra) raises with preimages,
native warps whose identities and maps are preserved, the declared report, and the derived cleanup.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
import copy, hashlib, json


def canonical(w): return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def need(ok, why):
    if not ok: raise ValueError(why)


def apply(parent, record):
    need(record.get('schema') == 'staged-entries-literal-v1', 'record schema')
    need(canonical(parent) == record['source_canonical_sha256'], 'source canonical digest')
    w = copy.deepcopy(parent)
    for sec, edits in record['sections'].items():
        need(sec in ('A', 'B', 'restore'), 'scalar section')
        old = parent[sec]; out = []; cursor = 0
        for edit in edits:
            a, b = edit['slice']; need(cursor <= a <= b <= len(old), 'ordered slice')
            need(old[a:b] == edit['old'], 'literal scalar preimage')
            out += copy.deepcopy(old[cursor:a]) + copy.deepcopy(edit['new']); cursor = b
        w[sec] = out + copy.deepcopy(old[cursor:])
    seen = set()
    for e in record['entrances']:
        h = e['helper']; need(h not in seen and h not in parent['helper_final'], 'ordinary staged helper')
        need(parent['start_extra'].get(h) == e['old'], 'entrance preimage')
        need(len(e['new']) == len(e['old']) + 1, 'entrance raised by exactly one dimension')
        seen.add(h); w['start_extra'][h] = copy.deepcopy(e['new'])
    need(len(parent['warps']) == len(record['warps']), 'warp inventory')
    need(all(a[1:3] == b[1:3] for a, b in zip(parent['warps'], record['warps'])), 'native identities and maps preserved')
    w['warps'] = copy.deepcopy(record['warps']); w['report'].update(copy.deepcopy(record['report']))
    from staged_pair import cleanup
    w['cleanup'] = cleanup(w)
    need(set(k for k in parent if parent[k] != w[k]) <= {'A', 'B', 'restore', 'start_extra', 'warps', 'report', 'cleanup'}, 'changed field contract')
    need(canonical(w) == record['target_canonical_sha256'], 'target canonical digest')
    return w
