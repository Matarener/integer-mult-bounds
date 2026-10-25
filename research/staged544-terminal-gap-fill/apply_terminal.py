"""Literal source-guarded terminal/frame recipe; no search or solver required.
Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
import audit_core as audit


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def apply(source, patch):
    need(canonical(source) == patch['source_canonical_sha256'], 'source canonical hash')
    w = copy.deepcopy(source)
    for section, edits in patch['sections'].items():
        need(section in ('A', 'B', 'restore'), 'section')
        last = len(source[section]) + 1
        for edit in sorted(edits, key=lambda e: e['slice'][0], reverse=True):
            a, b = edit['slice']
            need(0 <= a <= b < last and b <= len(source[section]), 'disjoint source slices')
            need(w[section][a:b] == edit['old'], 'scalar splice preimage')
            w[section][a:b] = copy.deepcopy(edit['new'])
            last = a
    need(w['warps'] == patch['old_warps'], 'native warp preimage')
    w['warps'] = copy.deepcopy(patch['new_warps'])
    seen = set()
    for edit in patch['terminal_edits']:
        r = str(edit['helper'])
        need(r not in seen and w['helper_final'][r] == edit['old'], 'terminal preimage')
        seen.add(r)
        w['helper_final'][r] = copy.deepcopy(edit['new'])
    need(len(seen) == 26, 'terminal count')
    w['cleanup'] = audit.derive_cleanup(w)
    audit.hygiene(w)
    profile, inventory, _, _, _ = audit.frame_bill(w, lagrangian=True)
    profile = {str(k): v for k, v in profile.items()}
    inventory = {str(k): v for k, v in inventory.items()}
    need(profile == patch['declared_profile'], 'declared profile')
    need(inventory == patch['declared_inventory'], 'declared inventory')
    w['report']['local_profile'] = profile
    w['report']['width_inventory'] = inventory
    need(canonical(w) == patch['target_canonical_sha256'], 'target canonical hash')
    return w


def exact_semantics(w):
    need(audit.endpoint_defects(w, audit.forward_rows(w, symbolic_buffers=True)) == ([], [], [], True), 'arbitrary-dirty forward')
    need(audit.endpoint_defects(w, audit.forward_rows(w, dual=True, symbolic_buffers=True), dual=True) == ([], [], [], True), 'arbitrary-dirty dual')
    need(not audit.boundary_defects(w, audit.transpose(audit.reverse_columns(w, upto_cleanup=True))), 'cleanup boundary')
