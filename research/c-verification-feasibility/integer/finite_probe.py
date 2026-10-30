"""Finite qualification source for the source-only integer/format prototype.

Not executed by its author. Parent-owned serial runner must pay compilation,
loading, all checks, allocation/copy costs and complete qualification costs.
Literal expected arithmetic below does not call any candidate helper.
Ali Romman predecessor integer replay; Chris R / Clear1nsight and substantial
OpenAI Codex assistance for this derivative feasibility source. Apache-2.0.
"""
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def multiply(value, numerator, exponent):
    value *= numerator
    need(not exponent or value % (1 << exponent) == 0, 'exact dyadic division')
    return value >> exponent


def literal_row(dst, src, numerator, exponent, scores=None, weights=None):
    out = dict(dst)
    totals = None if scores is None else list(scores)
    for event, value in src.items():
        old = out.get(event, 0)
        new = old + multiply(value, numerator, exponent)
        if totals is not None:
            change = abs(new) - abs(old)
            totals[0] += change * weights[event][0]
            totals[1] += change * weights[event][1]
            totals[2] += change
        if new:
            out[event] = new
        else:
            out.pop(event, None)
    return out if totals is None else (out, tuple(totals))


def literal_coefficient_bytes(row, scale):
    parts = []
    for event in sorted(row, reverse=True):
        value = Fraction(row[event], scale)
        parts.append(f'{event}:{value.numerator}/{value.denominator};'.encode())
    return b''.join(parts)


