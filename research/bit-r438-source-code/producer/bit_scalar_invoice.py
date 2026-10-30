#!/usr/bin/env python3
"""Literal scalar/integer prefix invoice of the three-target R438 producer.

No native operator lowering is assumed here.  The ordered integer lift uses
the emitted forward ADD coefficients +1; its inverse reverses the exact word
and uses -1.  Only reduction modulo2 has the declared coded BIT endpoint.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import bit_transvection as base

HERE = Path(__file__).resolve().parent
N = 660


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)] + [[0]*n]


def digest(rows):
    h = hashlib.sha256()
    for row in rows:
        h.update((','.join(map(str,row))+'\n').encode())
    return h.hexdigest()


def execute(records, initial, reverse=False, invert_sign=True):
    rows = [row[:] for row in initial]
    live, copies, maximum, phase_max = None, 0, 1, {}
    for number,(op,dst,src,coefficient,frame,phase) in enumerate(
            reversed(records) if reverse else records):
        if op == 1:
            sign = coefficient * (-1 if reverse and invert_sign else 1)
            rows[dst] = [a+sign*b for a,b in zip(rows[dst],rows[src])]
            value = sum(abs(x) for x in rows[dst])
            maximum = max(maximum,value)
            phase_max[str(phase)] = max(phase_max.get(str(phase),0),value)
        elif op == (3 if reverse else 2):
            base.require(live is None and not any(rows[N]), 'Integer COPY overwrites private dirt')
            rows[N], live = rows[dst][:], dst
            maximum = max(maximum,sum(abs(x) for x in rows[N]))
            copies += 1
        elif op == (2 if reverse else 3):
            base.require(live == dst and rows[N] == rows[dst],
                         f'Integer ERASE snapshot changed at record{number}')
            rows[N], live = [0]*N, None
        else:
            base.require(op == 0, 'Unknown integer operation')
    base.require(live is None and not any(rows[N]), 'Integer private buffer not clear')
    return rows,dict(maximum_exact_prefix_row_l1=maximum,
                     phase_exact_prefix_row_l1=phase_max,copies=copies,
                     endpoint_matrix_sha256=digest(rows),
                     endpoint_max_row_l1=max(sum(abs(x) for x in row) for row in rows))


def parity(rows):
    return [sum((x & 1) << j for j,x in enumerate(row)) for row in rows]


def small_bounds(records):
    selected = [r for r in records if r[0] == 1 and 21 <= r[5] <= 24]
    bounds, exact = [], []
    for reverse in (False,True):
        values = [1]*111
        for op,dst,src,coefficient,frame,phase in reversed(selected) if reverse else selected:
            values[dst] += abs(coefficient)*values[src]
        bounds.append(max(values))
        rows = [[int(i == j) for j in range(111)] for i in range(111)]
        maximum = 1
        for op,dst,src,coefficient,frame,phase in reversed(selected) if reverse else selected:
            sign = coefficient * (-1 if reverse else 1)
            rows[dst] = [a+sign*b for a,b in zip(rows[dst],rows[src])]
            maximum = max(maximum,sum(abs(x) for x in rows[dst]))
        exact.append(maximum)
    return dict(adds=len(selected),forward_positive=bounds[0],reverse_positive=bounds[1],
                forward_exact_prefix_l1=exact[0],reverse_exact_prefix_l1=exact[1],
                extra_helpers=0,extra_private_fields=0)


def main():
    meta = json.loads((HERE/'BIT-THREE-ROW.json').read_text())
    blob = (HERE/'BIT-THREE-ROW-WORD.json.gz').read_bytes()
    base.require(hashlib.sha256(blob).hexdigest() == meta['output_gzip_sha256'],
                 'Three-row word pin changed')
    word = json.loads(gzip.decompress(blob))
    records = word['records']
    start = eye(N)
    forward,fwd = execute(records,start)
    inverse,rev = execute(records,start,reverse=True)
    roundtrip,rt = execute(records,forward,reverse=True)
    base.require(roundtrip == start, 'Ordered integer inverse failed all660 columns')
    bad,bad_stats = execute(records,forward,reverse=True,invert_sign=False)
    base.require(bad != start, 'Wrong integer inverse sign control escaped')
    expected_forward = [1 << j for j in range(N)] + [0]
    expected_inverse = expected_forward[:]
    for p in range(111):
        expected_forward[p] = meta['matrices']['H'][p]
        expected_forward[111+p] ^= meta['matrices']['H'][p]
        expected_inverse[p] = meta['matrices']['Hinv'][p]
        expected_inverse[111+p] ^= 1 << p
    base.require(parity(forward) == expected_forward, 'Integer forward reduction differs')
    base.require(parity(inverse) == expected_inverse, 'Integer inverse reduction differs')
    positive = base.positive_bounds(records,N)
    base.require(fwd['maximum_exact_prefix_row_l1'] == positive['forward'],
                 'Forward positive envelope is not the exact nonnegative norm')
    base.require(rev['maximum_exact_prefix_row_l1'] <= positive['reverse'],
                 'Reverse triangle envelope failed')
    counts = Counter(r[0] for r in records)
    phase_adds = Counter(str(r[5]) for r in records if r[0] == 1)
    copy_ranks = Counter(r[5] for r in records if r[0] == 2)
    boundary = Counter(r[4] for r in records if r[0] == 0)
    output = dict(status='PASS_LITERAL_SCALAR_INTEGER_LIFT_AND_INVERSE_NO_GLOBAL_TRANSFER',
                  source_word_gzip_sha256=meta['output_gzip_sha256'],
                  covered_integer_columns=N,covered_integer_endpoint_coefficients=N*N,
                  forward=fwd,reverse_signed=rev,roundtrip_signed=rt,
                  source_code=small_bounds(records),positive=positive,
                  scalar_invoice=dict(ADD=counts[1],MOVE_children=counts[0],COPY=counts[2],ERASE=counts[3],
                                      ADDs_per_phase=dict(sorted(phase_adds.items())),
                                      COPY_rank_histogram=dict(sorted(copy_ranks.items())),
                                      MOVE_rank_histogram=dict(sorted(boundary.items())),
                                      owned_private_fields=1,max_live_immutable_snapshots=1,
                                      public_source_fields=111,public_target_fields=111,
                                      public_dirty_helper_fields=438,
                                      new_source_code_helpers=0,new_source_code_private_fields=0,
                                      extra_repair_helper_fields=0,reused_repair_helper=222),
                  negative_control=dict(wrong_reverse_integer_sign_detected=True,
                                        bad_roundtrip_sha256=bad_stats['endpoint_matrix_sha256'],
                                        F2_signs_cannot_detect_this_control=True),
                  exact_lift_statement='The emitted integer forward matrix reduces modulo2 to(Ax,y+Ax,h). Its exact inverse is the reversed word with negative ADD coefficients; all660 input columns restore overZ. The forward helper rows are NOT claimed to be identity overZ.',
                  precision_statement='F and reverse triangleR are exact ordered scalar envelopes for inputs with absolute value at most1, scaling linearly for larger bounds. Historical104/192 bit guards fail;173/320 are numerical sufficient exponents for the old scalar formulas, with applicability to a changed native/global interface still owed.',
                  unresolved=['Native field/address transport and actual integer normalization',
                              '63 extra global code bridges, their signed integer lift and full prefix bounds',
                              'Terminal N E^-1 N, chronological owner and physical stock',
                              'Complete payload/numerical scratch and all-size recurrence repricing'])
    (HERE/'BIT-SCALAR-INVOICE.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:output[k] for k in ('status','forward','reverse_signed','source_code','scalar_invoice')},
                     indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
