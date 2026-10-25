"""Separate literal-word cost and acquisition checks; no source executable imports.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
This module receives already authenticated source data from the orchestrator.
Counts are logical event counts and scalar allowances, never physical tariffs.
"""
from collections import Counter
from fractions import Fraction


def require(ok, message):
    if not ok:
        raise ValueError(message)


def invoice(word):
    """Recount the entire literal word, rejecting unsupported ADD tariffs."""
    count = Counter()
    active = None
    private_peak = 0
    for index, event in enumerate(word):
        require(type(event) is list and event, 'event structure')
        op = event[0]
        require(op in ('clear', 'add', 'line', 'map', 'begin', 'end', 'checkpoint'),
                'unpriced operation at ' + str(index))
        count[op] += 1
        if op == 'add':
            require(len(event) == 4 and type(event[3]) is str, 'ADD exact coefficient text')
            require(event[1] != event[2], 'ADD source/destination alias')
            coefficient = abs(Fraction(event[3]))
            require(coefficient in (1, Fraction(1, 4)), 'unsupported ADD coefficient')
            count['unit_ADD' if coefficient == 1 else 'quarter_ADD'] += 1
        elif op == 'begin':
            require(active is None and type(event[2]) is int and event[2] in (8, 16),
                    'private begin contract')
            active = (event[1], event[2])
            private_peak = max(private_peak, event[2])
        elif op == 'end':
            require(active == (event[1], event[2]), 'private end contract')
            active = None
        elif op in ('line', 'map'):
            require(active is None, 'native/map inside active private body')
    require(active is None, 'unterminated private body')
    return {
        'word_events': len(word),
        'H1_children': count['line'],
        'native_wrappers': 2 * count['line'],
        'cover_maps': count['map'],
        'unit_ADD': count['unit_ADD'],
        'quarter_ADD': count['quarter_ADD'],
        'CLEAR': count['clear'],
        'scalar_allowance': 8 * count['unit_ADD'] + 12 * count['quarter_ADD'] + 2 * count['clear'],
        'private_peak': private_peak,
    }


def acquisition(source_word, U, T, A):
    """Locate Q1's actual lifetime and the real 104-source recovery cut."""
    begin = source_word.index(['begin', 'B1_current_query', 8])
    end = source_word.index(['end', 'B1_current_query', 8])
    future = next(i for i, e in enumerate(source_word)
                  if e[0] == 'map' and e[2] == 2)
    source_rows = []
    for k in range(8):
        role = 'F' + str(k)
        writes = [(i, e) for i, e in enumerate(source_word[begin:end], begin)
                  if e[0] in ('clear', 'add') and e[1] == role]
        require(writes[0][1] == ['clear', role, 'wide'], 'Q1 initialization')
        require(writes[-1][1] == ['clear', role, 'identity'], 'Q1 retirement')
        require(all(e[0] == 'add' and e[2].startswith('W')
                    for _, e in writes[1:-1]), 'Q1 source form')
        uses = [i for i in range(writes[-2][0] + 1, writes[-1][0])
                if source_word[i][0] == 'add' and source_word[i][2] == role]
        require(uses and writes[-1][0] < end < future, 'Q1 lifetime precedes future cut')
        source_rows.append({'role': role, 'initialization': writes[0][0],
                            'last_accumulation': writes[-2][0], 'last_read': max(uses),
                            'retirement': writes[-1][0], 'frame': 'F17',
                            'private_at_future_cut': False})
    require(len(U) == 96 and len(T) == len(A) == 8 and len(set(U + T + A)) == 112,
            'source partition')
    hosted = []
    for port in U[:8]:
        name = 'Z' + str(port)
        refs = [(i, e) for i, e in enumerate(source_word[:future]) if name in e[1:3]]
        expected = [['clear', name, 'current'], ['add', name, 'X' + str(port), '1']]
        require([e for _, e in refs] == expected, 'deferred Q1 hosting def-use')
        hosted.append({'output': name, 'defer_definition_events': [i for i, _ in refs]})
    return {'source_current_query_begin': begin, 'source_current_query_end': end,
            'source_first_future_map': future, 'query_lifetimes': source_rows,
            'query_not_available_at_future_cut': True,
            'conservative_copy_acquisition': {'unit_ADD': 8, 'CLEAR': 8,
                                             'scalar_allowance': 80,
                                             'later_cleanup_or_output_restoration': 'additional obligation'},
            'potential_owned_query_hosting': hosted,
            'hosting_status': 'def-use eligibility only; not implemented by selected scalar-factorization candidate',
            'selected_candidate_acquisition': 'uses the actual 104 corrected W fields; no Q1 retention or reacquisition',
            'full_residual_preservation': 'Actual W includes both Q2(X_T) and -M21 Q1(Y). All 104 source ports must occur.',
            'frame_scope': 'F17 is inherited from the authenticated canonical frame replay; not a modulus.'}


