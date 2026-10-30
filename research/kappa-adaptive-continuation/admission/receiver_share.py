#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal receiver-sharing extension of the complete staged544 producer.

The source covector identity is credited to Nick Petalas; this transposed
application is this continuation's change to dataisfire's PR3734 word.
All preceding edits and their authors remain in the original replay chain.
"""
from copy import deepcopy
import audit_core as C

OLD = [['add', 672, 544, 1, 2, [414, 51]],
       ['add', 676, 544, -1, 2, [414, 51]]]
NEW = [['add', 672, 676, 1, 1, [51]],
       OLD[1],
       ['add', 672, 676, -1, 1, [413, 72, 48, 3]]]
PROFILE = {1: 2439, 2: 724, 3: 225, 4: 102, 5: 20, 8: 8}


def apply(word):
    assert word['B'][692:694] == OLD, 'exact receiver-sharing preimage'
    assert word['report']['local_profile'] == {
        '1': 2440, '2': 725, '3': 224, '4': 102, '5': 20, '8': 8}
    result = deepcopy(word)
    result['B'][692:694] = deepcopy(NEW)
    for warp in result['warps']:
        if warp[0] >= 694:
            warp[0] += 1
    result['cleanup'] = C.derive_cleanup(result)
    result['report']['local_profile'] = {str(r): n for r, n in PROFILE.items()}
    return result
