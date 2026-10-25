"""Independent Fraction row/column audit of the published finite scalar word.

No parent checker, dyadic arithmetic implementation, compiler or norm helper is
imported. COPY is the literal ADD chosen for the error interface.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
WORD_SHA = '48f8734ca9c5adf5d60ded3a5fefbc24894d2c358ed7cb30fcc0d71718599446'
CPU_LIMIT = 60

def require(test, message):
    if not test:
        raise AssertionError(message)

def serial(row):
    return {str(k): str(v) for k, v in sorted(row.items())}

def add_scaled(destination, source, coefficient):
    answer = destination.copy()
    for key, value in source.items():
        result = answer.get(key, Fraction(0)) + coefficient * value
        if result:
            answer[key] = result
        elif key in answer:
            del answer[key]
    return answer

def denominator_exponent(row):
    exponents = []
    for value in row.values():
        d = value.denominator
        require(d > 0 and d & (d - 1) == 0, 'Dyadic literal arithmetic')
        exponents.append(d.bit_length() - 1)
    return max(exponents, default=0)

def calculate():
    start = time.process_time()
    def deadline():
        require(time.process_time() - start < CPU_LIMIT, 'Incomplete: 60 CPU second cap')

    raw = (HERE / 'inputs/WORD.json.gz').read_bytes()
    require(sha256(raw).hexdigest() == WORD_SHA, 'Exact published word pin')
    word = json.loads(gzip.decompress(raw))
    events = word['program']
    require(word['public'] == 735 and len(events) == 25310, 'Fixed finite input ABI')
    public, roles = 735, 743
    coefficients = {k: Fraction(event[-2]) for k, event in enumerate(events)
                    if event[0] in ('ADD', 'COPY', 'SCALE')}
    one = Fraction(1)

    # P_t is represented by its rows over all arbitrary public originals.
    state = [{i: one} for i in range(public)] + [{} for _ in range(8)]
    chart = list(word['initial']) + [None] * 8
    owned = set()
    max_prefix = one
    prefix_witness = {'cut': 0, 'role': 0, 'l1': '1', 'row': {'0': '1'}}
    prefix_den = 0
    prefix_den_witness = None
    counts = Counter()
    copies = []
    for index, event in enumerate(events):
        if index % 64 == 0:
            deadline()
        opcode, target = event[:2]
        counts[opcode] += 1
        changed = True
        if opcode == 'MOVE':
            require(chart[target] == event[2], 'MOVE entry chart')
            chart[target] = event[3]
            changed = False
        elif opcode == 'INIT':
            require(target >= public and target not in owned, 'Owned initialization')
            owned.add(target)
            state[target] = {}
            chart[target] = event[2]
        elif opcode == 'CLEAR':
            require(target in owned and chart[target] == event[2], 'Owned clear')
            owned.remove(target)
            state[target] = {}
            chart[target] = None
        elif opcode == 'SCALE':
            require(chart[target] == event[-1], 'SCALE chart')
            state[target] = {i: coefficients[index] * v for i, v in state[target].items()
                             if coefficients[index] * v}
        else:
            require(opcode in ('ADD', 'COPY'), 'Known scalar opcode')
            source = event[2]
            require(source != target and chart[source] == chart[target] == event[-1],
                    'Actual common scalar chart')
            if opcode == 'COPY':
                require(target in owned and not state[target], 'COPY exact zero on ideal trace')
                copies.append((index, target))
            state[target] = add_scaled(state[target], state[source], coefficients[index])
        if changed:
            row = state[target]
            row_norm = sum((abs(value) for value in row.values()), Fraction(0))
            if row_norm > max_prefix:
                max_prefix = row_norm
                prefix_witness = {'cut': index + 1, 'role': target,
                                  'l1': str(row_norm), 'row': serial(row)}
            exp = denominator_exponent(row)
            if exp > prefix_den:
                prefix_den, prefix_den_witness = exp, [index + 1, target, exp]
    live = set(word['live'])
    require(not owned and chart[:public] == word['final'], 'Complete owned lifecycle and exits')
    for i, row in enumerate(state):
        expected = {i: one} if i < public else {}
        if i - 112 in live:
            expected[i - 112] = one
        require(row == expected, 'All 743 forward endpoint rows: ' + str(i))

    # S_t is represented by columns over public endpoints. The l-infinity
    # matrix norm is the maximum absolute ROW sum; maintain those sums while
    # a single column changes. The final owned outputs are discarded/reset.
    response = [{i: one} for i in range(public)] + [{} for _ in range(8)]
    absolute_sums = [one for _ in range(public)]
    max_suffix = one
    suffix_witness = {'cut': len(events), 'output': 0, 'l1': '1', 'row': {'0': '1'}}
    suffix_den = 0
    suffix_den_witness = None
    copy_residuals = []

    def replace_column(which, new, cut):
        nonlocal max_suffix, suffix_witness, suffix_den, suffix_den_witness
        old = response[which]
        response[which] = new
        for output in old.keys() | new.keys():
            absolute_sums[output] += abs(new.get(output, Fraction(0))) - abs(old.get(output, Fraction(0)))
            if absolute_sums[output] > max_suffix:
                max_suffix = absolute_sums[output]
                row = {j: col[output] for j, col in enumerate(response) if output in col}
                require(sum(map(abs, row.values())) == max_suffix, 'Suffix row-sum invariant')
                suffix_witness = {'cut': cut, 'output': output,
                                  'l1': str(max_suffix), 'row': serial(row)}
        exp = denominator_exponent(new)
        if exp > suffix_den:
            suffix_den, suffix_den_witness = exp, [cut, which, exp]

    for index in range(len(events) - 1, -1, -1):
        if index % 64 == 0:
            deadline()
        event = events[index]
        opcode, target = event[:2]
        if opcode == 'MOVE':
            continue
        if opcode in ('INIT', 'CLEAR'):
            replace_column(target, {}, index)
        elif opcode == 'SCALE':
            replace_column(target, {i: coefficients[index] * v for i, v in response[target].items()
                                    if coefficients[index] * v}, index)
        else:
            source = event[2]
            if opcode == 'COPY':
                # COPY is ADD, so an injected error already in target survives.
                require(response[target], 'Nonzero actual owned COPY residual')
                copy_residuals.append({'event': index, 'owned': target,
                                       'entire_public_response': serial(response[target])})
            replace_column(source, add_scaled(response[source], response[target], coefficients[index]), index)
            # Deliberately do not zero the target column as assignment would.
    for i, column in enumerate(response):
        expected = {i: one} if i < public else {}
        if i in live:
            expected[i + 112] = one
        require(column == expected, 'All 743 backward endpoint columns: ' + str(i))
    require(len(copies) == len(copy_residuals) == 8, 'Eight literal ADD-COPY sites')
    deadline()

    claim_raw = (HERE / 'inputs/CLAIM.json').read_bytes()
    claim = json.loads(claim_raw)
    checked = {
        'prefix_max_row_l1': str(max_prefix),
        'prefix_max_witness': prefix_witness,
        'prefix_max_entry_denominator_exponent': prefix_den,
        'prefix_denominator_witness': prefix_den_witness,
        'suffix_max_row_l1': str(max_suffix),
        'suffix_max_witness': suffix_witness,
        'suffix_max_entry_denominator_exponent': suffix_den,
        'suffix_denominator_witness': suffix_den_witness,
    }
    for key, actual in checked.items():
        require(actual == claim[key], 'Independent agreement with parent claim: ' + key)
    return {
        'status': 'PASS_INDEPENDENT_FRACTION_ALL_CUT_NORMS',
        'word_sha256': WORD_SHA,
        'compared_parent_claim_sha256': sha256(claim_raw).hexdigest(),
        'cuts_checked_in_each_direction': len(events) + 1,
        'public_arbitrary_inputs': public,
        'state_roles': roles,
        'op_counts': dict(sorted(counts.items())),
        'forward_endpoint_rows_checked': len(state),
        'backward_endpoint_columns_checked': len(response),
        'COPY_semantics': 'ADD into freshly initialized exact zero; residual target column retained',
        'COPY_residual_controls': list(reversed(copy_residuals)),
        **checked,
        'scope': 'Exact logical scalar all-cut infinity norms and denominator exponents only. No chart-diagram norm proof, child precision, tape admission, complete caller closure, new kappa or human review is established.',
    }, time.process_time() - start

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result, cpu = calculate()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        (HERE / 'ENVIRONMENT.json').write_text(json.dumps({'author_cpu_seconds': cpu, 'cpu_cap_seconds': CPU_LIMIT}, sort_keys=True, indent=2) + '\n')
    else:
        require(json.loads(path.read_bytes()) == result, 'Frozen independent receipt')
    print(json.dumps({k: result[k] for k in ('status', 'cuts_checked_in_each_direction', 'prefix_max_row_l1', 'suffix_max_row_l1', 'prefix_max_entry_denominator_exponent', 'suffix_max_entry_denominator_exponent')}, sort_keys=True))
    print(json.dumps({'cpu_seconds': round(cpu, 6)}, sort_keys=True))

if __name__ == '__main__':
    main()