def compare(candidate, baseline3985, baseline4015):
    bills = {'PR3985': invoice(baseline3985), 'PR4015': invoice(baseline4015),
             'candidate': invoice(candidate)}
    require(bills['PR3985']['scalar_allowance'] == 27184, '3985 scalar baseline')
    require(bills['PR4015']['scalar_allowance'] == 26944, '4015 scalar baseline')
    for name in ('PR3985', 'PR4015'):
        require(bills[name]['H1_children'] == 224 and bills[name]['cover_maps'] == 352,
                'source native/map baseline')
    return {'complete_literal_invoices': bills,
            'delta_against_PR4015': {k: bills['candidate'][k] - bills['PR4015'][k]
                                    for k in bills['candidate']},
            'count_type': 'exact logical event counts; scalar allowance is an inherited constructive upper allowance',
            'provenance': 'new independent event recount, inherited scalar tariff 8/12/2',
            'unknown': ['physical routing/movement/control', 'decoder numerical precision and range',
                        'actual native workspace exclusivity', 'supplier invocation/coverage and idle credits',
                        'weighted recursive cost and both supplier caps'],
            'kappa_change': 'not established'}


def preservation(source, candidate, host_ports):
    """Check exact preserved prefix/suffix and paid delayed output definitions."""
    start = next(i for i, e in enumerate(source) if e[0] == 'map' and e[2] == 2)
    stop = max(i for i, e in enumerate(source) if e[0] == 'map' and e[2] == 2) + 1
    require(len(host_ports) == len(set(host_ports)), 'distinct output hosts')
    removed = set()
    definitions = []
    records = []
    for port in host_ports:
        name = 'Z' + str(port)
        occurrences = [i for i, e in enumerate(source[:stop]) if name in e[1:3]]
        definition = [['clear', name, 'current'], ['add', name, 'X' + str(port), '1']]
        require([source[i] for i in occurrences] == definition and max(occurrences) < start,
                'host output has live prefix use')
        removed.update(occurrences)
        definitions.extend(definition)
        records.append({'host': name, 'deferred_source_events': occurrences})
    prefix = [e for i, e in enumerate(source[:start]) if i not in removed]
    suffix = source[stop:]
    require(candidate[:len(prefix)] == prefix, 'literal prefix changed beyond deferred output definitions')
    require(candidate[-len(suffix):] == suffix, 'literal preserved suffix changed')
    restore_start = len(candidate) - len(suffix) - len(definitions)
    require(candidate[restore_start:restore_start + len(definitions)] == definitions,
            'paid deferred output restoration before suffix')
    return {'source_replacement_interval': [start, stop],
            'preserved_prefix_events_after_deferral': len(prefix),
            'preserved_suffix_events': len(suffix),
            'paid_output_restoration_interval': [restore_start, restore_start + len(definitions)],
            'host_definitions': records,
            'prefix_value_contract': 'All source Q1 computation, its retirement, all U/T writes and all stage1 return maps retained literally.',
            'suffix_value_contract': 'Checkpoint, F0 inversion, every output finalization retained literally.'}


