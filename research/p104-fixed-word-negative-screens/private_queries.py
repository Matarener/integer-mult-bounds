"""Five private rank-four output-seam reconstructions on the pinned PR6030 word.

Prepared by Jonathan Capalbo (jon314159), with OpenAI Codex assistance.
Apache-2.0. No query is removed or priced; the source and predecessor credits
remain with PR6030, PR5827 and the retained P104 lineage.
"""
from fractions import Fraction as Q
from endpoints import (advance, binary_span, encode, finish, initial_state,
                       need, span_solve)


CASES = {12805: (798, 267, 1091), 13495: (773, 1031, 597),
         13510: (781, 518, 240), 13563: (782, 517, 243), 13592: (779, 477, 1090)}


def controls():
    a, b = {0: Q(1), 1: Q(1)}, {0: Q(1), 1: Q(-1)}
    positive = span_solve({0: Q(1)}, [('2', a), ('3', b)], fast=False)
    need(positive['in_span'] and positive['witness'] == {'2': '1/2', '3': '1/2'},
         'Dyadic two-donor positive')
    need(not span_solve({2: Q(1)}, [('2', a), ('3', b)], fast=False)['in_span'],
         'Independent-column negative')
    odd = span_solve({0: Q(1)}, [('3', {0: Q(3)})], fast=False)
    need(odd['in_span'] and not odd['witness_dyadic'], 'Nondyadic witness is labeled')
    target, rows, levels, receiver = {0: Q(1)}, [{0: Q(1)}, {1: Q(1)}], [0, 0], 0
    donors = [(str(r), row) for r, row in enumerate(rows) if r != receiver and levels[r] == 0]
    need(not span_solve(target, donors, fast=False)['in_span'], 'Receiver cannot supply its own value')
    need(span_solve(target, [('self', rows[receiver])], fast=False)['in_span'], 'Self-exclusion positive comparator')
    need(binary_span([1, 2]) == binary_span([3, 2]), 'Distinct presentations of the same binary subspace')
    need(binary_span([1, 2]) != binary_span([1, 4]), 'Different binary subspaces distinguished')
    return {'dyadic_two_donor_positive': True, 'independent_column_negative': True,
            'nondyadic_witness_labeled': True, 'receiver_excluded': True,
            'duplicate_frame_presentations_recognized': True, 'different_frame_spans_distinguished': True}


def run(word):
    """Return deterministic exact output-seam evidence; no I/O or source mutation."""
    control_results = controls()
    public = word['public']
    frames = [binary_span(basis) for basis in word['frames']]
    rows, levels = initial_state(word)
    results, peak_live = [], 0
    for i, event in enumerate(word['program']):
        advance(rows, levels, event, public)
        peak_live = max(peak_live, sum(frame is not None for frame in levels[public:]))
        if i not in CASES:
            continue
        r, a, b = CASES[i]
        need(event == ['MOVE', r, a, b, True] and r >= public, 'Nominated private output seam')
        need(frames[b] < frames[a] and len(word['frames'][a]) - len(word['frames'][b]) == 4,
             'Nominated nested private rank-four transport')
        exact = [s for s, frame in enumerate(levels) if s != r and frame == b]
        relaxed = [s for s, frame in enumerate(levels)
                   if s != r and frame is not None and frames[frame] == frames[b]]
        exact_result = span_solve(rows[r], [(str(s), rows[s]) for s in exact], fast=False)
        relaxed_result = span_solve(rows[r], [(str(s), rows[s]) for s in relaxed], fast=False)
        results.append({'after_event_zero_based': i, 'role': r, 'source_frame': a, 'destination_frame': b,
                        'target_row': encode(rows[r]), 'target_nonzero': bool(rows[r]),
                        'exact_frame_donors': exact, 'exact_frame_result': exact_result,
                        'same_span_donors': relaxed, 'same_span_result': relaxed_result,
                        'donor_rows': {str(s): encode(rows[s]) for s in relaxed},
                        'donor_frames': {str(s): levels[s] for s in relaxed}})
    replay = finish(word, rows, levels)
    need(len(results) == 5 and all(item['target_nonzero'] for item in results), 'Five nonzero private query values')
    exact_candidates = sum(item['exact_frame_result']['in_span'] for item in results)
    relaxed_candidates = sum(item['same_span_result']['in_span'] for item in results)
    need(exact_candidates == relaxed_candidates == 0, 'Five exact negative private-query reconstructions')
    return {'status': 'PASS_FIVE_PRIVATE_QUERY_OUTPUT_RECONSTRUCTION_SCREEN',
            'replay': replay, 'peak_live_owned': peak_live, 'cases': results,
            'exact_frame_candidates': exact_candidates, 'same_span_relaxed_candidates': relaxed_candidates,
            'controls': control_results,
            'scope': 'Only the five nominated immediate output seams. All other live same-chart rows are '
                     'available, with the receiver excluded. A further relaxation identifies duplicate '
                     'binary-subspace presentations for free. No changed continuation, new lifetime, '
                     'different native monomial, query deletion, paid improvement or global optimum is claimed.'}