def run(native):
    checks = []

    def reject(label, fn, exception):
        try:
            fn()
        except exception:
            checks.append(label)
        else:
            raise ValueError('accepted rejected fixture: ' + label)

    big = 1 << 8192
    cases = [
        ({}, {}, 1, 0),
        ({0: 8}, {0: 8}, -1, 0),
        ({0: 3, 1: -2}, {0: -8, 2: 16}, 3, 2),
        ({0: -3}, {0: 8, 3: -24}, -5, 3),
        ({0: big, 1: -big}, {0: big, 2: -3 * big}, 3, 130),
        ({0: 0, 1: 7}, {0: 0, 2: 8}, 0, 1),
        ({3: -1}, {0: -16, 1: 48}, -7, 4),
        ({0: big + 1}, {0: -(big + 1), 3: big - 1}, 1, 0),
    ]
    weights = [(3, 5), (7, 11), (13, 17), (19, 23)]
    scores = [29, 31, 37]
    for dst, src, numerator, exponent in cases:
        before = (dict(dst), dict(src), list(scores), list(weights))
        need(native.add_row(dst, src, numerator, exponent) ==
             literal_row(dst, src, numerator, exponent), 'sparse row equality')
        need(native.error_row(dst, src, numerator, exponent, scores, weights) ==
             literal_row(dst, src, numerator, exponent, scores, weights),
             'signed cancellation and weighted score equality')
        need(native.scale_row(src, numerator, exponent) ==
             {i: multiply(v, numerator, exponent) for i, v in src.items()},
             'scaled row equality including retained zero entries')
        need((dst, src, scores, weights) == before, 'all row inputs unchanged')
    checks.append('eight-row-and-score-differentials')

    same = {0: 8, 2: -16}
    snapshot = dict(same)
    need(native.add_row(same, same, -1, 0) == {}, 'safe aliased cancellation')
    need(native.error_row(same, same, -1, 0, scores, weights) ==
         literal_row(same, same, -1, 0, scores, weights), 'safe aliased error row')
    need(same == snapshot, 'alias source unchanged')
    checks.append('aliased-inputs-return-fresh-outputs')

    # Prefix comparisons preserve source insertion order and every full row.
    candidate, literal = {}, {}
    candidate_scores = literal_scores = (0, 0, 0)
    prefix_count = 0
    for src, numerator, exponent in [
            ({0: 64, 1: -32}, 1, 0), ({0: 32, 2: 16}, -2, 0),
            ({1: 64, 3: -128}, 3, 1), ({2: -64, 3: 128}, 1, 2),
            ({0: big, 1: -big}, 3, 130), ({0: big, 1: -big}, -3, 130)]:
        candidate, candidate_scores = native.error_row(
            candidate, src, numerator, exponent, candidate_scores, weights)
        literal, literal_scores = literal_row(
            literal, src, numerator, exponent, literal_scores, weights)
        need((candidate, candidate_scores) == (literal, literal_scores), 'every signed prefix')
        need(native.coefficient_bytes(candidate, 64) ==
             literal_coefficient_bytes(literal, 64), 'every prefix full canonical bytes')
        prefix_count += 1
    checks.append('six-ordered-prefixes-and-complete-bytes')

    hash_rows = [({}, 1), ({0: 0}, 8), ({3: -8, 0: 16, 2: -3, 1: 0}, 8),
                 ({big: -(big + 1), 0: big, -2: -big}, 1 << 130),
                 ({1: -big, 0: big, 2: 3}, 1)]
    for row, scale in hash_rows:
        expected = literal_coefficient_bytes(row, scale)
        got = native.coefficient_bytes(row, scale)
        need(type(got) is bytes and got == expected, 'complete descending canonical bytes')
        for event, value in row.items():
            need(native.coefficient_item_bytes(event, value, scale) ==
                 literal_coefficient_bytes({event: value}, scale), 'signed one-event bytes')
    checks.append('zero-negative-large-reduced-and-ordered-formatting')
    for event, values, units in [
            (0, (0, 8, -8), (1, 8, 8)),
            (17, (-3, 12, big + 1), (8, 8, 1 << 130)),
            (-1, (-big, big, 0), (1, 1, 16))]:
        expected = (str(event) + ':' + ','.join(str(Fraction(v, u))
                    for v, u in zip(values, units)) + ';').encode()
        need(native.score_bytes(event, values, units) == expected, 'score stream bytes omit /1')
    checks.append('score-string-contract-distinct-from-coefficient-contract')

    column = {2: -64, 0: 128, 1: 0}
    table = [[2, 3, 5], [7, 11, 13], [17, 19, 23]]
    before = [list(row) for row in table]
    expected = [(i, (table[i][0] + abs(v) * 3,
                     table[i][1] + abs(v) * 7, table[i][2] + abs(v)),
                 literal_coefficient_bytes({9: v}, 64)) for i, v in column.items()]
    need(native.reverse_updates(column, table, 3, 7, 9, 64) == expected,
         'reverse scores and signed bytes in dict insertion order')
    need(table == before, 'reverse score inputs unchanged')
    shared = [2, 3, 5]
    aliased_table = [shared] * 3
    native.reverse_updates(column, aliased_table, 3, 7, 9, 64)
    need(aliased_table == [[2, 3, 5]] * 3 and shared == [2, 3, 5], 'reverse score alias safety')
    checks.append('reverse-scores-signed-bytes-and-aliases')

    class ForeignInt(int):
        def __mul__(self, other):
            raise RuntimeError('foreign arithmetic must never execute')

    class ForeignDict(dict):
        pass

    class ForeignList(list):
        pass

    reject('bool-numerator', lambda: native.add_row({}, {}, True, 0), TypeError)
    reject('foreign-int-value', lambda: native.add_row({}, {0: ForeignInt(2)}, 1, 0), TypeError)
    reject('foreign-dict', lambda: native.add_row(ForeignDict(), {}, 1, 0), TypeError)
    reject('foreign-key', lambda: native.add_row({}, {ForeignInt(0): 2}, 1, 0), TypeError)
    reject('float-value', lambda: native.add_row({}, {0: 2.0}, 1, 0), TypeError)
    reject('negative-exponent', lambda: native.add_row({}, {}, 1, -1), ValueError)
    reject('bool-exponent', lambda: native.add_row({}, {}, 1, True), TypeError)
    failed_dst, failed_src = {0: 9}, {0: 4, 1: 3}
    reject('inexact-division-transaction', lambda: native.add_row(failed_dst, failed_src, 1, 1), ValueError)
    need(failed_dst == {0: 9} and failed_src == {0: 4, 1: 3}, 'failure leaves inputs unchanged')
    reject('inexact-scaled-row', lambda: native.scale_row({0: -3}, 1, 1), ValueError)
    reject('nondyadic-scale', lambda: native.coefficient_bytes({0: 1}, 3), ValueError)
    reject('zero-scale', lambda: native.coefficient_bytes({}, 0), ValueError)
    reject('negative-scale', lambda: native.coefficient_bytes({}, -8), ValueError)
    reject('bool-scale', lambda: native.coefficient_bytes({}, True), TypeError)
    reject('short-score', lambda: native.error_row({}, {}, 1, 0, (0, 0), weights), ValueError)
    reject('foreign-scores', lambda: native.error_row({}, {}, 1, 0, ForeignList([0, 0, 0]), weights), TypeError)
    reject('foreign-weight', lambda: native.error_row({}, {0: 1}, 1, 0, scores, [(1, True)]), TypeError)
    reject('weight-index-range', lambda: native.error_row({}, {4: 1}, 1, 0, scores, weights), IndexError)
    reject('negative-weight-index', lambda: native.error_row({}, {-1: 1}, 1, 0, scores, weights), IndexError)
    reject('reverse-index-range', lambda: native.reverse_updates({3: 1}, table, 1, 1, 0, 1), IndexError)
    reject('score-nondyadic-unit', lambda: native.score_bytes(0, (0, 0, 0), (1, 1, 3)), ValueError)
    reject('event-type', lambda: native.coefficient_item_bytes(True, 1, 1), TypeError)
    return dict(status='PASS_FINITE_INTEGER_FORMAT', checks=checks,
                row_cases=len(cases), ordered_prefixes=prefix_count,
                independent_fraction_formatting=True, whole_replay=False,
                timing_claim=False)


if __name__ == '__main__':
    import argparse
    import json
    import native_loader
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    result = run(native_loader.load(args.source_sha256))
    print(json.dumps(dict(result=result, build=native_loader.receipt()), sort_keys=True))