def pair_identity(R, pairs, expected_ports):
    """Independent two-symbol check of every emitted pair's planned scalar circuit.

    This verifies the sharing identity, not the lowering's frames or source copies.
    Those are separate complete-word replay obligations.
    """
    flat = [p for pair in pairs for p in pair]
    require(len(flat) == len(set(flat)) and set(flat) == set(expected_ports),
            'pair partition includes every actual U and T source exactly once')
    histogram = Counter()
    savings = 0
    for p, q in pairs:
        r = [Fraction(R[k][p]) for k in range(8)]
        s = [Fraction(R[k][q]) for k in range(8)]
        require(all(x in (-1, 0, 1) for x in r + s), 'source coefficient alphabet')
        require([i for i in range(8) if r[i]] == [i for i in range(8) if s[i]], 'common pair support')
        require(sum(bool(x) for x in r) == 4, 'four-source support')
        agree = [i for i in range(8) if r[i] and r[i] == s[i]]
        disagree = [i for i in range(8) if r[i] and r[i] != s[i]]
        require(len(agree) >= 2, 'pair fails strict ADD saving')
        # Before D changes: deposit both original symbols into differing channels.
        out = [[Fraction(0), Fraction(0)] for _ in range(8)]
        for i in disagree:
            out[i][0] += r[i]
            out[i][1] += s[i]
        # One legal unit ADD forms D+E; shared channels each read this same value.
        for i in agree:
            out[i][0] += r[i]
            out[i][1] += r[i]
        require(out == [[r[i], s[i]] for i in range(8)], 'complete two-source identity')
        after = 2 * len(disagree) + 1 + len(agree)
        require(after < 8, 'positive pair saving')
        histogram[len(agree)] += 1
        savings += 8 - after
    return {'pairs': len(pairs), 'agreements_histogram': dict(sorted(histogram.items())),
            'query_unit_ADD_before': 4 * len(expected_ports),
            'query_unit_ADD_after': 4 * len(expected_ports) - savings,
            'query_unit_ADD_saving': savings,
            'full_scalar_allowance_saving_if_other_counts_equal': 8 * savings,
            'proof': 'Two independent symbols per pair; all 104 ports appear exactly once; differing-channel reads precede destructive D+=E.'}


