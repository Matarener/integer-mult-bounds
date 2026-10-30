"""Exact scalar inverse and literal Y-cleanup geometry; no native replay."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json


WORD_SHA256 = '934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775'
R_SHA256 = '7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(vectors):
    basis = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def run(word_path, R_path):
    """Read the two pinned archive members and return JSON-compatible facts."""
    raw, rraw = Path(word_path).read_bytes(), Path(R_path).read_bytes()
    need(sha256(raw).hexdigest() == WORD_SHA256, 'Wrong native word bytes')
    need(sha256(rraw).hexdigest() == R_SHA256, 'Wrong R bytes')
    word = json.loads(gzip.decompress(raw))
    rows = [[Fraction(value) for value in row] for row in json.loads(rraw)]
    need(len(rows) == 8 and all(len(row) == 112 for row in rows), 'Wrong R shape')
    gram = [[sum(a*b for a, b in zip(x, y)) for y in rows] for x in rows]
    need(gram == [[Fraction(56 if i == j else 0) for j in range(8)]
                  for i in range(8)], 'R Gram matrix is not 56 I8')
    # P=R^T R has P^2=56P. This is the coefficient of P in
    # (I-P/4)(I-P/52), establishing the displayed inverse exactly.
    inverse_coefficient = -Fraction(1, 4)-Fraction(1, 52)+Fraction(56, 208)
    need(inverse_coefficient == 0, 'Claimed C inverse does not multiply to I')
    mode = rows[5]
    delta_y = [-x/13 for x in mode]
    r_delta_y = [sum(a*b for a, b in zip(row, delta_y)) for row in rows]
    c_delta_y = [delta_y[i]-sum(rows[k][i]*r_delta_y[k] for k in range(8))/4
                 for i in range(112)]
    need(c_delta_y == mode, 'C deltaY is not r5 on all112 entries')

    canonical = word['canonical']
    frame_rows = canonical['frames']
    need(frame_rows[0] == [], 'Ground frame is not frame0')
    need(all(canonical['start'][i] == 0 for i in range(112, 224)),
         'Y does not start at ground')
    need(all(len(frame_rows[canonical['final'][i]]) == 8 for i in range(112, 224)),
         'Y does not finish at rank8')
    support = [i for i, value in enumerate(mode) if value]
    frames = [canonical['final'][112+i] for i in support]
    need(len(support) == 56 and set(mode) == {Fraction(-1), Fraction(0), Fraction(1)},
         'Unexpected mode5 support or coefficients')
    need(len(set(frames)) == 56, 'The56 Y destination frames are not distinct')
    need(all(binary_rank(frame_rows[f]+frame_rows[g]) == 9
             for i, f in enumerate(frames) for g in frames[i+1:]),
         'Two distinct Y target hyperplanes fail to join to rank9')
    containment = {}
    for frame in (72, 114, 115):
        need(len(frame_rows[frame]) == 1, 'Selected provider frame is not rank1')
        containment[str(frame)] = sum(binary_rank(frame_rows[frame]+frame_rows[g]) == 8
                                      for g in frames)
    need(containment == {'72': 28, '114': 24, '115': 24},
         'Unexpected rank1-provider containment counts')
    return {
        'schema': 1,
        'source_word_sha256': WORD_SHA256,
        'R_sha256': R_SHA256,
        'R_gram': '56 I8',
        'C_definition': 'I112 - transpose(R)*R/4',
        'R_times_C': '-13 R',
        'C_inverse': 'I112 - transpose(R)*R/52',
        'inverse_identity_checked_using_exact_R_gram': True,
        'pure_Y_route_assumption': 'deltaX = -C*deltaY; desired deltaX = -transpose(r5)*m',
        'unique_deltaY': '-transpose(r5)*m/13',
        'all112_C_times_deltaY_entries_equal_r5': True,
        'deltaY_nonzero_denominators': sorted({x.denominator for x in delta_y if x}),
        'Y_initial_rank': 0,
        'Y_final_rank': 8,
        'mode5_support': support,
        'mode5_Y_target_frames': frames,
        'distinct_rank8_targets': 56,
        'all_distinct_target_pairs_join_to_rank9': True,
        'rank1_chart_target_containment': containment,
        'scope': 'Conditional scalar identity and literal cleanup geometry only. No paid-native-route lower bound, dyadic compilation, or physical construction is claimed.',
    }
