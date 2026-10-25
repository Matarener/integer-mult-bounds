#!/usr/bin/env python3
"""Choose real signed cleanup for the unchanged three-row BIT construction.

The coded BIT endpoint is modulo2.  Unlike the original all-positive integer
lift, this forward lift restores all438 dirty helpers exactly overZ, and its
source code acts only on x.  No native/global admission is inferred.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import bit_transvection as base
import bit_scalar_invoice as scalar

HERE = Path(__file__).resolve().parent
N,V = 660,111


def source_integer_code(records):
    code = [r for r in records if r[0] == 1 and 21 <= r[5] <= 24]
    rows = [[int(i == j) for j in range(V)] for i in range(V)]
    for op,dst,src,c,frame,phase in code:
        rows[dst] = [a+c*b for a,b in zip(rows[dst],rows[src])]
    inverse = [[int(i == j) for j in range(V)] for i in range(V)]
    for op,dst,src,c,frame,phase in reversed(code):
        inverse[dst] = [a-c*b for a,b in zip(inverse[dst],inverse[src])]
    trial = [row[:] for row in rows]
    for op,dst,src,c,frame,phase in reversed(code):
        trial[dst] = [a-c*b for a,b in zip(trial[dst],trial[src])]
    base.require(trial == [[int(i == j) for j in range(V)] for i in range(V)],
                 'Integer source code and inverse fail')
    return rows,inverse


def column_control(records, input_column, bad_phase):
    values = [int(i == input_column) for i in range(N)] + [0]
    for op,dst,src,c,frame,phase in records:
        if op == 1:
            values[dst] += (1 if phase == bad_phase else c)*values[src]
        elif op == 2:
            values[N] = values[dst]
        elif op == 3:
            base.require(values[N] == values[dst], 'Control snapshot failed before endpoint')
            values[N] = 0
    differences = [dict(row=i,value=values[i],expected=int(i == input_column))
                   for i in range(2*V,N) if values[i] != int(i == input_column)]
    base.require(differences, 'Bad cleanup sign control escaped')
    return dict(input_column=input_column,bad_phase=bad_phase,first_difference=differences[0])


def main():
    old_meta = json.loads((HERE/'BIT-THREE-ROW.json').read_text())
    old_blob = (HERE/'BIT-THREE-ROW-WORD.json.gz').read_bytes()
    base.require(hashlib.sha256(old_blob).hexdigest() == old_meta['output_gzip_sha256'],
                 'Raw three-row source changed')
    word = json.loads(gzip.decompress(old_blob))
    records = [r[:] for r in word['records']]
    copy_number = -1
    changes = Counter()
    for r in records:
        op,dst,src,c,frame,phase = r
        if op == 2:
            copy_number += 1
        if op != 1:
            continue
        if phase in (5,24,17) or (phase == 15 and copy_number%2 == 0):
            r[3] = -1
            changes[str(phase)] += 1
    base.require(copy_number+1 == 6, 'Wrong snapshot episode count')
    forward,fwd = scalar.execute(records,scalar.eye(N))
    inverse,rev = scalar.execute(records,scalar.eye(N),reverse=True)
    roundtrip,rt = scalar.execute(records,forward,reverse=True)
    base.require(roundtrip == scalar.eye(N), 'Signed integer roundtrip failed')
    A,Ainv = source_integer_code(records)
    for p in range(V):
        base.require(forward[p] == A[p]+[0]*(N-V),
                     'Forward integer source code depends on a target/helper')
        base.require(inverse[p] == Ainv[p]+[0]*(N-V),
                     'Inverse integer source code depends on a target/helper')
    for h in range(2*V,N):
        base.require(forward[h] == [int(j == h) for j in range(N)],
                     f'Actual forward integer helper{h} not restored')
        base.require(inverse[h] == [int(j == h) for j in range(N)],
                     f'Actual inverse integer helper{h} not restored')
    for p in range(V):
        base.require(forward[V+p][V:2*V] == [int(j == p) for j in range(V)],
                     'Integer target self-block changed')
        base.require(all(x%2 == 0 for x in forward[V+p][2*V:]),
                     'Integer target has odd dirty-helper leakage')
    expected_forward = [1 << j for j in range(N)] + [0]
    expected_inverse = expected_forward[:]
    for p in range(V):
        expected_forward[p] = old_meta['matrices']['H'][p]
        expected_forward[V+p] ^= old_meta['matrices']['H'][p]
        expected_inverse[p] = old_meta['matrices']['Hinv'][p]
        expected_inverse[V+p] ^= 1 << p
    base.require(scalar.parity(forward) == expected_forward, 'Signed forward parity differs')
    base.require(scalar.parity(inverse) == expected_inverse, 'Signed inverse parity differs')
    # The ordinary all-input frame audit treats +/-1 equally overF2, but now
    # consumes this actual signed record list, with the original source bytes.
    raw_word,builder,baseline,_ = base.load()
    native_scalar_forward = base.replay(raw_word,builder,records,old_meta['matrices'])
    native_scalar_reverse = base.replay(raw_word,builder,records,old_meta['matrices'],reverse=True)
    controls = [column_control(records,0,5),column_control(records,0,17)]
    word['format'] = 'coded-r438-three-row-signed-local-records-v1'
    word['records'] = records
    word['signed_from'] = old_meta['output_gzip_sha256']
    raw = base.canonical(word)
    outword = HERE/'BIT-SIGNED-WORD.json.gz'
    outword.write_bytes(gzip.compress(raw,mtime=0))
    F,R = fwd['maximum_exact_prefix_row_l1'],rev['maximum_exact_prefix_row_l1']
    output = dict(status='PASS_SIGNED_LIFT_ACTUAL_FORWARD_DIRTY_RESTORATION_NO_GLOBAL_TRANSFER',
                  raw_word_gzip_sha256=old_meta['output_gzip_sha256'],
                  output_word=str(outword),output_gzip_sha256=hashlib.sha256(outword.read_bytes()).hexdigest(),
                  output_canonical_sha256=hashlib.sha256(raw).hexdigest(),
                  matrices_sha256=hashlib.sha256(base.canonical(old_meta['matrices'])).hexdigest(),
                  signed_changes=dict(sorted(changes.items())),
                  forward=fwd,reverse_signed=rev,roundtrip_signed=rt,
                  source_code=scalar.small_bounds(records),
                  source_integer_matrix_sha256=scalar.digest(A),
                  source_integer_inverse_sha256=scalar.digest(Ainv),
                  public_integer_input_columns=N,
                  actual_forward_integer_equalities=dict(source='A_Z x, independent of all targets/helpers',
                                                        dirty_helpers='all438 exactly h',private='exactly zero',
                                                        target='y+T_Z x+E_Z h, with T_Z mod2=A and E_Z even'),
                  actual_inverse_integer_equalities=dict(source='A_Z^-1 x',dirty_helpers='all438 exactly h',private='exactly zero'),
                  signed_prefix_F=F,signed_prefix_R=R,
                  old_formula_screen_with_exact_signed_norms=dict(local_bits=(64*F**3*R**2).bit_length(),
                                                                 nine_bits=((1<<18)*F**5*R**4).bit_length(),
                                                                 applicability='Requires new proof that exact signed coefficient norms meet the native rounded-network contract'),
                  cancellation_free=base.positive_bounds(records,N),
                  local_frame_invoice=native_scalar_forward,
                  local_reverse_frame_invoice=native_scalar_reverse,
                  ADDs=sum(r[0] == 1 for r in records),
                  negative_controls=controls,
                  scope='Exact full660-column integer forward, inverse, parity and helper restoration. The target/source coded BIT identity is modulo2, not equality overZ.',
                  unresolved=['Native/global63-code-bridge invoice and its signed source code',
                              'Complete rounded-network perturbation weights and precision/payload reserve',
                              'Terminal N E^-1 N, chronological owner and all-size physical supplier'])
    (HERE/'BIT-SIGNED-LIFT.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:output[k] for k in ('status','signed_changes','signed_prefix_F','signed_prefix_R',
                                          'old_formula_screen_with_exact_signed_norms','source_code','ADDs')},
                     indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
