#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reconstruct and independently audit both changed complete dirty words.

The exact all-column interpreter is the retained PR3687/3693 audit_core and
audit_verify by Sagar Thakrar. New scalar and mutation checks are explicit.
No recorded PASS value substitutes for executing the complete semantics.
"""
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import audit_core as C
from audit_verify import semantics
import receiver_share as R

P = Path(__file__).resolve().parent


def load(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def require(value, why):
    if not value:
        raise ValueError(why)


def scalar(events):
    roles = (544, 672, 676)
    rows = {r: [Q(int(r == s)) for s in roles] for r in roles}
    for _, target, source, num, den, frame in events:
        rows[target] = [a + Q(num, den) * b for a, b in zip(rows[target], rows[source])]
    return [rows[r] for r in roles]


def inspect(word):
    C.hygiene(word)
    bill, widths, _, _, _ = C.frame_bill(word)
    require(bill == R.PROFILE, 'actual changed local profile')
    require(widths == {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}, 'actual helper widths')
    require(word['cleanup'] == C.derive_cleanup(word), 'literal derived cleanup')
    return semantics(C, word)


def reject(name, function):
    try:
        function()
    except (ValueError, AssertionError, C.AuditFailure):
        return name
    raise ValueError('accepted mutation: ' + name)


require(scalar(R.OLD) == scalar(R.NEW), 'arbitrary three-register scalar identity')
rows = []
for tag in ('base', 'extra'):
    parent_path = P / 'receiver-share-parent' / ('BORROW-WORD-43' + tag + '.json.gz')
    word_path = P / 'words' / ('BORROW-WORD-43' + tag + '.json.gz')
    parent, word = load(parent_path), load(word_path)
    require(R.apply(parent) == word, 'literal extension reconstructs current word')
    require(parent['B'][683:685] == R.OLD and word['B'][683:686] == R.NEW, 'literal event binding')
    semantic = inspect(word)
    controls = []
    mutant = deepcopy(word)
    mutant['B'][685][3] = 1
    mutant['cleanup'] = C.derive_cleanup(mutant)
    controls.append(reject('closing_share_sign_flipped', lambda: semantics(C, mutant)))
    mutant = deepcopy(word)
    mutant['B'][683][3] = -1
    mutant['cleanup'] = C.derive_cleanup(mutant)
    controls.append(reject('opening_share_sign_flipped', lambda: semantics(C, mutant)))
    mutant = deepcopy(parent)
    mutant['report']['local_profile'] = {str(r): n for r, n in R.PROFILE.items()}
    controls.append(reject('old_frames_under_new_bill', lambda: inspect(mutant)))
    mutant = deepcopy(parent)
    mutant['B'][683][3] += 1
    controls.append(reject('changed_literal_preimage', lambda: R.apply(mutant)))
    rows.append(dict(provider=tag, source_sha256=hashlib.sha256(parent_path.read_bytes()).hexdigest(),
                     candidate_sha256=hashlib.sha256(word_path.read_bytes()).hexdigest(),
                     semantics=semantic, controls=controls))
print(json.dumps(dict(status='PASS_RECEIVER_SHARING_DIRTY_WORD_AND_CONTROLS',
                      providers=rows), sort_keys=True), flush=True)