def selected_acquisition(source, candidate, U, T, host_ports):
    """Audit the emitted acquisition events, independently of pair planning.

    Full logical values and phase frames remain the central replay's job.
    This checks that every source is the real corrected owned W and that
    its CLEAR/copy/map/native normalization has survived the lowering.
    """
    retained = preservation(source, candidate, host_ports)
    start = retained['preserved_prefix_events_after_deferral']
    stop = retained['paid_output_restoration_interval'][0]
    block = candidate[start:stop]
    owned_hosts = {'Z' + str(p) for p in host_ports}
    require(len(owned_hosts) == 10 and set(host_ports).issubset(U), 'ten U-owned hosts')
    query_initializations = block[:8]
    require(len(query_initializations) == 8 and
            all(e[0] == 'clear' and e[1] in owned_hosts and e[2] == 'query2'
                for e in query_initializations) and
            len({e[1] for e in query_initializations}) == 8, 'eight paid query initializations')
    acquired = []
    for i, e in enumerate(block):
        if e[0] != 'add' or not e[2].startswith('W'):
            continue
        port = int(e[2][1:])
        require(e[1] in owned_hosts and e[3] == '1', 'actual W copy into owned host')
        require(i >= 1 and i + 2 < len(block), 'complete source normalization')
        require(block[i-1] == ['clear', e[1], 'current'], 'source acquisition CLEAR')
        require(block[i+1] == ['map', e[1], 2, port, False], 'stage2 source map')
        require(block[i+2] == ['line', e[1], port, -1], 'source negative line')
        acquired.append(port)
    require(len(acquired) == len(set(acquired)) == 104 and set(acquired) == set(U + T),
            'all 104 corrected W values acquired once, including all T')
    require(not any(e[0] == 'add' and e[2].startswith(('X', 'Y', 'F', 'G')) for e in block),
            'no free borrowed-Y bypass or retired private-query input')
    require(not any(e[0] in ('clear', 'add', 'line', 'map') and e[1].startswith(('X', 'Y'))
                    for e in candidate), 'borrowed current values are read-only')
    require(not any(e[0] in ('begin', 'end') for e in block), 'future query uses no private scope')
    nonhost_writes = [e for e in block if e[0] in ('clear', 'add', 'line', 'map') and e[1] not in owned_hosts]
    require(len(nonhost_writes) == 8 and all(e[0] == 'add' and e[1].startswith('W')
                and e[2] in owned_hosts and e[3] == '1' for e in nonhost_writes),
            'only eight owned response deposits occur outside ten hosts')
    return {'window': [start, stop], 'acquired_source_ports': sorted(acquired),
            'U_sources': len(set(acquired).intersection(U)),
            'T_sources': len(set(acquired).intersection(T)),
            'source_acquisition_unit_ADD': 104, 'source_acquisition_CLEAR': 104,
            'source_normalization_maps': 104, 'source_normalization_H1': 104,
            'source_acquisition_scalar_allowance': 104 * (8 + 2),
            'query_initialization_CLEAR': 8, 'query_initialization_scalar_allowance': 16,
            'owned_output_hosts': sorted(owned_hosts), 'extra_owned_banks': 0,
            'future_private_peak': 0, 'owned_output_banks_still_required': 224,
            'response_deposits': len(nonhost_writes),
            'Q1_retention_or_reacquisition': 'not used; corrected W already contains its paid prefix effect',
            'restoration': 'Ten delayed output definitions each use one CLEAR and one X copy; included in full invoice.',
            'physical_status': 'Logical def-use feasibility only; movement, native tag ABI and exclusivity are not priced here.'}


def negative_controls(source, candidate, U, T, host_ports):
    """Small adversarial acquisition/charging controls, without replay claims."""
    from copy import deepcopy
    retained = preservation(source, candidate, host_ports)
    start = retained['preserved_prefix_events_after_deferral']
    stop = retained['paid_output_restoration_interval'][0]
    first_copy = next(i for i in range(start, stop)
                      if candidate[i][0] == 'add' and candidate[i][2].startswith('W'))
    t_copy = next(i for i in range(start, stop)
                 if candidate[i][0] == 'add' and candidate[i][2] == 'W' + str(T[0]))
    cases = {}
    trial = deepcopy(candidate); trial[first_copy][2] = 'Y' + trial[first_copy][2][1:]
    cases['borrowed_Y_substitution'] = trial
    trial = deepcopy(candidate); del trial[t_copy]
    cases['omitted_T_source'] = trial
    trial = deepcopy(candidate); del trial[first_copy - 1]
    cases['uninitialized_source_host'] = trial
    trial = deepcopy(candidate); trial[first_copy + 1][-1] = True
    cases['wrong_source_map_direction'] = trial
    trial = deepcopy(candidate); del trial[start]
    cases['free_query_initialization'] = trial
    trial = deepcopy(candidate); del trial[stop]
    cases['omitted_output_restoration_CLEAR'] = trial
    checked = {}
    for name, trial in cases.items():
        try:
            selected_acquisition(source, trial, U, T, host_ports)
        except ValueError as exc:
            checked[name] = str(exc)
        else:
            raise ValueError('acquisition control unexpectedly passed: ' + name)
    try:
        invoice([['add', 'Z0', 'W0', '1/2']])
    except ValueError as exc:
        checked['unsupported_scalar_tariff'] = str(exc)
    else:
        raise ValueError('unpriced half ADD passed')
    try:
        invoice([['begin', 'F', 8], ['line', 'Z0', 1, -1], ['end', 'F', 8]])
    except ValueError as exc:
        checked['native_inside_private_scope'] = str(exc)
    else:
        raise ValueError('native/private overlap passed')
    return checked
