#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Encode PR #3633's literal T488 owner journal (FILL.json.gz from PR3633's deterministic expander,
owners/portable_expand.py) as data/FILL-columns.xz: the owner_replica (uint16), child, port and offset (uint8)
columns, little-endian, concatenated, xz-compressed.  time and helper are implicit (row i is (i // 408, i % 408)).
verify.py decodes it and re-serialises the rows in PR3633's documented format; the result must hash to PR3633's
pinned payload sha256 (owners/EXPECTED.json), so this encoding cannot change the audited object.

Usage: python3 -I -B tools/encode_journal.py PATH/TO/FILL.json.gz data/FILL-columns.xz
Standard library only.
"""
import gzip
import json
import lzma
import sys
from array import array


def main(src, dst):
    rows = json.loads(gzip.decompress(open(src, 'rb').read()))['rows']
    for i, r in enumerate(rows):
        assert r[0] == i // 408 and r[1] == i % 408, 'rows are not in (time, helper) order'
        assert 0 <= r[2] < 65536 and all(0 <= v < 256 for v in r[3:]), 'value outside the column type'
    cols = [array('H', (r[2] for r in rows))] + [array('B', (r[k] for r in rows)) for k in (3, 4, 5)]
    if sys.byteorder != 'little':
        cols[0].byteswap()
    blob = b''.join(c.tobytes() for c in cols)
    open(dst, 'wb').write(lzma.compress(blob, format=lzma.FORMAT_XZ, check=lzma.CHECK_SHA256,
                                        preset=9 | lzma.PRESET_EXTREME))
    print('ENCODED', len(rows), 'rows ->', dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
