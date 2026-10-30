#!/usr/bin/env python3
"""Independent separator discovery and composed-caller regression controls.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Counterexample and requested repair credited to Mister-Meeseeks's PR2477 review.
"""
import compare_logs as C


def exercise(left, right, left_context, right_context, left_outer, right_outer):
    # Derive the dangerous alphabet from Python's parser, independently of the guard.
    separators = [chr(cp) for cp in range(0x110000)
                  if ('A' + chr(cp) + 'B').splitlines() == ['A', 'B']
                  and chr(cp) not in '\r\n']
    C.require(len(separators) == 8, 'splitlines separator alphabet changed')
    raw = C.canonical_log(right_outer)
    boundaries = [i for i, byte in enumerate(raw) if byte == 10]
    C.require(len(boundaries) == 13, 'fixture must have thirteen LF boundaries')
    adapted, portable_context = C.roles.adapt(right, right_context)
    C.closed.prepare(adapted, portable_context)
    historical, rejected = [], []
    for char in separators:
        label = 'U+' + format(ord(char), '04X')
        replacement = char.encode('utf-8')
        # First-LF counterexamples pass the actual unchanged predecessor, before
        # this caller's guard. All files and same-side timing receipts are real.
        bad = raw.replace(b'\n', replacement, 1)
        C.require(C.closed.outer_log(bad, adapted) == C.closed.outer_log(raw, adapted),
                  'historical parser counterexample no longer reproduces: ' + label)
        historical.append(label)
        for i, offset in enumerate(boundaries):
            changed = raw[:offset] + replacement + raw[offset + 1:]
            try:
                C.canonical_outer_log(changed)
            except ValueError as exc:
                C.require(str(exc) == 'non-LF/CRLF separator in outer log', 'unexpected guard rejection')
            else:
                raise ValueError('foreign separator accepted: ' + label)
            rejected.append(label + ':boundary:' + str(i))
        for side in ('reference', 'candidate', 'both'):
            lraw = C.canonical_log(left_outer)
            rraw = raw
            if side in ('reference', 'both'):
                lraw = lraw.replace(b'\n', replacement, 1)
            if side in ('candidate', 'both'):
                rraw = rraw.replace(b'\n', replacement, 1)
            try:
                C.compare(left, right, left_context, right_context, lraw, rraw)
            except ValueError as exc:
                C.require(str(exc) == 'non-LF/CRLF separator in outer log',
                          'full comparison rejected for wrong reason: ' + side + ':' + label)
            else:
                raise ValueError('full comparison accepted: ' + side + ':' + label)
            rejected.append(label + ':composed:' + side)
    try:
        C.canonical_outer_log(b'\xff' + raw)
    except UnicodeDecodeError:
        rejected.append('invalid-UTF8')
    else:
        raise ValueError('malformed UTF-8 accepted')

    def mixed(outer, parity):
        lines = C.canonical_log(outer).split(b'\n')
        return b''.join(line + (b'\r\n' if index % 2 == parity else b'\n')
                        for index, line in enumerate(lines[:-1]))

    C.require(C.compare(left, right, left_context, right_context,
                        mixed(left_outer, 0), mixed(right_outer, 1))['equivalent'],
              'mixed LF/CRLF within both outer logs rejected')
    return {'historical_separator_counterexamples': historical,
            'positive_cases': ['mixed-outer-boundaries-both-sides'],
            'negative_count': len(rejected), 'negative_cases': rejected,
            'guard_boundary_rejections': 104, 'composed_rejections': 24,
            'unicode_codepoints_scanned': 0x110000}
